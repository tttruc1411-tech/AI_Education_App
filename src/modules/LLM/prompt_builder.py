# Prompt builder — supports Qwen2.5 ChatML and Phi-3 chat formats

import re
from . import model_config as _mcfg

# ── Function library context for Ask/Explain modes ─────────────────────────
# Lazy-loaded from definitions.py. Only injected into ask/explain prompts,
# never into fix prompts (to avoid confusing the translator pattern).

_FUNC_CACHE = None  # {func_name: {desc, params, returns, usage}}


def _load_func_cache():
    """Build a flat lookup of all library functions from definitions.py."""
    global _FUNC_CACHE
    if _FUNC_CACHE is not None:
        return _FUNC_CACHE
    _FUNC_CACHE = {}
    try:
        from src.modules.library.definitions import LIBRARY_FUNCTIONS
        for cat_name, cat in LIBRARY_FUNCTIONS.items():
            for func_name, fdef in cat.get("functions", {}).items():
                entry = {"category": cat_name, "desc": fdef.get("desc", "")}
                params = fdef.get("params", [])
                if params:
                    entry["params"] = ", ".join(
                        f"{p['name']} ({p.get('type','')}) — {p.get('desc','')}"
                        for p in params
                    )
                else:
                    entry["params"] = "None"
                ret = fdef.get("returns", {})
                entry["returns"] = f"{ret.get('type','')} — {ret.get('desc','')}" if ret else "None"
                entry["usage"] = fdef.get("usage", "")
                _FUNC_CACHE[func_name] = entry
    except Exception:
        pass
    return _FUNC_CACHE


def _extract_func_context(text: str, max_funcs: int = 4) -> str:
    """Find known function names in text and return their definitions as context.
    Returns empty string if no functions found. Limits to max_funcs to save tokens."""
    cache = _load_func_cache()
    if not cache:
        return ""
    found = []
    for func_name, info in cache.items():
        if func_name in text and len(found) < max_funcs:
            lines = [f"📦 {func_name} ({info['category']})"]
            lines.append(f"   What it does: {info['desc']}")
            lines.append(f"   Parameters: {info['params']}")
            lines.append(f"   Returns: {info['returns']}")
            if info.get("usage"):
                lines.append(f"   Example: {info['usage']}")
            found.append("\n".join(lines))
    if not found:
        return ""
    return "Function reference:\n" + "\n\n".join(found)

SYSTEM_PROMPT = (
    "You are a friendly Python tutor for kids in AI Code Lab.\n"
    "The app uses drag-and-drop code blocks. Here are the available functions and how they connect:\n\n"
    "WORKFLOW — A typical AI camera program follows this order:\n"
    "1. Init_Camera() → get a camera handle\n"
    "2. Get_Camera_Frame(capture_camera) → get a picture from camera\n"
    "3. Load a model: Load_ONNX_Model() or Load_Engine_Model() or Load_YuNet_Model()\n"
    "4. Run the model: Run_ONNX_Model() or Run_Engine_Model() or Run_YuNet_Model()\n"
    "5. Draw results: Draw_Detections() or Draw_Detections_MultiClass() or Draw_Engine_Detections()\n"
    "6. Update_Dashboard(camera_frame, var_name, var_value) → REQUIRED to display the camera feed and results on screen\n"
    "7. Steps 2-6 go inside a 'while True:' loop\n\n"
    "OTHER BLOCKS:\n"
    "- Image: convert_to_gray(), resize_image(), apply_blur(), detect_edges(), flip_image()\n"
    "- Robotics: DC_Run(pin, speed, time_ms), DC_Stop(pin), Get_Speed(pin), Set_Servo(pin, angle)\n"
    "- Logic: while True (loop), if/else (condition)\n\n"
    "IMPORTANT — Update_Dashboard() is the ONLY way to show the camera feed on screen. "
    "Without it, the kid will not see anything in the Live Feed panel.\n\n"
    "Rules:\n"
    "- Use simple words a 10-year-old can understand.\n"
    "- Keep answers short: 2-4 sentences max. NEVER output full scripts or code blocks.\n"
    "- When suggesting a fix, just tell the kid which function to add and where, like: "
    "'Add Update_Dashboard() at the end of your while loop.'\n"
    "- If function details are provided below, use them to give accurate parameter info."
)

