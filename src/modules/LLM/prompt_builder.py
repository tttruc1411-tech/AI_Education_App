# Prompt builder — supports Qwen2.5 ChatML and Phi-3 chat formats

import re
import ast
from . import model_config as _mcfg

# ── Sentinel prefix for pre-built answers that skip LLM inference ──────────
DIRECT_ANSWER_PREFIX = "DIRECT:"

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
    "You are a Python tutor for kids. Be ULTRA BRIEF.\n\n"
    "WORKFLOW: Init_Camera → Get_Camera_Frame → Load Model → Run Model → Draw → Update_Dashboard (inside while True loop).\n"
    "Update_Dashboard() is the ONLY way to show camera feed.\n\n"
    "RULES:\n"
    "- MAX 2 sentences. No code blocks. No full scripts.\n"
    "- Just say WHAT to fix/add and WHERE (which line or position).\n"
    "- Use simple words for kids.\n"
    "- Example good answer: 'Add Update_Dashboard() at the end of your while loop.'"
)

FIX_SYSTEM_PROMPT_EN = (
    "You are a coding tutor for kids. Output ONLY the fix — no extra explanation.\n"
    "Use the EXACT format: Line N: [short reason] / Original: [code] / Fixed: [code].\n"
    "Never write paragraphs. Never repeat the error message."
)

