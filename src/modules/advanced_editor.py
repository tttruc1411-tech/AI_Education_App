from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QTimer
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout, QGraphicsDropShadowEffect
from .library.definitions import LIBRARY_FUNCTIONS
import re

class AdvancedPythonEditor(QsciScintilla):
    # Signal to notify when a function is dropped
    functionDropped = pyqtSignal(str, tuple) # (function_id, (line, col))

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._lang = "en"  # Current language for tooltips
        
        # Drag-and-drop state for Ghost Blocks
        self._drag_active = False
        self._target_line = -1
        self._target_col = -1
        
        # 1. Setup Python Lexer with beautiful fonts
        self.lexer = QsciLexerPython()
        base_font = QFont("Consolas", 11) # Compact font for better visibility of long scripts
        
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
        self.setSelectionForegroundColor(QColor("#1e293b"))
        
        # 3. Line Numbers on Left Border
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, "0000") # Allocates space for up to 4 digits
        self.setMarginsBackgroundColor(QColor("#f1f5f9"))
        self.setMarginsForegroundColor(QColor("#64748b"))
        
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        
        # 🐍 Smart Python Indentation Settings
        self.setAutoIndent(True)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setBackspaceUnindents(True)
        self.setIndentationGuides(True)
        self.setIndentationGuidesBackgroundColor(QColor("#e2e8f0"))
        self.setIndentationGuidesForegroundColor(QColor("#cbd5e1"))
        
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
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(2) # Show suggestions after 2 characters
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(True)
        
        # Configure Call Tips (Function parameter helpers)
        self.setCallTipsStyle(QsciScintilla.CallTipsContext)
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
        self.indicatorDefine(QsciScintilla.BoxIndicator, self.BLANK_INDICATOR)
        self.setIndicatorForegroundColor(QColor(239, 68, 68, 180), self.BLANK_INDICATOR) # Vibrant Red (Semi-Transparent)
        self.setIndicatorOutlineColor(QColor(185, 28, 28), self.BLANK_INDICATOR) # Dark Red Border

        # 🟢 NEW: Logic Match Indicator (Soft Green glow for source variables)
        self.LOGIC_MATCH_INDICATOR = 10
        self.indicatorDefine(QsciScintilla.BoxIndicator, self.LOGIC_MATCH_INDICATOR)
        self.setIndicatorForegroundColor(QColor(16, 185, 129, 60), self.LOGIC_MATCH_INDICATOR) # Soft Emerald Glow
        self.setIndicatorOutlineColor(QColor(5, 150, 105, 150), self.LOGIC_MATCH_INDICATOR) 

        # 🟡 NEW: Occurrence Indicator (Yellow highlight for same-word matches)
        self.OCCURRENCE_INDICATOR = 11
        # Use FullBoxIndicator for the "Background Fill" look
        self.indicatorDefine(QsciScintilla.FullBoxIndicator, self.OCCURRENCE_INDICATOR)
        self.setIndicatorForegroundColor(QColor(255, 255, 0), self.OCCURRENCE_INDICATOR)  # Pure Neon Yellow
        self.setIndicatorOutlineColor(QColor(220, 180, 0), self.OCCURRENCE_INDICATOR)     # Deep gold border
        self.SendScintilla(self.SCI_INDICSETALPHA, self.OCCURRENCE_INDICATOR, 255)        # pure solid color since it's underneath
        self.SendScintilla(self.SCI_INDICSETOUTLINEALPHA, self.OCCURRENCE_INDICATOR, 255)
        # 🔑 Critical: Draw the background UNDER the text so it doesn't overlap and wash out the text colors!
        # SCI_INDICSETUNDER = 2510
        self.SendScintilla(2510, self.OCCURRENCE_INDICATOR, True)


        # 🟣 Occurrence Text Indicator — forces text color over Lexer tokens
        self.OCCURRENCE_TEXT_INDICATOR = 12
        if hasattr(QsciScintilla, 'TextColorIndicator'):
            self.indicatorDefine(QsciScintilla.TextColorIndicator, self.OCCURRENCE_TEXT_INDICATOR)
        else:
            self.indicatorDefine(17, self.OCCURRENCE_TEXT_INDICATOR) # INDIC_TEXTFORE = 17
        # SCI_INDICSETFLAGS = 2523, SC_INDICFLAG_VALUEFORE = 1
        # This absolutely forces Scintilla to use the value we pass as the text foreground
        self.SendScintilla(2523, self.OCCURRENCE_TEXT_INDICATOR, 1)
        # Globally set the dark purple text color (#3b0764) for fallback
        self.setIndicatorForegroundColor(QColor(59, 7, 100), self.OCCURRENCE_TEXT_INDICATOR)
        self.SendScintilla(self.SCI_INDICSETOUTLINEALPHA, self.BLANK_INDICATOR, 80)
        
        # 🔒 NEW: Protected/Read-Only Tag Indicator (Indicator 13)
        self.PROTECTED_INDICATOR = 13
        self.indicatorDefine(QsciScintilla.PlainIndicator, self.PROTECTED_INDICATOR)
        # We don't want visual clutter, so we make it invisible but logically active
        self.setIndicatorForegroundColor(QColor(0,0,0,0), self.PROTECTED_INDICATOR)
        
        # Scanner Timer for performance (only scan 300ms after last keypress)
        self._blank_timer = QTimer(self)
        self._blank_timer.setSingleShot(True)
        self._blank_timer.timeout.connect(self.scan_for_blanks)
        self.textChanged.connect(lambda: self._blank_timer.start(300))
        
        # Initial scan
        QTimer.singleShot(500, self.scan_for_blanks)

        # 🟢 --- 🚀 PERSISTENT ASSIST BOX (Floating Guidance) ---
        self._is_small = False  # Resolution mode — updated from main.py
        self.assist_box = QFrame(self)
        self.assist_box.hide()
        self.assist_box.setMinimumWidth(220)
        self.assist_box.setMaximumWidth(340)
        self.assist_box.setMinimumHeight(60)
        self.assist_box.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #6366f1;
                border-radius: 12px;
            }
        """)
        
        self.assist_layout = QVBoxLayout(self.assist_box)
        self.assist_layout.setContentsMargins(15, 15, 15, 15)
        self.assist_label = QLabel(self.assist_box)
        self.assist_label.setWordWrap(True)
        self._update_assist_base_style()
        self.assist_layout.addWidget(self.assist_label, 0, Qt.AlignCenter)
        
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

    def _update_assist_base_style(self):
        """Update assist label base font size based on resolution mode."""
        fs = 8 if self._is_small else 12
        self.assist_label.setStyleSheet(f"border: none; color: #1e293b; font-size: {fs}px; line-height: 1.5;")

    def _get_assist_title_fs(self):
        """Get the title font size for the assist box based on resolution."""
        return 10 if self._is_small else 16

    def _update_assist_box(self, line, index):
        """Triggered on cursor changes."""
        pos = self.SendScintilla(self.SCI_GETCURRENTPOS)
        self._show_assistance(pos, -1, -1, trigger="cursor")

    def _show_assistance(self, pos, x, y, trigger="cursor"):
        """Central logic to show/hide the balanced assist box based on context."""
        if pos < 0:
            return
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
                tip_text_inner = f"{f_info['desc']}<br><br><i>{'Giá trị của hàm' if self._lang == 'vi' else 'Returns'}: {f_info['returns']['type']}</i>"
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
             workspace_tip = f"<br><div style='margin-top:8px; padding-top:8px; border-top: 1px solid #e2e8f0; color:#6366f1;'>🔍 <b>Select model:</b> 📂 <b>Workspace</b> ➔ 📦 <b>Model</b><br><i style='font-size:13px; color:#94a3b8;'>Choose your file to find the local path!</i></div>"

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
                           
                           if var_type_actual != target_type_simple and target_type_simple != "any" and var_type_actual != "any":
                               is_mismatch = True

            # 🎨 --- 🚥 DYNAMIC COLOR-CODING ---
            if is_in_blank:
                if is_mismatch:
                    # TYPE MISMATCH MODE (Red)
                    self.assist_box.setStyleSheet("""
                        QFrame { background-color: #ffffff; border: 2px solid #ef4444; border-radius: 12px; }
                    """)
                    title_style = f"color:#ef4444; font-size: {self._get_assist_title_fs()}px;"
                    prefix_icon = "🧬"
                    action_text = "Type Mismatch"
                    tip_text_inner += f"<br><br><span style='color:#ef4444;'>❌ <b>'{current_val}'</b> is an <b>{registry[current_val]['type']}</b>, but this slot needs a <b>{param_type}</b>.</span>"
                elif is_nonsense:
                    # NONSENSE MODE (Red)
                    self.assist_box.setStyleSheet("""
                        QFrame { background-color: #ffffff; border: 2px solid #ef4444; border-radius: 12px; }
                    """)
                    title_style = f"color:#ef4444; font-size: {self._get_assist_title_fs()}px;"
                    prefix_icon = "🕵️‍♂️"
                    action_text = f"Warning: '{current_val}' Unknown"
                    if matches:
                         tip_text_inner += f"<br><br><span style='color:#ef4444;'>❌ <b>'{current_val}'</b> is not defined yet.</span>"
                else:
                    # MANDATORY MODE (Amber)
                    self.assist_box.setStyleSheet("""
                        QFrame { background-color: #ffffff; border: 2px solid #f59e0b; border-radius: 12px; }
                    """)
                    title_style = f"color:#d97706; font-size: {self._get_assist_title_fs()}px;"
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
                title_style = f"color:#4338ca; font-size: {self._get_assist_title_fs()}px;" # Indigo 700
                prefix_icon = "💡" if is_func else "📝"
                action_text = "Reference"

            # Reformat text with the dynamic style
            styled_text = f"{prefix_icon} <b style='{title_style}'>{action_text}: {word}</b><br><br>{tip_text_inner}"
            self.assist_label.setText(styled_text)
            self.assist_label.adjustSize()
            self.assist_box.setMinimumHeight(self.assist_label.sizeHint().height() + 40)
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
            self.clearIndicatorRange(0, 0, total_lines - 1, last_line_len, self.PROTECTED_INDICATOR)
            
        content_bytes = self.text().encode('utf-8')
        content_str = content_bytes.decode('utf-8', errors='ignore')
        registry = self._scan_variable_types()
        
        # 2. Iterate through all categories and functions in our library
        for category, data in LIBRARY_FUNCTIONS.items():
            for f_name, f_info in data["functions"].items():
                # Regex: find 'module.FunctionName(args)' or 'FunctionName(args)'
                # This ensures we only look INSIDE function calls!
                pattern = rf"(?:\w+\.)?{f_name}\s*\(([^)]*)\)"
                
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
                                is_string = (val_text.startswith("'") or val_text.startswith('"')
                                             or val_text.startswith("f'") or val_text.startswith('f"')
                                             or val_text.startswith("r'") or val_text.startswith('r"')
                                             or val_text.startswith("b'") or val_text.startswith('b"'))
                                # Numbers: int, float, negative, or bare digits
                                stripped_val = val_text.lstrip('-')
                                is_number = (stripped_val.replace('.', '', 1).isdigit() if stripped_val else False)
                                # Boolean/None-like constants
                                is_constant = val_text in ("True", "False", "None", "0")
                                # Expressions: contains operators like +, -, *, /, %, //, **
                                is_expression = bool(re.search(r'[\+\-\*/%]', val_text)) and not is_string
                                if not is_string and not is_number and not is_constant and not is_expression:
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
                                            
                                            # Check for mismatch, allowing 'number' flexibility
                                            is_mismatch = True
                                            if (var_type_actual == target_type_simple) or (target_type_simple == "any") or (var_type_actual == "any"):
                                                is_mismatch = False
                                            elif (target_type_simple == "number" or var_type_actual == "number"):
                                                is_mismatch = False
                                            elif (target_type_simple == "list" or var_type_actual == "list"):
                                                is_mismatch = False
                                            
                                            if is_mismatch:
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

                            # 🔒 LOCK the 'param_name =' part — ALWAYS, regardless of value validity
                            arg_in_full = args_str[current_offset:]
                            p_start_in_arg = arg_in_full.find(p_match.group(0))
                            if p_start_in_arg >= 0:
                                global_char_start = args_start_pos + current_offset + p_start_in_arg
                                byte_start = len(content_str[:global_char_start].encode('utf-8'))
                                s_line, s_col = self.lineIndexFromPosition(byte_start)
                                key_text = p_match.group(1) + " ="
                                self.fillIndicatorRange(s_line, s_col, s_line, s_col + len(key_text), self.PROTECTED_INDICATOR)

                        # New: Lock assignments like 'cap = '
                        prefix_match = re.search(rf"\b([a-zA-Z_]\w*)\s*=\s*(?:\w+\.)?{f_name}\b", content_str[:f_match.start()])
                        if prefix_match:
                             p_start = len(content_str[:f_match.start() - (len(f_match.group(0)) + 50)].encode('utf-8')) # safe range
                             # Finding the actual match in the line
                             l_line, _ = self.lineIndexFromPosition(f_match.start())
                             l_text = self.text(l_line)
                             l_match = re.search(rf"\b([a-zA-Z_]\w*)\s*=\s*(?:\w+\.)?{f_name}\b", l_text)
                             if l_match:
                                 # Lock the result variable + equals sign
                                 lock_text = l_match.group(1) + " ="
                                 lock_start = l_text.find(lock_text)
                                 if lock_start != -1:
                                     self.fillIndicatorRange(l_line, lock_start, l_line, lock_start + len(lock_text), self.PROTECTED_INDICATOR)

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
        if pos < 0:
            return ""
        start = self.SendScintilla(self.SCI_WORDSTARTPOSITION, pos, True)
        end = self.SendScintilla(self.SCI_WORDENDPOSITION, pos, True)
        if start == end: return ""
        
        # Scintilla positions are bytes
        content_bytes = self.text().encode('utf-8')
        return content_bytes[start:end].decode('utf-8', errors='ignore')

    def _handle_dwell_start(self, pos, x, y):
        """Show instructional tooltips when hovering over AI functions or parameters."""
        if pos < 0:
            return
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
        # 1. Clear previous highlights (both fill + text color layers)
        total_lines = max(0, self.lines() - 1)
        self.clearIndicatorRange(0, 0, total_lines, 120, self.OCCURRENCE_INDICATOR)
        if hasattr(self, 'OCCURRENCE_TEXT_INDICATOR'):
            self.clearIndicatorRange(0, 0, total_lines, 120, self.OCCURRENCE_TEXT_INDICATOR)

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
        
        # Dark purple #3b0764 as Scintilla RGB integer: R=59, G=7, B=100
        dark_purple_rgb = 59 | (7 << 8) | (100 << 16)
       
        for match in re.finditer(pattern, content):
            # Convert char offsets to BYTES, then to line/col for fillIndicatorRange
            byte_start = len(content[:match.start()].encode('utf-8'))
            byte_end = len(content[:match.end()].encode('utf-8'))
           
            s_line, s_col = self.lineIndexFromPosition(byte_start)
            e_line, e_col = self.lineIndexFromPosition(byte_end)
           
            # Layer 1: Neon yellow FullBox background
            self.fillIndicatorRange(s_line, s_col, e_line, e_col, self.OCCURRENCE_INDICATOR)


            # Layer 2: Dark purple text via SC_INDICFLAG_VALUEFORE using raw int constants
            # 2500=SCI_SETINDICATORCURRENT, 2501=SCI_SETINDICATORVALUE, 2504=SCI_INDICATORFILLRANGE
            self.SendScintilla(2500, self.OCCURRENCE_TEXT_INDICATOR)
            self.SendScintilla(2501, dark_purple_rgb)
            self.SendScintilla(2504, byte_start, byte_end - byte_start)

    def _scan_variable_types(self):
        """Analyzes the current script to find what variables represent what data types."""
        registry = {}
        content = self.text()
        
        # Pass 1: Library Function Outputs (e.g. model_session = camera.Init_Camera(...))
        for category, data in LIBRARY_FUNCTIONS.items():
            for f_name, f_info in data["functions"].items():
                pattern = rf"\b([a-zA-Z_]\w*)\s*=\s*(?:\w+\.)?{f_name}\b"
                for match in re.finditer(pattern, content):
                    var_name = match.group(1)
                    registry[var_name] = {
                        "type": f_info["returns"]["type"],
                        "start": len(content[:match.start(1)].encode('utf-8')),
                        "end": len(content[:match.end(1)].encode('utf-8'))
                    }
        
        # Pass 2: List Literals (e.g. CLASSES = ["a", "b"]) 
        # Supports multi-line with re.DOTALL
        list_pattern = r"\b([a-zA-Z_]\w*)\s*=\s*\[.*?\]"
        for match in re.finditer(list_pattern, content, re.DOTALL):
            var_name = match.group(1)
            registry[var_name] = {
                "type": "List",
                "start": len(content[:match.start(1)].encode('utf-8')),
                "end": len(content[:match.end(1)].encode('utf-8'))
            }

        # Pass 3: String/Numeric Literals (e.g. NAME = "AI", GAIN = 0.5)
        lit_pattern = r"\b([a-zA-Z_]\w*)\s*=\s*('[^']*'|\"[^\"]*\"|-?\d+(?:\.\d+)?)\b"
        for match in re.finditer(lit_pattern, content):
            var_name = match.group(1)
            val = match.group(2)
            var_type = "Text (str)" if (val.startswith("'") or val.startswith('"')) else "Number"
            registry[var_name] = {
                "type": var_type,
                "start": len(content[:match.start(1)].encode('utf-8')),
                "end": len(content[:match.end(1)].encode('utf-8'))
            }

        # Pass 4: General assignments not yet registered (e.g. _, faces = detector.detect(frame))
        # This catches variables from non-library calls so they aren't flagged as "unknown"
        general_pattern = r"\b([a-zA-Z_]\w*)\s*="
        for match in re.finditer(general_pattern, content):
            var_name = match.group(1)
            if var_name not in registry and var_name != "_":
                registry[var_name] = {
                    "type": "Any",
                    "start": len(content[:match.start(1)].encode('utf-8')),
                    "end": len(content[:match.end(1)].encode('utf-8'))
                }
        
        return registry
        
    # 🐍 Python block-opening keywords for smart indentation
    _BLOCK_OPENERS = frozenset((
        'if', 'elif', 'else', 'for', 'while',
        'def', 'class', 'try', 'except', 'finally', 'with'
    ))

    def keyPressEvent(self, event):
        """Smart Python auto-indentation + Fixed Tag (Indicator 13) protection."""
        # 1. Allow Navigation and Selection keys
        if event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down, 
                           Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown,
                           Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt):
            super().keyPressEvent(event)
            return

        # ── 🐍 2. SMART PYTHON AUTO-INDENTATION on Enter/Return ──────────
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # Block Enter inside protected tags
            pos = self.SendScintilla(self.SCI_GETCURRENTPOS)
            if self.SendScintilla(self.SCI_INDICATORVALUEAT, self.PROTECTED_INDICATOR, pos):
                return

            # Capture context from the current line BEFORE inserting newline
            line, col = self.getCursorPosition()
            line_text = self.text(line)
            current_indent = self.indentation(line)
            stripped = line_text.strip()
            text_up_to_cursor = line_text[:col].rstrip()

            # Let QScintilla handle newline + basic auto-indent
            super().keyPressEvent(event)
            new_line, _ = self.getCursorPosition()

            # CASE A: Block opener (if/while/for/def/class/else/try/except/finally/with)
            #         Text before cursor ends with ':' AND first word is a Python keyword
            if text_up_to_cursor.endswith(':'):
                first_word = stripped.split()[0].rstrip(':') if stripped else ''
                if first_word in self._BLOCK_OPENERS:
                    new_indent = current_indent + 4
                    self.setIndentation(new_line, new_indent)
                    self.setCursorPosition(new_line, new_indent)

            # CASE B: Flow terminator → de-indent one level
            #         return, break, continue, pass, raise
            elif stripped in ('return', 'break', 'continue', 'pass') or \
                 stripped.startswith('return ') or stripped.startswith('raise '):
                new_indent = max(0, current_indent - 4)
                self.setIndentation(new_line, new_indent)
                self.setCursorPosition(new_line, new_indent)

            # CASE C: Structural END marker (# [ENDIF], # [ENDLOOP]) → de-indent
            elif stripped.startswith('# [END'):
                new_indent = max(0, current_indent - 4)
                self.setIndentation(new_line, new_indent)
                self.setCursorPosition(new_line, new_indent)

            return

        # ── 3. Protected Tag Guards ──────────────────────────────────────

        # 🚀 OPTION A: If the entire line is selected, allow deletion even if it has protected zones
        if self.hasSelectedText():
            start_line, start_col, end_line, end_col = self.getSelection()
            # If the selection spans the entire line(s) content
            if start_col == 0 and end_col >= len(self.text(end_line).strip()):
                super().keyPressEvent(event)
                return
            
            # Otherwise check if the selection overlaps any protected indicators
            sel_start = self.SendScintilla(self.SCI_GETSELECTIONSTART)
            sel_end = self.SendScintilla(self.SCI_GETSELECTIONEND)
            for i in range(sel_start, sel_end):
                if self.SendScintilla(self.SCI_INDICATORVALUEAT, self.PROTECTED_INDICATOR, i):
                    # Blocking selection modification if it touches protected code
                    return 
        
        # 4. Check current cursor and intended modification
        pos = self.SendScintilla(self.SCI_GETCURRENTPOS)
        
        # CASE: Backspacing into a protected zone
        if event.key() == Qt.Key_Backspace:
            if pos > 0 and self.SendScintilla(self.SCI_INDICATORVALUEAT, self.PROTECTED_INDICATOR, pos - 1):
                return # Block
                
        # CASE: Deleting a character inside a protected zone
        elif event.key() == Qt.Key_Delete:
            if self.SendScintilla(self.SCI_INDICATORVALUEAT, self.PROTECTED_INDICATOR, pos):
                return # Block
        
        # CASE: Regular typing / Tab / Space (Enter is handled above)
        elif event.text() or event.key() == Qt.Key_Tab:
            # If cursor is INSIDE a protected word (not at the end of it)
            if self.SendScintilla(self.SCI_INDICATORVALUEAT, self.PROTECTED_INDICATOR, pos):
                # EXCEPTION: If we are at the very END of the protected zone, and NOT backspacing, allow.
                # Indicator 13 is set for 'param_name ='
                # If we are at the space after '=', we should be free.
                is_prev_protected = self.SendScintilla(self.SCI_INDICATORVALUEAT, self.PROTECTED_INDICATOR, pos - 1) if pos > 0 else False
                if is_prev_protected:
                    # We are on the edge or inside.
                    # Verify if the CURRENT position is ALSO protected (inside the zone)
                    if self.SendScintilla(self.SCI_INDICATORVALUEAT, self.PROTECTED_INDICATOR, pos):
                        return # Block
        
        # If we passed all checks, allow the event
        super().keyPressEvent(event)

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
            pos = event.pos()
            
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
        pos = event.pos()
        
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
            painter.setPen(QPen(QColor(0, 0, 0, 15), 1, Qt.DotLine))
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
