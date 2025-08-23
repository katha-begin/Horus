"""
Horus Comments Panel
===================

Main comments and annotations panel creation and management.
"""

from horus.utils.globals import comments_dock, annotations_popup_window
from horus.comments.comment_widgets import create_comment_widget, create_reply_widget
from horus.comments.sample_data import create_sample_vfx_comments
from horus.comments.comment_handlers import (
    on_add_comment, on_add_frame_comment, show_reply_input, 
    hide_reply_input, post_reply, on_open_annotations_popup
)
from horus.comments.annotations import (
    create_annotations_popup, on_open_rv_paint, on_export_rv_annotations,
    on_clear_annotations, on_save_annotations, get_current_frame, update_frame_info
)


def create_comments_panel():
    """Create comments and annotations panel."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                                       QLabel, QPushButton, QFrame, QListWidget,
                                       QListWidgetItem, QSplitter, QLineEdit,
                                       QComboBox, QScrollArea, QGroupBox)
        from PySide2.QtCore import Qt, QTimer

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Clean header matching reference design
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)

        # Comments title with count
        comments_title = QLabel("Comments (23)")
        comments_title.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 14px;")
        header_layout.addWidget(comments_title)

        header_layout.addStretch()

        # Frame info display (compact)
        frame_info_label = QLabel("Frame: --")
        frame_info_label.setObjectName("frame_info_label")
        frame_info_label.setStyleSheet("color: #888888; font-size: 10px;")
        header_layout.addWidget(frame_info_label)

        # Essential action buttons
        rv_paint_btn = QPushButton("Paint")
        rv_paint_btn.setObjectName("rv_paint_btn")
        rv_paint_btn.setMaximumWidth(50)
        rv_paint_btn.setStyleSheet("font-size: 10px; padding: 2px 4px;")
        header_layout.addWidget(rv_paint_btn)

        annotations_popup_btn = QPushButton("Annotations")
        annotations_popup_btn.setObjectName("annotations_popup_btn")
        annotations_popup_btn.setMaximumWidth(70)
        annotations_popup_btn.setStyleSheet("font-size: 10px; padding: 2px 4px;")
        header_layout.addWidget(annotations_popup_btn)

        layout.addWidget(header_frame)

        # Dynamic comments area - scales with panel height
        comments_scroll = QScrollArea()
        comments_scroll.setWidgetResizable(True)
        comments_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        comments_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        comments_scroll.setStyleSheet("QScrollArea { border: none; }")

        # Comments container
        comments_container = QWidget()
        comments_layout = QVBoxLayout(comments_container)
        comments_layout.setContentsMargins(0, 0, 0, 0)
        comments_layout.setSpacing(8)

        # Load sample comments
        sample_comments = create_sample_vfx_comments()
        for comment_data in sample_comments:
            comment_widget = create_comment_widget(comment_data)
            comments_layout.addWidget(comment_widget)

        # Add stretch to push comments to top
        comments_layout.addStretch()

        comments_scroll.setWidget(comments_container)
        layout.addWidget(comments_scroll)

        # Comment input area
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(5)

        # Comment text input
        comment_text = QTextEdit()
        comment_text.setObjectName("comment_text")
        comment_text.setPlaceholderText("💭 Add a comment...")
        comment_text.setMaximumHeight(60)
        comment_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-size: 11px;
            }
        """)
        input_layout.addWidget(comment_text)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)

        add_comment_btn = QPushButton("Add Comment")
        add_comment_btn.setObjectName("add_comment_btn")
        add_comment_btn.setStyleSheet("font-size: 10px; padding: 4px 8px;")
        button_layout.addWidget(add_comment_btn)

        add_frame_comment_btn = QPushButton("Add Frame Comment")
        add_frame_comment_btn.setObjectName("add_frame_comment_btn")
        add_frame_comment_btn.setStyleSheet("font-size: 10px; padding: 4px 8px;")
        button_layout.addWidget(add_frame_comment_btn)

        button_layout.addStretch()

        input_layout.addLayout(button_layout)
        layout.addWidget(input_frame)

        # Store references for access
        widget.comments_container = comments_container
        widget.comment_text = comment_text
        widget.frame_info_label = frame_info_label

        # Connect signals
        rv_paint_btn.clicked.connect(on_open_rv_paint)
        annotations_popup_btn.clicked.connect(on_open_annotations_popup)
        add_comment_btn.clicked.connect(on_add_comment)
        add_frame_comment_btn.clicked.connect(on_add_frame_comment)

        # Update frame info periodically
        timer = QTimer()
        timer.timeout.connect(update_frame_info)
        timer.start(1000)  # Update every second
        widget.frame_timer = timer

        print("✅ Comments panel created successfully")
        return widget

    except Exception as e:
        print(f"❌ Error creating comments panel: {e}")
        import traceback
        traceback.print_exc()
        return None