FIX_SYSTEM_PROMPT_EN = (
    "You are a coding tutor for kids. Explain this Python error simply."
)

FIX_SYSTEM_PROMPT_VI = (
    "Bạn là người hướng dẫn lập trình cho trẻ em. Giải thích lỗi Python này một cách dễ hiểu."
)

# Max characters of code to include in any prompt.
# ~1500 chars ≈ 400 tokens, leaving ~600 tokens for the response within 4096 ctx.
_MAX_CODE_CHARS = 1500
# Max characters of console output
_MAX_CONSOLE_CHARS = 400


def _trim_code(code: str) -> str:
    """
    Trim code to _MAX_CODE_CHARS by keeping the LAST portion.
    Trimming from the end (most recent code) is more useful than the start.
    Also strips huge single-line data structures by truncating long lines.
    """
    lines = []
    for line in code.splitlines():
        if len(line) > 300:
            lines.append(line[:300] + "  # ... (truncated)")
        else:
            lines.append(line)
    joined = "\n".join(lines)
    if len(joined) > _MAX_CODE_CHARS:
        joined = "# ... (earlier code omitted)\n" + joined[-_MAX_CODE_CHARS:]
    return joined.strip()


def _trim_console(console: str) -> str:
    """Keep only the last _MAX_CONSOLE_CHARS of console output."""
    text = "\n".join(
        l for l in console.strip().splitlines() if l.strip()
    )
    if len(text) > _MAX_CONSOLE_CHARS:
        text = "...\n" + text[-_MAX_CONSOLE_CHARS:]
    return text.strip()


# ── Chat template wrappers ─────────────────────────────────────────────────