FIX_SYSTEM_PROMPT_VI = (
    "Bạn là người hướng dẫn lập trình cho trẻ em. Chỉ xuất phần sửa — không giải thích thêm.\n"
    "Dùng ĐÚNG định dạng: Dòng N: [lý do ngắn] / Gốc: [code] / Sửa: [code].\n"
    "Không viết đoạn văn. Không lặp lại thông báo lỗi."
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
    user_parts.append("Answer in 1-2 sentences only. No code blocks.")
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


def _find_unclosed_bracket(editor_code: str, error_line: int):
    """Scan backwards from error_line to find an unclosed bracket/paren/brace.
    Returns (line_num, broken_line, bracket_char, fixed_line) or None.
    Python reports 'invalid syntax' on the line AFTER an unclosed bracket,
    so we scan the lines before the reported error."""
    code_lines = editor_code.splitlines()
    close_for = {'[': ']', '(': ')', '{': '}'}

    def _count_outside_strings(line, char):
        """Count occurrences of char that are NOT inside string literals."""
        count = 0
        in_single = False
        in_double = False
        i = 0
        while i < len(line):
            c = line[i]
            if c == '\\' and i + 1 < len(line):
                i += 2  # skip escaped char
                continue
            if c == "'" and not in_double:
                in_single = not in_single
            elif c == '"' and not in_single:
                in_double = not in_double
            elif c == char and not in_single and not in_double:
                count += 1
            i += 1
        return count

    # Scan from the error line backwards (up to 10 lines back)
    start = min(error_line - 1, len(code_lines) - 1)
    for i in range(start, max(start - 10, -1), -1):
        line = code_lines[i]
        for open_br, close_br in close_for.items():
            open_count = _count_outside_strings(line, open_br)
            close_count = _count_outside_strings(line, close_br)
            if open_count > close_count:
                # Found unclosed bracket on this line
                stripped = line.rstrip()
                fixed = stripped + close_br
                return (i + 1, line, close_br, fixed)
    return None


# ── Known library functions/modules that students import ───────────────────
# These are always available via `import camera`, `import ai_vision`, etc.
# We don't flag them as "undefined" since they come from drag-and-drop blocks.
_KNOWN_IMPORTS = {
    "camera", "ai_vision", "drawing", "display", "image", "logic",
    "variables", "robotics", "cv2", "time", "math", "os", "sys",
}


def check_undefined_vars(code: str):
    """Lightweight static analysis: find variables used but never assigned.
    Returns list of (line_num, var_name, usage_line_text) or empty list.
    Only catches simple cases — not a full linter, just typo detection."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []  # can't parse — let compile() handle it

    # Collect all assigned names (targets of assignments, for-loop vars, etc.)
    assigned = set()
    # Also collect imported names
    imported = set(_KNOWN_IMPORTS)

    for node in ast.walk(tree):
        # Assignment targets: x = ..., x, y = ...
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            for target in (node.targets if isinstance(node, ast.Assign) else [node.target]):
                if isinstance(target, ast.Name):
                    assigned.add(target.id)
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            assigned.add(elt.id)
        # AugAssign: x += ...
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name):
                assigned.add(node.target.id)
        # For loop: for x in ...
        elif isinstance(node, ast.For):
            if isinstance(node.target, ast.Name):
                assigned.add(node.target.id)
        # Function defs and class defs
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            assigned.add(node.name)
            for arg in node.args.args:
                assigned.add(arg.arg)
        elif isinstance(node, ast.ClassDef):
            assigned.add(node.name)
        # Imports
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported.add(alias.asname or alias.name)
        # With statement: with X as y
        elif isinstance(node, ast.With):
            for item in node.items:
                if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                    assigned.add(item.optional_vars.id)
        # Except handler: except E as e
        elif isinstance(node, ast.ExceptHandler):
            if node.name:
                assigned.add(node.name)

    # Python builtins we should never flag
    import builtins
    builtin_names = set(dir(builtins))

    # Now find Name nodes in Load context that aren't assigned or imported
    code_lines = code.splitlines()
    issues = []
    seen = set()  # avoid duplicate reports for same var

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            name = node.id
            if (name not in assigned
                    and name not in imported
                    and name not in builtin_names
                    and name not in seen):
                seen.add(name)
                ln = node.lineno
                line_text = code_lines[ln - 1] if ln <= len(code_lines) else ""
                issues.append((ln, name, line_text))

    return issues


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

    # ── Step 2b: Unclosed bracket detection ────────────────────────────
    # Python reports "invalid syntax" on the line AFTER an unclosed [ ( {.
    # The reported line is often fine — the real error is the missing bracket.
    # Python 3.10+ may also say "was never closed" or "unexpected EOF".
    if error_type and line_num and isinstance(line_num, int):
        is_generic_syntax = ("invalid syntax" in error_type.lower()
                             or "expected" in error_type.lower()
                             or "was never closed" in error_type.lower()
                             or "unexpected eof" in error_type.lower())
        if is_generic_syntax:
            bracket_info = _find_unclosed_bracket(editor_code, line_num)
            if bracket_info:
                real_line, real_broken, bracket_char, fixed_line = bracket_info
                bracket_names = {']': ('ngoặc vuông ]', 'closing bracket ]'),
                                 ')': ('ngoặc tròn )', 'closing parenthesis )'),
                                 '}': ('ngoặc nhọn }', 'closing brace }')}
                vi_name, en_name = bracket_names.get(bracket_char, (bracket_char, bracket_char))
                if lang == "vi":
                    return DIRECT_ANSWER_PREFIX + (
                        f"Dòng {real_line}: thêm {vi_name} ở cuối dòng\n"
                        f"Gốc: {real_broken.strip()}\n"
                        f"Sửa: {fixed_line}"
                    )
                else:
                    return DIRECT_ANSWER_PREFIX + (
                        f"Line {real_line}: add {en_name} at the end\n"
                        f"Original: {real_broken.strip()}\n"
                        f"Fixed: {fixed_line}"
                    )

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
                # Bypass LLM — we already know the exact fix
                if lang == "vi":
                    return DIRECT_ANSWER_PREFIX + (
                        f"Dòng {line_num}: code sau dấu ':' phải xuống dòng mới\n"
                        f"Gốc: {broken_line.strip()}\n"
                        f"Sửa: Nhấn Enter sau '{before_colon.strip()}' rồi viết '{after_colon}' ở dòng mới (thụt vào 4 dấu cách)"
                    )
                else:
                    return DIRECT_ANSWER_PREFIX + (
                        f"Line {line_num}: press Enter after the colon\n"
                        f"Original: {broken_line.strip()}\n"
                        f"Fixed: Press Enter after '{before_colon.strip()}' then write '{after_colon}' on next line (with 4 spaces)"
                    )

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

    # ── Indentation errors: bypass LLM entirely ───────────────────────
    # Python already knows the fix (strip spaces). No need for LLM.
    if is_indent_err and broken_line:
        fixed_line = broken_line.strip()
        if lang == "vi":
            desc = "xóa khoảng trắng thừa ở đầu dòng"
            return DIRECT_ANSWER_PREFIX + (
                f"Dòng {line_num}: {desc}\n"
                f"Gốc: {broken_line}\n"
                f"Sửa: {fixed_line}"
            )
        else:
            desc = "remove extra spaces at the start"
            return DIRECT_ANSWER_PREFIX + (
                f"Line {line_num}: {desc}\n"
                f"Original: {broken_line}\n"
                f"Fixed: {fixed_line}"
            )

    # ── Missing colon: bypass LLM only for clear keyword lines ──────────
    # Only trigger if the broken line starts with a known keyword and has no colon
    if broken_line and error_type:
        stripped = broken_line.strip()
        is_colon_keyword = any(stripped.startswith(kw) for kw in
                               ["while ", "while(", "if ", "if(", "else",
                                "elif ", "elif(", "for ", "for(", "def ", "try", "except "])
        has_no_colon = not stripped.endswith(":")
        is_colon_err = ("expected ':'" in error_type.lower()
                        or ("invalid syntax" in error_type.lower() and is_colon_keyword and has_no_colon))
        if is_colon_keyword and has_no_colon and is_colon_err:
            fixed_line = stripped + ":"
            if lang == "vi":
                return DIRECT_ANSWER_PREFIX + (
                    f"Dòng {line_num}: thêm dấu hai chấm ':' ở cuối dòng\n"
                    f"Gốc: {stripped}\n"
                    f"Sửa: {fixed_line}"
                )
            else:
                return DIRECT_ANSWER_PREFIX + (
                    f"Line {line_num}: add a colon ':' at the end\n"
                    f"Original: {stripped}\n"
                    f"Fixed: {fixed_line}"
                )

    if is_runtime:
        # Runtime error — concise fix only
        if lang == "vi":
            system = FIX_SYSTEM_PROMPT_VI
            user_content = (
                f"Lỗi: {error_type}\n"
                f"{'Dòng ' + str(line_num) + ': `' + broken_line.strip() + '`' if broken_line else ''}\n\n"
                f"Xuất ĐÚNG 1 dòng: nguyên nhân + cách sửa. Tối đa 15 từ."
            )
        else:
            system = FIX_SYSTEM_PROMPT_EN
            user_content = (
                f"Error: {error_type}\n"
                f"{'Line ' + str(line_num) + ': `' + broken_line.strip() + '`' if broken_line else ''}\n\n"
                f"Output EXACTLY 1 line: cause + how to fix. Max 15 words."
            )
    else:
        # Normal syntax error
        if lang == "vi":
            system = FIX_SYSTEM_PROMPT_VI
            user_content = (
                f"Lỗi: {error_type}\n"
                f"Dòng lỗi: `{broken_line.strip() if broken_line else 'Unknown'}`\n\n"
                f"Xuất ĐÚNG 3 dòng:\n"
                f"Dòng {line_num}: [hành động cần làm, ví dụ: thêm dấu hai chấm, sửa tên hàm]\n"
                f"Gốc: {broken_line.strip() if broken_line else 'Unknown'}\n"
                f"Sửa: [dòng code đã sửa]"
            )
        else:
            system = FIX_SYSTEM_PROMPT_EN
            user_content = (
                f"Error: {error_type}\n"
                f"Broken code: `{broken_line.strip() if broken_line else 'Unknown'}`\n\n"
                f"Output EXACTLY 3 lines:\n"
                f"Line {line_num}: [action to take, e.g. add a colon, fix the function name]\n"
                f"Original: {broken_line.strip() if broken_line else 'Unknown'}\n"
                f"Fixed: [corrected code line]"
            )

    return _wrap_prompt(system, user_content)


def build_explain_prompt(editor_code: str, lang: str = "en") -> str:
    sys_prompt = SYSTEM_PROMPT + _lang_instruction(lang)

    # Inject function definitions for any library functions in the code
    func_ctx = _extract_func_context(editor_code)
    ctx_block = f"\n\n{func_ctx}" if func_ctx else ""

    if lang == "vi":
        user_content = (
            f"Giải thích code này cho người mới bắt đầu. Tối đa 3 dòng, mỗi dòng mô tả 1 bước chính.{ctx_block}\n\n"
            f"```python\n{_trim_code(editor_code)}\n```"
        )
    else:
        user_content = (
            f"Explain this code for a beginner. Max 3 bullet points, one per key step. No code blocks in reply.{ctx_block}\n\n"
            f"```python\n{_trim_code(editor_code)}\n```"
        )
    return _wrap_prompt(sys_prompt, user_content)
