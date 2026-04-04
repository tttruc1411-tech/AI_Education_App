from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QTimer
from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout, QGraphicsDropShadowEffect
from .library.definitions import LIBRARY_FUNCTIONS
import re

class AdvancedPythonEditor(QsciScintilla):
    # Signal to notify when a function is dropped
    functionDropped = pyqtSignal(str, tuple) # (function_id, (line, col))

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        
        # Drag-and-drop state for Ghost Blocks
        self._drag_active = False
        self._target_line = -1
        self._target_col = -1
        
        # 1. Setup Python Lexer with beautiful fonts
        self.lexer = QsciLexerPython()
        base_font = QFont("Consolas", 10) # Slightly larger font for better readability
        
        # Professional Light Theme Backgrounds (Beige match)
        bg_color = QColor("#faf7f2")
        fg_color = QColor("#1e293b") 
        self.lexer.setDefaultFont(base_font)
        self.lexer.setDefaultPaper(bg_color)
        self.lexer.setDefaultColor(fg_color)
        
        # ⚠️ CRITICAL: We must explicitly set the font, background, AND foreground 
        # for ALL 128 possible Python lexer styles. Otherwise, standard variables 
        # (like cv2 or np) will default back to Windows Black, making them invisible!
        for i in range(128):
            self.lexer.setFont(base_font, i)
            self.lexer.setPaper(bg_color, i)
            self.lexer.setColor(fg_color, i)
            
        # 2. Semantic Syntax Highlighting (Modern Light Theme Style)
        self.lexer.setColor(QColor("#7c3aed"), QsciLexerPython.Keyword)            # Purple Keywords
        self.lexer.setColor(QColor("#2563eb"), QsciLexerPython.ClassName)          # Blue classes
        self.lexer.setColor(QColor("#0891b2"), QsciLexerPython.FunctionMethodName) # Cyan/Teal functions
        self.lexer.setColor(QColor("#059669"), QsciLexerPython.SingleQuotedString) # Green strings
        self.lexer.setColor(QColor("#059669"), QsciLexerPython.DoubleQuotedString)
        self.lexer.setColor(QColor("#64748b"), QsciLexerPython.Comment)            # Slate/Gray comments
        self.lexer.setColor(QColor("#db2777"), QsciLexerPython.Decorator)          # Pink decorators
        
        self.setLexer(self.lexer)
        self.setCaretForegroundColor(QColor("#1e293b"))
        self.setSelectionBackgroundColor(QColor("#c4b5fd"))
        self.setSelectionForegroundColor(QColor("white"))
        
        # 3. Line Numbers on Left Border
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, "0000") # Allocates space for up to 4 digits
        self.setMarginsBackgroundColor(QColor("#f1f5f9"))
        self.setMarginsForegroundColor(QColor("#64748b"))
        
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        
        # --- 🚀 SNIPPET REGISTRY ---
        # Map function names to their full usage snippets
        self.snippets = {}
 
        # 5. --- 🚀 ADVANCED AUTOCOMPLETE & API REGISTRY ---
        # Initialize the API engine for Python
        self.api = QsciAPIs(self.lexer)
        
        # 🟢 Populate with AI Coding Lab Library Functions
        for category, data in LIBRARY_FUNCTIONS.items():
            for func_name, func_info in data["functions"].items():
                # Build a detailed completion string for searchability
                params_list = [p["name"] for p in func_info.get("params", [])]
                params_str = ", ".join(params_list)
                completion_key = f"{func_name}({params_str})"
                
                # Add to autocomplete
                self.api.add(completion_key)
                
                # Store full usage for replacement on selection (using func name as key is safer)
                self.snippets[func_name] = func_info["usage"]
                # Also store the full completion string as a key just in case
                self.snippets[completion_key] = func_info["usage"]
                
        # 🔵 Add common AI/Robotics Standard Library Keywords
        standard_libs = [
            "cv2.imread", "cv2.imshow", "cv2.waitKey", "cv2.destroyAllWindows",
            "cv2.rectangle", "cv2.putText", "cv2.circle", "cv2.line",
            "np.array", "np.zeros", "np.ones", "np.uint8", "np.float32",
            "os.path.exists", "os.makedirs", "sys.exit", "time.sleep",
            "print", "range", "len", "int", "str", "float", "list", "dict"
        ]
        for lib_func in standard_libs:
            self.api.add(lib_func)
            
        # Compile and link the API to the editor
        self.api.prepare()
        
        # Configure Autocomplete Behavior
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(2) # Show suggestions after 2 characters
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(True)
        
        # Configure Call Tips (Function parameter helpers)
        self.setCallTipsStyle(QsciScintilla.CallTipsStyle.CallTipsContext)
        self.setCallTipsBackgroundColor(QColor("#1e293b"))
        self.setCallTipsForegroundColor(QColor("white"))
        self.setCallTipsVisible(0)

        # 🟢 --- 🚀 MOUSE HOVER TOOLTIPS (Parameter Instructions) ---
        # Using SendScintilla directly as some PyQt bindings don't expose this method
        self.SendScintilla(self.SCI_SETMOUSEDWELLTIME, 600) 
        self.SCN_DWELLSTART.connect(self._handle_dwell_start)
        self.SCN_DWELLEND.connect(self._handle_dwell_end)

        # ⚡ Connect completion signal for snippet injection
        # Fixed: QScintilla uses SCN_AUTOCSELECTION for autocomplete selection signals
        self.SCN_AUTOCSELECTION.connect(self._handle_completion_selected)
        
        # --- 🚀 FILL-IN-THE-BLANKS & TYPE LOGIC INDICATORS ---
        self.BLANK_INDICATOR = 8
        self.indicatorDefine(QsciScintilla.IndicatorStyle.BoxIndicator, self.BLANK_INDICATOR)
        self.setIndicatorForegroundColor(QColor(239, 68, 68, 180), self.BLANK_INDICATOR) # Vibrant Red (Semi-Transparent)
        self.setIndicatorOutlineColor(QColor(185, 28, 28), self.BLANK_INDICATOR) # Dark Red Border

        # 🟢 NEW: Logic Match Indicator (Soft Green glow for source variables)
        self.LOGIC_MATCH_INDICATOR = 10
        self.indicatorDefine(QsciScintilla.IndicatorStyle.BoxIndicator, self.LOGIC_MATCH_INDICATOR)
        self.setIndicatorForegroundColor(QColor(16, 185, 129, 60), self.LOGIC_MATCH_INDICATOR) # Soft Emerald Glow
        self.setIndicatorOutlineColor(QColor(5, 150, 105, 150), self.LOGIC_MATCH_INDICATOR) 

        # 🟡 NEW: Occurrence Indicator (Yellow highlight for same-word matches)
        self.OCCURRENCE_INDICATOR = 11
        # Use FullBoxIndicator for the "Background Fill" look
        self.indicatorDefine(QsciScintilla.IndicatorStyle.FullBoxIndicator, self.OCCURRENCE_INDICATOR)
        self.setIndicatorForegroundColor(QColor(254, 240, 138, 180), self.OCCURRENCE_INDICATOR) # Yellow 200 (Semi-Transparent)
        self.setIndicatorOutlineColor(QColor(250, 204, 21), self.OCCURRENCE_INDICATOR) # Yellow 400 Border
        
        # Set transparency for the fill
        self.SendScintilla(self.SCI_INDICSETALPHA, self.OCCURRENCE_INDICATOR, 100)
        self.SendScintilla(self.SCI_INDICSETOUTLINEALPHA, self.OCCURRENCE_INDICATOR, 200)
        self.SendScintilla(self.SCI_INDICSETALPHA, self.BLANK_INDICATOR, 30)
        self.SendScintilla(self.SCI_INDICSETOUTLINEALPHA, self.BLANK_INDICATOR, 80)
        
        # Scanner Timer for performance (only scan 300ms after last keypress)
        self._blank_timer = QTimer(self)
        self._blank_timer.setSingleShot(True)
        self._blank_timer.timeout.connect(self.scan_for_blanks)
        self.textChanged.connect(lambda: self._blank_timer.start(300))
        
        # Initial scan
        QTimer.singleShot(500, self.scan_for_blanks)

        # 🟢 --- 🚀 PERSISTENT ASSIST BOX (Floating Guidance) ---
        self.assist_box = QFrame(self)
        self.assist_box.hide()
        self.assist_box.setMinimumWidth(200)
        self.assist_box.setMaximumWidth(280) # Balanced shape
        self.assist_box.setMinimumHeight(100)
        self.assist_box.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #6366f1;
                border-radius: 12px;
            }
        """)
        
        self.assist_layout = QVBoxLayout(self.assist_box)
        self.assist_layout.setContentsMargins(15, 15, 15, 15) # Better padding
        self.assist_label = QLabel(self.assist_box)
        self.assist_label.setWordWrap(True)
        self.assist_label.setStyleSheet("border: none; color: #1e293b; font-size: 12px; line-height: 1.5;")
        self.assist_layout.addWidget(self.assist_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Add a premium drop shadow
        shadow = QGraphicsDropShadowEffect(self.assist_box)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(2, 4)
        self.assist_box.setGraphicsEffect(shadow)
        
        # Connect cursor changes to show help when inside blank zones
        self.cursorPositionChanged.connect(self._update_assist_box)
        # 🟡 High-Fidelity Occurrence Selection
        self.selectionChanged.connect(self._update_occurrence_highlights)

    def _update_assist_box(self, line, index):
        """Triggered on cursor changes."""
        pos = self.SendScintilla(self.SCI_GETCURRENTPOS)
        self._show_assistance(pos, -1, -1, trigger="cursor")

    def _show_assistance(self, pos, x, y, trigger="cursor"):
        """Central logic to show/hide the balanced assist box based on context."""
        # 1. Area-Aware Parameter Detection
        # Check if the hover/cursor position is anywhere inside a Red Blank Indicator
        is_in_blank = self.SendScintilla(self.SCI_INDICATORVALUEAT, self.BLANK_INDICATOR, pos)
        
        word = ""
        if is_in_blank:
            # If in a red zone, find the boundaries of the entire 'parameter = ' '' match
            start = self.SendScintilla(self.SCI_INDICATORSTART, self.BLANK_INDICATOR, pos)
            end = self.SendScintilla(self.SCI_INDICATOREND, self.BLANK_INDICATOR, pos)
            
            # Extract and parse the variable name from the block (e.g., "model_path = None")
            try:
                block_text = self.text().encode('utf-8')[start:end].decode('utf-8').strip()
                # Find the word before '='
                match = re.search(r"([a-zA-Z_]\w*)\s*=", block_text)
                if match:
                    word = match.group(1)
            except:
                pass

        # If not in a red zone or parsing failed, try to get the word directly under cursor
        if not word:
            word = self._get_word_at_pos(pos)

        if not word:
            if trigger != "cursor": self.assist_box.hide()
            return

        tip_text = ""
        line, _ = self.lineIndexFromPosition(pos)
        line_text = self.text(line)

        # 2. Identify Function or Parameter Details
        is_func = False
        tip_text_inner = ""
        param_type = ""
        
        for category, data in LIBRARY_FUNCTIONS.items():
            # A. Is it a library function name? (Return-Type Info)
            if word in data["functions"]:
                f_info = data["functions"][word]
                tip_text_inner = f"{f_info['desc']}<br><br><i>Returns: {f_info['returns']['type']}</i>"
                is_func = True
                break
            
            # B. Is it a known parameter on the current line? (Requirement-Type Info)
            if not is_func:
                for f_name, f_info in data["functions"].items():
                    if f_name in line_text:
                        for p in f_info.get("params", []):
                            if p["name"] == word:
                                tip_text_inner = f"{p['desc']}"
                                param_type = p["type"]
                                break
                    if tip_text_inner: break
            if tip_text_inner: break

        # 3. Smart Reference: Find existing variables that match this parameter's type
        reference_tip = ""
        registry = self._scan_variable_types()
        matches = []
        
        # Clear previous logic match highlights before redraw
        self.clearIndicatorRange(0, 0, self.lines()-1, 120, self.LOGIC_MATCH_INDICATOR)

        if param_type:
            # Normalize types (e.g. 'Image' and 'Image (ndarray)' are the same for the student)
            simple_target = param_type.split("(")[0].strip().lower()
            
            for var_name, var_data in registry.items():
                var_type = var_data["type"]
                simple_var = var_type.split("(")[0].strip().lower()
                
                if simple_var == simple_target:
                    matches.append(f"<b>'{var_name}'</b>")
                    # 🌉 VISUAL BRIDGE: Highlight where this variable was created!
                    s_line, s_col = self.lineIndexFromPosition(var_data["start"])
                    e_line, e_col = self.lineIndexFromPosition(var_data["end"])
                    self.fillIndicatorRange(s_line, s_col, e_line, e_col, self.LOGIC_MATCH_INDICATOR)
            
            if matches:
                reference_tip = f"<br><div style='margin-top:8px; padding-top:8px; border-top: 1px solid #e2e8f0; color:#10b981;'>🔗 <b>Connect Logic:</b> Try using your variable {', '.join(matches)} here!</div>"

        # 4. Workspace Shortcut: Find if it's a path-based parameter
        workspace_tip = ""
        if "path" in word.lower():
             workspace_tip = f"<br><div style='margin-top:8px; padding-top:8px; border-top: 1px solid #e2e8f0; color:#6366f1;'>🔍 <b>Select model:</b> 📂 <b>Workspace</b> ➔ 📦 <b>Model</b><br><i style='font-size:11px; color:#94a3b8;'>Choose your file to find the local path!</i></div>"

        # 5. Show and Position the Balanced Box
        if tip_text_inner:
            # Add the reference and workspace tips if applicable
            tip_text_inner += reference_tip
            tip_text_inner += workspace_tip
            
            # Check if current value is 'Nonsense' or 'Type Mismatch'
            is_nonsense = False
            is_mismatch = False
            current_val = ""
            var_type_actual = ""
            
            if is_in_blank:
               start = self.SendScintilla(self.SCI_INDICATORSTART, self.BLANK_INDICATOR, pos)
               end = self.SendScintilla(self.SCI_INDICATOREND, self.BLANK_INDICATOR, pos)
               block_text = self.text().encode('utf-8')[start:end].decode('utf-8').strip()
               val_match = re.search(r"=\s*(.*)", block_text)
               if val_match:
                   current_val = val_match.group(1).strip()
                   if current_val != "None" and current_val != "":
                       if current_val not in registry:
                           # Check for literal strings/numbers
                           if not (current_val.startswith("'") or current_val.startswith('"') or current_val.isdigit()):
                               is_nonsense = True
                       else:
                           # --- 🧬 TYPE CHECK ---
                           var_info = registry[current_val]
                           var_type_actual = var_info["type"].split("(")[0].strip().lower()
                           target_type_simple = param_type.split("(")[0].strip().lower()
                           
                           if var_type_actual != target_type_simple:
                               is_mismatch = True

            # 🎨 --- 🚥 DYNAMIC COLOR-CODING ---
            if is_in_blank:
                if is_mismatch:
                    # TYPE MISMATCH MODE (Red)
                    self.assist_box.setStyleSheet("""
                        QFrame { background-color: #ffffff; border: 2px solid #ef4444; border-radius: 12px; }
                    """)
                    title_style = "color:#ef4444; font-size: 13px;"
                    prefix_icon = "🧬"
                    action_text = "Type Mismatch"
                    tip_text_inner += f"<br><br><span style='color:#ef4444;'>❌ <b>'{current_val}'</b> is an <b>{registry[current_val]['type']}</b>, but this slot needs a <b>{param_type}</b>.</span>"
                elif is_nonsense:
                    # NONSENSE MODE (Red)
                    self.assist_box.setStyleSheet("""
                        QFrame { background-color: #ffffff; border: 2px solid #ef4444; border-radius: 12px; }
                    """)
                    title_style = "color:#ef4444; font-size: 13px;"
                    prefix_icon = "🕵️‍♂️"
                    action_text = f"Warning: '{current_val}' Unknown"
                    if matches:
                         tip_text_inner += f"<br><br><span style='color:#ef4444;'>❌ <b>'{current_val}'</b> is not defined yet.</span>"
                else:
                    # MANDATORY MODE (Amber)
                    self.assist_box.setStyleSheet("""
                        QFrame { background-color: #ffffff; border: 2px solid #f59e0b; border-radius: 12px; }
                    """)
                    title_style = "color:#d97706; font-size: 13px;"
                    prefix_icon = "⚠️"
                    action_text = "Action: Fill"
            else:
                # REFERENCE MODE (Indigo/Blue for Info)
                self.assist_box.setStyleSheet("""
                    QFrame {
                        background-color: #ffffff;
                        border: 2px solid #6366f1;
                        border-radius: 12px;
                    }
                """)
                title_style = "color:#4338ca; font-size: 13px;" # Indigo 700
                prefix_icon = "💡" if is_func else "📝"
                action_text = "Reference"

            # Reformat text with the dynamic style
            styled_text = f"{prefix_icon} <b style='{title_style}'>{action_text}: {word}</b><br><br>{tip_text_inner}"
            self.assist_label.setText(styled_text)
            self.assist_box.adjustSize()
            
            # Position safely relative to trigger
            if x != -1 and y != -1:
                box_x, box_y = x + 15, y - self.assist_box.height() - 10
            else:
                px = self.SendScintilla(self.SCI_POINTXFROMPOSITION, 0, pos)
                py = self.SendScintilla(self.SCI_POINTYFROMPOSITION, 0, pos)
                box_x, box_y = px + 25, py - self.assist_box.height() - 12

            if box_y < 10: box_y += self.assist_box.height() + 40
            if box_x + self.assist_box.width() > self.width(): box_x = self.width() - self.assist_box.width() - 20

            self.assist_box.move(box_x, box_y)
            self.assist_box.show()
            self.assist_box.raise_()
        else:
            self.assist_box.hide()

    def scan_for_blanks(self):
        """Finds AI function parameters that are either 'None' (missing) or 'Nonsense' (unknown variable)."""
        # 1. Clear all existing indicators
        total_lines = self.lines()
        if total_lines > 0:
            last_line_len = len(self.text(total_lines - 1))
            self.clearIndicatorRange(0, 0, total_lines - 1, last_line_len, self.BLANK_INDICATOR)
            
        content_bytes = self.text().encode('utf-8')
        content_str = content_bytes.decode('utf-8', errors='ignore')
        registry = self._scan_variable_types()
        
        # 2. Iterate through all categories and functions in our library
        for category, data in LIBRARY_FUNCTIONS.items():
            for f_name, f_info in data["functions"].items():
                # Regex: find 'FunctionName(args)'
                # This ensures we only look INSIDE function calls!
                pattern = rf"\b{f_name}\s*\(([^)]*)\)"
                
                for f_match in re.finditer(pattern, content_str):
                    args_str = f_match.group(1)
                    args_start_pos = f_match.start(1) # Start of text inside (...)
                    
                    # 3. Inside the parentheses, find 'param_name = value'
                    # We split by comma to handle multiple parameters correctly
                    args_list = args_str.split(',')
                    current_offset = 0
                    
                    for arg in args_list:
                        # Find 'param_name = value' pattern
                        # We use a non-greedy value match to ensure we don't bleed into next params
                        p_match = re.search(r"\b([a-zA-Z_]\w*)\s*=\s*([^,\n]*)", arg)
                        if p_match:
                            param_name = p_match.group(1)
                            val_text = p_match.group(2).strip()
                            
                            should_highlight = False
                            # 🧪 ADVANCED VALIDATION LOGIC
                            if not val_text or val_text == "None":
                                # 🔴 CASE 1: Empty or 'None' (Mandatory Action)
                                should_highlight = True
                            else:
                                # 🧬 CASE 2: Type Flow & Nonsense Check
                                is_string = (val_text.startswith("'") or val_text.startswith('"'))
                                is_number = val_text.replace('.', '', 1).isdigit()
                                if not is_string and not is_number:
                                    if val_text not in registry:
                                        # Unknown Variable
                                        should_highlight = True
                                    else:
                                        # 🛡️ STRICT TYPE CHECK
                                        # Find expected type for this specific parameter
                                        target_type = ""
                                        for category, data in LIBRARY_FUNCTIONS.items():
                                            for f_name_inner, f_info_inner in data["functions"].items():
                                                if f_name_inner == f_name:
                                                     for p in f_info_inner["params"]:
                                                         if p["name"] == param_name:
                                                             target_type = p["type"]
                                                             break
                                            if target_type: break
                                        
                                        if target_type:
                                            # Normalize and compare
                                            var_info = registry[val_text]
                                            var_type_actual = var_info["type"].split("(")[0].strip().lower()
                                            target_type_simple = target_type.split("(")[0].strip().lower()
                                            
                                            if var_type_actual != target_type_simple:
                                                # Valid variable but WRONG logical type!
                                                should_highlight = True

                            if should_highlight:
                                # Calculate exact byte range for this specific parameter assignment
                                arg_in_full = args_str[current_offset:]
                                p_start_in_arg = arg_in_full.find(p_match.group(0))
                                
                                global_char_start = args_start_pos + current_offset + p_start_in_arg
                                global_char_end = global_char_start + len(p_match.group(0))
                                
                                byte_start = len(content_str[:global_char_start].encode('utf-8'))
                                byte_end = len(content_str[:global_char_end].encode('utf-8'))
                                
                                if byte_end > byte_start:
                                    s_line, s_col = self.lineIndexFromPosition(byte_start)
                                    e_line, e_col = self.lineIndexFromPosition(byte_end)
                                    self.fillIndicatorRange(s_line, s_col, e_line, e_col, self.BLANK_INDICATOR)

                        current_offset += len(arg) + 1 # +1 for comma

    def _handle_completion_selected(self, selection, position):
        """When a function is selected, check if we should replace it with a full usage snippet."""
        # 1. Normalization
        if hasattr(selection, "decode"):
            selection = selection.decode('utf-8')
            
        # Extract function name from completion string (e.g., 'Get_Frame(cap)' -> 'Get_Frame')
        func_name = selection.split('(')[0].strip()
            
        if func_name in self.snippets:
            # 🛑 STOP default Scintilla insertion
            self.SendScintilla(self.SCI_AUTOCCANCEL)
            
            snippet = self.snippets[func_name]
            
            # 2. Identify the partial text typed by the user (e.g. 'Get_')
            line, index = self.getCursorPosition()
            
            # Use absolute positions to find the exact word boundaries
            pos = self.SendScintilla(self.SCI_GETCURRENTPOS)
            word_start = self.SendScintilla(self.SCI_WORDSTARTPOSITION, pos, True)
            word_end = self.SendScintilla(self.SCI_WORDENDPOSITION, pos, True)
            
            # If word_end hasn't moved, use current index
            if word_end <= word_start:
                word_end = pos
                
            start_line, start_col = self.lineIndexFromPosition(word_start)
            end_line, end_col = self.lineIndexFromPosition(word_end)
            
            # 3. Decision Logic: Full Snippet vs. Function Call
            line_text = self.text(line)
            prefix = line_text[:start_col].strip()
            
            if not prefix:
                # Start of line: Full assignment snippet
                indent_str = " " * self.indentation(line)
                new_line_content = indent_str + snippet + "\n"
                
                # Select the entire current line (including the partial word typed)
                self.setSelection(line, 0, line, len(line_text))
                self.replaceSelectedText(new_line_content)
                
                # Strategic cursor placement after '='
                eq_idx = new_line_content.find("=")
                if eq_idx != -1:
                    self.setCursorPosition(line, eq_idx + 2)
                else:
                    self.setCursorPosition(line, len(new_line_content))
            else:
                # Middle of code: Just the function call from snippet
                # Extract part after '= ' if present
                call_part = snippet.split("=")[-1].strip() if "=" in snippet else snippet
                self.setSelection(line, start_col, line, end_col)
                self.replaceSelectedText(call_part)

    # ── Tooltips & Intelligence ────────────────────────────────────────

    def _get_word_at_pos(self, pos):
        """Helper to extract the word string at a specific absolute position."""
        start = self.SendScintilla(self.SCI_WORDSTARTPOSITION, pos, True)
        end = self.SendScintilla(self.SCI_WORDENDPOSITION, pos, True)
        if start == end: return ""
        
        # Scintilla positions are bytes
        content_bytes = self.text().encode('utf-8')
        return content_bytes[start:end].decode('utf-8', errors='ignore')

    def _handle_dwell_start(self, pos, x, y):
        """Show instructional tooltips when hovering over AI functions or parameters."""
        # Use our unified persistent assist box for hovers too
        self._show_assistance(pos, x, y, trigger="dwell")

    def _handle_dwell_end(self, pos, x, y):
        """Only hide if we aren't still active due to cursor position."""
        # If cursor isn't in a blank, we can hide on mouse leave
        cursor_pos = self.SendScintilla(self.SCI_GETCURRENTPOS)
        is_in_blank = self.SendScintilla(self.SCI_INDICATORVALUEAT, self.BLANK_INDICATOR, cursor_pos)
        if not is_in_blank:
            self.assist_box.hide()

    def _update_occurrence_highlights(self):
        """Finds and highlights all occurrences of the currently selected word."""
        # 1. Clear previous highlights
        total_lines = self.lines()
        self.clearIndicatorRange(0, 0, total_lines if total_lines > 0 else 0, 120, self.OCCURRENCE_INDICATOR)

        # 2. Extract selected word
        if not self.hasSelectedText():
            return
            
        selected_text = self.selectedText().strip()
        
        # Only highlight if it's a valid "word" (letters, numbers, underscores)
        if not selected_text or not re.match(r"^[a-zA-Z_]\w*$", selected_text):
            return
            
        # 3. Scan the whole document for exact word matches
        content = self.text()
        pattern = rf"\b{re.escape(selected_text)}\b"
        
        for match in re.finditer(pattern, content):
            start_pos = match.start()
            end_pos = match.end()
            
            # Convert char offsets to BYTES, then to line/col for fillIndicatorRange
            byte_start = len(content[:start_pos].encode('utf-8'))
            byte_end = len(content[:end_pos].encode('utf-8'))
            
            s_line, s_col = self.lineIndexFromPosition(byte_start)
            e_line, e_col = self.lineIndexFromPosition(byte_end)
            self.fillIndicatorRange(s_line, s_col, e_line, e_col, self.OCCURRENCE_INDICATOR)

    def _scan_variable_types(self):
        """Analyzes the current script to find what variables represent what data types."""
        registry = {}
        content = self.text()
        content_bytes = content.encode('utf-8')
        
        # Regex to find: var_name = FunctionName(args)
        # We also capture the byte positions
        for category, data in LIBRARY_FUNCTIONS.items():
            for f_name, f_info in data["functions"].items():
                pattern = rf"\b([a-zA-Z_]\w*)\s*=\s*{f_name}\b"
                for match in re.finditer(pattern, content):
                    var_name = match.group(1)
                    # We store type + actual byte positions for highlighting
                    registry[var_name] = {
                        "type": f_info["returns"]["type"],
                        "start": len(content[:match.start(1)].encode('utf-8')),
                        "end": len(content[:match.end(1)].encode('utf-8'))
                    }
        
        return registry

    # ── Smart Scope Detection ───────────────────────────────────────
    
    def get_contextual_indent(self, line):
        """Determine what the indentation SHOULD be for a given line index based on Python scope."""
        if line <= 0: return 0
        
        # 1. Scan upwards to find the context from the nearest relative code
        for i in range(line - 1, -1, -1):
            text = self.text(i).strip()
            if not text: continue  # Skip empty lines
            
            # Case A: We hit an END marker block (e.g., # [ENDIF] or # [ENDLOOP])
            # This line itself might be indented, but the NEXT line should be one level out.
            if "[END" in text:
                return max(0, self.indentation(i) - 4)
                
            # Case B: If a line ends with colon, the next line MUST be indented one level in
            if text.endswith(":"):
                return self.indentation(i) + 4
            
            # Case C: If the line itself is a de-indenter (like else:), but we already handled text.endswith(':')
            # we just match it.
            
            # Case D: Otherwise, just match the indentation of the nearest code line above
            return self.indentation(i)
            
        return 0

    # ── Ghost Block (Drag & Drop Visuals) ───────────────────────────
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            self._drag_active = True
            event.acceptProposedAction()
            self.update()

    def dragLeaveEvent(self, event):
        self._drag_active = False
        self._target_line = -1
        self.update()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            pos = event.position().toPoint()
            
            # --- 🚀 SMART CONTEXTUAL POSITIONING ---
            # Only use pixel Y to find the line. Ignore pixel X; 
            # the indentation is automatically calculated from the local scope.
            char_pos = self.SendScintilla(self.SCI_POSITIONFROMPOINT, pos.x(), pos.y())
            line, _ = self.lineIndexFromPosition(char_pos)
            
            if line != -1:
                self._target_line = line
                # Calculate what the indentation SHOULD be for this line
                self._target_col = self.get_contextual_indent(line)
                
                # Show cursor at the start of original line for clarity
                self.setCursorPosition(line, 0)
            
            event.acceptProposedAction()
            self.update()

    def dropEvent(self, event):
        self._drag_active = False
        pos = event.position().toPoint()
        
        char_pos = self.SendScintilla(self.SCI_POSITIONFROMPOINT, pos.x(), pos.y())
        line, _ = self.lineIndexFromPosition(char_pos)
        
        if line == -1:
            line = self.lines() - 1
            
        function_id = event.mimeData().text()
        # Use calculated scope indentation for the final drop
        target_indent = self.get_contextual_indent(line)
        self.functionDropped.emit(function_id, (line, target_indent))
        event.acceptProposedAction()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._drag_active:
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Constants for grid alignment
            char_width = self.fontMetrics().horizontalAdvance(' ')
            margin_width = self.marginWidth(0) 
            scroll_x = self.horizontalScrollBar().value()
            view_w = self.viewport().width()
            view_h = self.viewport().height()
            
            # --- 1. Global Structural Map (The 'Horizontal' Layers) ---
            # We iterate through visible lines and tint their backgrounds based on their current indentation.
            # This shows the "Main", "Loop", and "Condition" blocks clearly.
            
            row_h = self.textHeight(0)
            first_vis = self.firstVisibleLine()
            last_vis = first_vis + (view_h // row_h) + 1
            max_line = self.lines()
            
            for line_idx in range(first_vis, min(max_line, last_vis)):
                # 🚀 Use Smart Scope detection so even empty lines show their 'intended' block color
                indent = self.get_contextual_indent(line_idx)
                
                # Determine Block Color
                block_color = None
                if indent >= 8:
                    block_color = QColor(168, 85, 247, 20) # Purple (Condition)
                elif indent >= 4:
                    block_color = QColor(59, 130, 246, 20)  # Blue (Loop)
                else:
                    block_color = QColor(34, 197, 94, 20)   # Green (Main)
                
                # Draw the horizontal block stripe
                line_y = (line_idx - first_vis) * row_h
                painter.fillRect(0, line_y, view_w, row_h, block_color)

            # --- 2. Indentation Zones (Vertical Guides) ---
            # These help align the mouse to specific indent levels
            z0_x = margin_width - scroll_x
            z0_w = 4 * char_width
            # Faint vertical guide for the margins
            painter.setPen(QPen(QColor(0, 0, 0, 15), 1, Qt.PenStyle.DotLine))
            painter.drawLine(int(z0_x + z0_w), 0, int(z0_x + z0_w), view_h)
            painter.drawLine(int(z0_x + 2 * z0_w), 0, int(z0_x + 2 * z0_w), view_h)

            # --- 3. Current Targeted Row & Zone Focus ---
            if self._target_line != -1:
                # Find Target Indent based on mouse X position
                # We repeat the logic from main.py here to show predictive colors
                target_indent_level = 0
                bg_color = QColor(34, 197, 94, 60) # Default Green
                
                if self._target_col >= 4 and self._target_col < 8:
                    target_indent_level = 1
                    bg_color = QColor(59, 130, 246, 60) # Blue
                elif self._target_col >= 8:
                    target_indent_level = 2
                    bg_color = QColor(168, 85, 247, 60) # Purple
                
                line_y = (self._target_line - first_vis) * row_h
                
                # Draw a highlight behind the line to indicate where the code will land
                # and what its indentation/color will be.
                target_rect = QRect(0, line_y, view_w, row_h)
                painter.fillRect(target_rect, bg_color)
                
                # Draw a "Ghost Block" pointer showing the indent depth
                pointer_w = (target_indent_level + 1) * (4 * char_width)
                painter.fillRect(QRect(0, line_y, int(pointer_w + margin_width), 3), bg_color.darker(150))

    # API compatibility layer so we don't have to rewrite the saving logic in main.py
    def toPlainText(self):
        return self.text()
        
    def setPlainText(self, text):
        self.setText(text)
