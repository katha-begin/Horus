"""
Horus UI Styling
================

Shared styling functions and theme management for Horus UI components.
"""


def apply_rv_styling(widget):
    """Apply RV dark theme styling."""
    try:
        # Professional dark theme for VFX workflows
        dark_style = """
        QWidget {
            background-color: #2d2d2d;
            color: #e0e0e0;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 9pt;
        }
        
        QFrame {
            border: none;
            background-color: #2d2d2d;
        }
        
        QLabel {
            color: #e0e0e0;
            background-color: transparent;
        }
        
        QPushButton {
            background-color: #404040;
            border: 1px solid #555555;
            color: #e0e0e0;
            padding: 4px 8px;
            border-radius: 2px;
            font-weight: normal;
        }
        
        QPushButton:hover {
            background-color: #4a4a4a;
            border-color: #666666;
        }
        
        QPushButton:pressed {
            background-color: #353535;
            border-color: #777777;
        }
        
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #666666;
            border-color: #444444;
        }
        
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #555555;
            color: #e0e0e0;
            padding: 4px;
            border-radius: 2px;
            selection-background-color: #0078d4;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border-color: #0078d4;
        }
        
        QComboBox {
            background-color: #404040;
            border: 1px solid #555555;
            color: #e0e0e0;
            padding: 4px 8px;
            border-radius: 2px;
        }
        
        QComboBox:hover {
            background-color: #4a4a4a;
            border-color: #666666;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #e0e0e0;
            margin-right: 6px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #404040;
            border: 1px solid #555555;
            color: #e0e0e0;
            selection-background-color: #0078d4;
        }
        
        QTreeWidget, QListWidget, QTableWidget {
            background-color: #1e1e1e;
            border: 1px solid #555555;
            color: #e0e0e0;
            alternate-background-color: #252525;
            selection-background-color: #0078d4;
            gridline-color: #404040;
        }
        
        QTreeWidget::item, QListWidget::item, QTableWidget::item {
            padding: 2px;
            border: none;
        }
        
        QTreeWidget::item:hover, QListWidget::item:hover, QTableWidget::item:hover {
            background-color: #3a3a3a;
        }
        
        QTreeWidget::item:selected, QListWidget::item:selected, QTableWidget::item:selected {
            background-color: #0078d4;
        }
        
        QHeaderView::section {
            background-color: #404040;
            color: #e0e0e0;
            padding: 4px;
            border: 1px solid #555555;
            font-weight: bold;
        }
        
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 12px;
            border: none;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 12px;
            border: none;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #555555;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #666666;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        QSplitter::handle {
            background-color: #555555;
        }
        
        QSplitter::handle:horizontal {
            width: 2px;
        }
        
        QSplitter::handle:vertical {
            height: 2px;
        }
        
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #2d2d2d;
        }
        
        QTabBar::tab {
            background-color: #404040;
            color: #e0e0e0;
            padding: 6px 12px;
            border: 1px solid #555555;
            border-bottom: none;
        }
        
        QTabBar::tab:selected {
            background-color: #2d2d2d;
            border-bottom: 1px solid #2d2d2d;
        }
        
        QTabBar::tab:hover {
            background-color: #4a4a4a;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 1px solid #555555;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 4px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px 0 4px;
        }
        
        QCheckBox, QRadioButton {
            color: #e0e0e0;
            spacing: 4px;
        }
        
        QCheckBox::indicator, QRadioButton::indicator {
            width: 12px;
            height: 12px;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: #1e1e1e;
            border: 1px solid #555555;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 1px solid #0078d4;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #555555;
            height: 4px;
            background-color: #1e1e1e;
            border-radius: 2px;
        }
        
        QSlider::handle:horizontal {
            background-color: #0078d4;
            border: 1px solid #0078d4;
            width: 12px;
            margin: -4px 0;
            border-radius: 6px;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #106ebe;
        }
        
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 2px;
            text-align: center;
            background-color: #1e1e1e;
        }
        
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 1px;
        }
        
        QToolTip {
            background-color: #404040;
            color: #e0e0e0;
            border: 1px solid #555555;
            padding: 4px;
            border-radius: 2px;
        }
        """
        
        widget.setStyleSheet(dark_style)
        
    except Exception as e:
        print(f"Error applying styling: {e}")
