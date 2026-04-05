from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt

class VariableCard(QFrame):
    def __init__(self, name, var_type, value):
        super().__init__()
        self.setStyleSheet("""
            VariableCard {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            VariableCard:hover { border: 1px solid #3b82f6; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header: Name and Type Badge
        header = QHBoxLayout()
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("color: #93c5fd; font-weight: bold; font-family: monospace;")
        
        lbl_type = QLabel(var_type)
        lbl_type.setStyleSheet("background: rgba(147, 51, 234, 0.2); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.4); border-radius: 4px; padding: 2px 6px; font-size: 9px;")
        
        header.addWidget(lbl_name)
        header.addStretch()
        header.addWidget(lbl_type)
        layout.addLayout(header)

        # Value display
        val_str = str(value)
        if len(val_str) > 100: val_str = val_str[:100] + "..."
        
        lbl_val = QLabel(val_str)
        lbl_val.setWordWrap(True)
        lbl_val.setStyleSheet("color: #94a3b8; font-family: monospace; font-size: 11px; background: #0f172a; padding: 6px; border-radius: 4px;")
        layout.addWidget(lbl_val)

def clear_layout(layout):
    while layout.count() > 1: # Keep the spacer
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

def update_results_panel(ui, variables_list):
    """
    variables_list should be a list of dicts: [{'name': 'img', 'type': 'ndarray', 'value': '...'}]
    """
    layout = ui.resultsListLayout
    clear_layout(layout)
    
    ui.lblVarCount.setText(f"{len(variables_list)} vars")
    
    for var in variables_list:
        card = VariableCard(var['name'], var['type'], var['value'])
        layout.insertWidget(layout.count() - 1, card)