def _wrap_prompt(system: str, user: str) -> str:
    """Wrap system + user content in the correct chat template for the active model."""
    fmt = _mcfg.ACTIVE_MODEL.get("chat_format", "chatml")

    if fmt == "phi3":
        # Phi-3: <|system|>\n...<|end|>\n<|user|>\n...<|end|>\n<|assistant|>\n
        return (
            f"<|system|>\n{system}<|end|>\n"
            f"<|user|>\n{user}<|end|>\n"
            f"<|assistant|>\n"
        )
    elif fmt == "gemma":
        # Gemma 3: no system role — prepend system instructions to user turn
        # Format: <start_of_turn>user\n...<end_of_turn>\n<start_of_turn>model\n
        combined = f"{system}\n\n{user}" if system.strip() else user
        return (
            f"<start_of_turn>user\n{combined}<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )
    else:
        # Qwen2.5 ChatML: <|im_start|>role\n...<|im_end|>
        return (
            f"<|im_start|>system\n{system}<|im_end|>\n"
            f"<|im_start|>user\n{user}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )


# ── Language instruction appended to system prompts ────────────────────────

def _lang_instruction(lang: str) -> str:
    """Return a language instruction to append to system prompts."""
    if lang == "vi":
        return "\n\nIMPORTANT: You MUST reply entirely in Vietnamese. Dùng tiếng Việt để trả lời."
    return "\n\nIMPORTANT: You MUST reply entirely in English."


def _detect_missing_workflow(code: str, lang: str = "en") -> str:
    """Detect missing steps in the typical AI camera workflow.
    Returns a pre-built hint string, or empty if nothing obvious is missing."""
    if not code.strip():
        return ""

    has_camera = "Init_Camera" in code
    has_frame = "Get_Camera_Frame" in code
    has_model = any(m in code for m in ["Load_ONNX_Model", "Load_Engine_Model", "Load_YuNet_Model"])
    has_run = any(m in code for m in ["Run_ONNX_Model", "Run_Engine_Model", "Run_YuNet_Model"])
    has_draw = any(m in code for m in ["Draw_Detections", "Draw_Detections_MultiClass", "Draw_Engine_Detections"])
    has_dashboard = "Update_Dashboard" in code
    has_loop = "while True" in code or "while true" in code.lower()

    missing = []
    if has_frame and not has_camera:
        missing.append(("Init_Camera()", "capture_camera = Init_Camera()",
                        "Khởi tạo camera trước khi lấy hình" if lang == "vi" else "Initialize camera before getting frames"))
    if has_run and not has_model:
        missing.append(("Load model", "model = Load_ONNX_Model(model_path='...')",
                        "Tải mô hình AI trước khi chạy" if lang == "vi" else "Load the AI model before running it"))
    if has_draw and not has_dashboard:
        missing.append(("Update_Dashboard()", "Update_Dashboard(camera_frame=camera_frame, var_name='Objects', var_value=total_objects)",
                        "Cần Update_Dashboard() để hiển thị camera feed lên màn hình" if lang == "vi" else "You need Update_Dashboard() to show the camera feed on screen"))
    if has_frame and has_run and not has_draw:
        missing.append(("Draw function", "Draw_Detections_MultiClass(...) or Draw_Engine_Detections(...)",
                        "Cần hàm Draw để vẽ khung phát hiện lên hình" if lang == "vi" else "You need a Draw function to show detection boxes on the image"))
    if has_frame and not has_loop:
        missing.append(("while True:", "while True:\n    # your code here",
                        "Cần vòng lặp while True để camera chạy liên tục" if lang == "vi" else "You need a while True loop to keep the camera running"))

    if not missing:
        return ""

    if lang == "vi":
        hint = "Code của bạn đang thiếu:\n"
    else:
        hint = "Your code is missing:\n"
    for func, example, desc in missing:
        hint += f"- {func}: {desc}\n  Example: {example}\n"
    return hint


def build_prompt(user_question: str, editor_code: str = "",
                 console_output: str = "", lang: str = "en") -> str:
    system = SYSTEM_PROMPT + _lang_instruction(lang)
    user_parts = []

    # Detect missing workflow steps and pre-build the answer
    workflow_hint = _detect_missing_workflow(editor_code, lang)
    if workflow_hint:
        user_parts.append(workflow_hint)

    # Inject function definitions for any library functions mentioned
    search_text = (user_question + " " + editor_code)
    func_ctx = _extract_func_context(search_text)
    if func_ctx:
        user_parts.append(func_ctx)

    if editor_code.strip():
        user_parts.append(f"Code:\n```python\n{_trim_code(editor_code)}\n```")
    if console_output.strip():
        user_parts.append(f"Console:\n```\n{_trim_console(console_output)}\n```")
    user_parts.append(user_question.strip())
    user_content = "\n\n".join(user_parts)
    return _wrap_prompt(system, user_content)


def _extract_error_line(error_text: str, editor_code: str):
    """
    Parse the actual error line number from Python's traceback output.
    Returns (line_number, error_type, broken_line_text) or (None, None, None).
    """
    m = re.search(r'line\s+(\d+)', error_text, re.IGNORECASE)
    if not m:
        return None, None, None

    line_num = int(m.group(1))
    code_lines = editor_code.splitlines()

    broken_line = ""
    if 1 <= line_num <= len(code_lines):
        broken_line = code_lines[line_num - 1]

    error_type = ""
    for raw_line in reversed(error_text.splitlines()):
        stripped = raw_line.strip()
        if re.match(r'^[A-Z]\w*(Error|Exception|Warning)', stripped):
            error_type = stripped
            break

    return line_num, error_type, broken_line


def _strip_comments(code: str) -> str:
    """Remove comment-only lines but keep blank lines to preserve line numbers."""
    lines = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            lines.append("")  # keep as blank to preserve line count
        else:
            lines.append(line)
    return "\n".join(lines)


def _get_context_lines(editor_code: str, line_num: int, window: int = 3) -> str:
    """Get a few lines around the error line with line numbers."""
    code_lines = editor_code.splitlines()
    start = max(0, line_num - 1 - window)
    end = min(len(code_lines), line_num + window)
    context = []
    for i in range(start, end):
        marker = " >>>" if i == line_num - 1 else "    "
        context.append(f"{marker} {i+1}| {code_lines[i]}")
    return "\n".join(context)


def _numbered_code(code: str) -> str:
    """Add line numbers to code so the model doesn't have to count."""
    lines = code.splitlines()
    return "\n".join(f"{i+1}| {line}" for i, line in enumerate(lines))


def _check_syntax(code: str):
    """Use Python's compiler to check for syntax errors. Returns (line, msg) or None."""
    try:
        compile(code, "<student>", "exec")
        return None  # no syntax error
    except SyntaxError as e:
        return (e.lineno, str(e))


def build_fix_prompt(error_text: str, editor_code: str, lang: str = "en") -> str:
    """Translator Pattern: Python finds the error, LLM just explains it for kids."""

    # ── Step 1: Try to get the real error from console output ──────────
    line_num, error_type, broken_line = _extract_error_line(error_text, editor_code)

    # ── Step 2: If console had no error, use compile() to find it ──────
    if not error_type and editor_code.strip():
        syntax = _check_syntax(editor_code)
        if syntax is not None:
            line_num, error_type = syntax[0], syntax[1]
            code_lines = editor_code.splitlines()
            if line_num and 1 <= line_num <= len(code_lines):
                broken_line = code_lines[line_num - 1]

    # ── Step 3: Handle "expected indented block" or "unexpected indent" ──
    # When the previous line has code after a colon (while True:code_here),
    # Python either says "expected an indented block" or "unexpected indent"
    # on the NEXT line. The real fix is to split the previous line.
    if error_type and line_num and isinstance(line_num, int):
        code_lines = editor_code.splitlines()
        is_block_err = ("expected an indented block" in error_type.lower()
                        or "unexpected indent" in error_type.lower())
        if is_block_err and line_num >= 2 and line_num - 2 < len(code_lines):
            prev_line = code_lines[line_num - 2]
            # Check if previous line has code after a colon (e.g. "while True:x = 1")
            colon_idx = None
            for kw in ["while ", "if ", "else:", "elif ", "for ", "def ", "try:", "except "]:
                if kw in prev_line:
                    ci = prev_line.find(":")
                    if ci >= 0 and ci < len(prev_line) - 1 and prev_line[ci+1:].strip():
                        colon_idx = ci
                        break
            if colon_idx is not None:
                line_num = line_num - 1
                broken_line = prev_line
                after_colon = prev_line[colon_idx+1:].strip()
                before_colon = prev_line[:colon_idx+1]
                indent = "    "
                # Override error type — this is NOT a normal indent error
                error_type = f"Two statements on one line — '{after_colon}' should be on the next line"
                # Build the prompt directly and return — don't fall through
                if lang == "vi":
                    system = FIX_SYSTEM_PROMPT_VI
                    user_content = (
                        f"Thông báo lỗi: Hai lệnh trên cùng một dòng\n"
                        f"Dòng code bị lỗi: `{broken_line.strip()}`\n\n"
                        f"Chỉ xuất ĐÚNG 3 dòng:\n"
                        f"Dòng {line_num}: [giải thích rằng code sau dấu hai chấm phải xuống dòng mới]\n"
                        f"Gốc: {broken_line.strip()}\n"
                        f"Sửa: Nhấn Enter sau '{before_colon.strip()}' rồi viết '{after_colon}' ở dòng mới (thụt vào 4 dấu cách)"
                    )
                else:
                    system = FIX_SYSTEM_PROMPT_EN
                    user_content = (
                        f"Error message: Two statements on one line\n"
                        f"Broken code: `{broken_line.strip()}`\n\n"
                        f"Output EXACTLY 3 lines:\n"
                        f"Line {line_num}: [explain that code after the colon must go on the next line]\n"
                        f"Original: {broken_line.strip()}\n"
                        f"Fixed: Press Enter after '{before_colon.strip()}' then write '{after_colon}' on the next line (with 4 spaces)"
                    )
                return _wrap_prompt(system, user_content)

    # ── Step 4: Detect runtime errors (NameError, ImportError, etc.) ───
    # These pass compile() but fail at runtime. The console has the answer.
    is_runtime = False
    if error_type and any(rt in error_type for rt in
                          ["NameError", "ImportError", "ModuleNotFoundError",
                           "AttributeError", "TypeError", "ValueError"]):
        is_runtime = True

    # ── Step 4: Fallbacks ──────────────────────────────────────────────
    error_type = error_type or _trim_console(error_text) or "Unknown error"
    broken_line = broken_line.rstrip() if broken_line else ""
    line_num = line_num or "?"

    is_indent_err = "indent" in error_type.lower()

    # ── Step 5: Build the micro-prompt ─────────────────────────────────
    if is_runtime:
        # Runtime error — just ask the model to explain and suggest a fix
        if lang == "vi":
            system = FIX_SYSTEM_PROMPT_VI
            user_content = (
                f"Thông báo lỗi: {error_type}\n"
                f"{'Dòng ' + str(line_num) + ': `' + broken_line.strip() + '`' if broken_line else ''}\n\n"
                f"Giải thích lỗi này bằng 1-2 câu đơn giản cho trẻ em và nói cách sửa."
            )
        else:
            system = FIX_SYSTEM_PROMPT_EN
            user_content = (
                f"Error message: {error_type}\n"
                f"{'Line ' + str(line_num) + ': `' + broken_line.strip() + '`' if broken_line else ''}\n\n"
                f"Explain this error in 1-2 simple sentences for kids and tell them how to fix it."
            )
    elif is_indent_err:
        if lang == "vi":
            system = FIX_SYSTEM_PROMPT_VI
            user_content = (
                f"Thông báo lỗi: {error_type}\n"
                f"Dòng code bị lỗi (chú ý dấu cách ở đầu): `{broken_line}`\n\n"
                f"Chỉ xuất ĐÚNG 3 dòng theo định dạng sau:\n"
                f"Dòng {line_num}: [giải thích lỗi thụt lề bằng từ ngữ đơn giản]\n"
                f"Gốc: {broken_line}\n"
                f"Sửa: {broken_line.strip()}"
            )
        else:
            system = FIX_SYSTEM_PROMPT_EN
            user_content = (
                f"Error message: {error_type}\n"
                f"Broken code (notice the extra spaces at the start): `{broken_line}`\n\n"
                f"Output EXACTLY 3 lines in this format:\n"
                f"Line {line_num}: [explain the indentation error in simple words]\n"
                f"Original: {broken_line}\n"
                f"Fixed: {broken_line.strip()}"
            )
    else:
        # Normal syntax error
        if lang == "vi":
            system = FIX_SYSTEM_PROMPT_VI
            user_content = (
                f"Thông báo lỗi: {error_type}\n"
                f"Dòng code bị lỗi: `{broken_line.strip() if broken_line else 'Unknown'}`\n\n"
                f"Chỉ xuất ĐÚNG 3 dòng theo định dạng sau:\n"
                f"Dòng {line_num}: [giải thích lỗi bằng từ ngữ đơn giản cho trẻ em]\n"
                f"Gốc: {broken_line.strip() if broken_line else 'Unknown'}\n"
                f"Sửa: [viết lại dòng code cho đúng]"
            )
        else:
            system = FIX_SYSTEM_PROMPT_EN
            user_content = (
                f"Error message: {error_type}\n"
                f"Broken code: `{broken_line.strip() if broken_line else 'Unknown'}`\n\n"
                f"Output EXACTLY 3 lines in this format:\n"
                f"Line {line_num}: [explain the error in simple words for kids]\n"
                f"Original: {broken_line.strip() if broken_line else 'Unknown'}\n"
                f"Fixed: [write the corrected code line]"
            )

    return _wrap_prompt(system, user_content)


def build_explain_prompt(editor_code: str, lang: str = "en") -> str:
    system = SYSTEM_PROMPT + _lang_instruction(lang)

    # Inject function definitions for any library functions in the code
    func_ctx = _extract_func_context(editor_code)
    ctx_block = f"\n\n{func_ctx}" if func_ctx else ""

    user_content = (
        f"Explain this code simply for a beginner:{ctx_block}\n\n"
        f"```python\n{_trim_code(editor_code)}\n```"
    )
    return _wrap_prompt(system, user_content)
