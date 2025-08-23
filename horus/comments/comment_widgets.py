"""
Horus Comment Widgets
====================

Individual comment and reply widget creation and management.
"""


def create_comment_widget(comment_data):
    """Create a threaded comment widget following Facebook/Slack patterns."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                       QPushButton, QFrame, QLineEdit, QTextEdit)
        from PySide2.QtCore import Qt
        from PySide2.QtGui import QFont

        # Main comment container
        comment_widget = QWidget()
        comment_layout = QVBoxLayout(comment_widget)
        comment_layout.setContentsMargins(0, 0, 0, 0)
        comment_layout.setSpacing(4)

        # Comment header with user info
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 6, 8, 4)
        header_layout.setSpacing(8)

        # User avatar (circular)
        avatar_label = QLabel(comment_data.get("avatar", "??"))
        avatar_label.setFixedSize(32, 32)
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet("""
            QLabel {
                background-color: #0078d4;
                color: white;
                border-radius: 16px;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        header_layout.addWidget(avatar_label)

        # User info container
        user_info_layout = QVBoxLayout()
        user_info_layout.setSpacing(2)

        # Username and timestamp
        user_time_layout = QHBoxLayout()
        user_time_layout.setSpacing(8)

        username_label = QLabel(comment_data.get("user", "Unknown User"))
        username_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 11px;")
        user_time_layout.addWidget(username_label)

        time_label = QLabel(comment_data.get("time", ""))
        time_label.setStyleSheet("color: #888888; font-size: 10px;")
        user_time_layout.addWidget(time_label)

        user_time_layout.addStretch()
        user_info_layout.addLayout(user_time_layout)

        # Frame info if present
        frame_number = comment_data.get("frame")
        if frame_number:
            frame_label = QLabel(f"🎬 Frame {frame_number}")
            frame_label.setStyleSheet("color: #ffa500; font-size: 10px; font-weight: bold;")
            user_info_layout.addWidget(frame_label)

        # Status and priority for frame comments
        status = comment_data.get("status")
        priority = comment_data.get("priority")
        if status or priority:
            status_layout = QHBoxLayout()
            status_layout.setSpacing(8)
            
            if status:
                status_label = QLabel(f"Status: {status}")
                status_label.setStyleSheet("color: #888888; font-size: 9px;")
                status_layout.addWidget(status_label)
            
            if priority:
                priority_color = {"High": "#ff4444", "Medium": "#ffaa00", "Low": "#44ff44"}.get(priority, "#888888")
                priority_label = QLabel(f"Priority: {priority}")
                priority_label.setStyleSheet(f"color: {priority_color}; font-size: 9px; font-weight: bold;")
                status_layout.addWidget(priority_label)
            
            status_layout.addStretch()
            user_info_layout.addLayout(status_layout)

        header_layout.addLayout(user_info_layout)
        comment_layout.addWidget(header_frame)

        # Comment text
        text_label = QLabel(comment_data.get("text", ""))
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 11px;
                padding: 4px 8px 8px 48px;
                line-height: 1.4;
            }
        """)
        comment_layout.addWidget(text_label)

        # Action buttons (likes, reply)
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(48, 0, 8, 4)
        actions_layout.setSpacing(12)

        # Like button with count
        likes_count = comment_data.get("likes", 0)
        like_btn = QPushButton(f"👍 {likes_count}" if likes_count > 0 else "👍")
        like_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #888888;
                font-size: 10px;
                padding: 2px 4px;
            }
            QPushButton:hover {
                color: #0078d4;
                background-color: rgba(0, 120, 212, 0.1);
                border-radius: 2px;
            }
        """)
        actions_layout.addWidget(like_btn)

        # Reply button
        reply_btn = QPushButton("💬 Reply")
        reply_btn.setObjectName(f"reply_btn_{comment_data.get('id', 0)}")
        reply_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #888888;
                font-size: 10px;
                padding: 2px 4px;
            }
            QPushButton:hover {
                color: #0078d4;
                background-color: rgba(0, 120, 212, 0.1);
                border-radius: 2px;
            }
        """)
        actions_layout.addWidget(reply_btn)

        # Resolve button for frame comments
        if frame_number:
            resolve_btn = QPushButton("✅ Resolve")
            resolve_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #44ff44;
                    font-size: 10px;
                    padding: 2px 4px;
                }
                QPushButton:hover {
                    background-color: rgba(68, 255, 68, 0.1);
                    border-radius: 2px;
                }
            """)
            actions_layout.addWidget(resolve_btn)

        actions_layout.addStretch()
        comment_layout.addWidget(actions_frame)

        # Reply input area (initially hidden)
        reply_input_frame = QFrame()
        reply_input_frame.setObjectName(f"reply_input_{comment_data.get('id', 0)}")
        reply_input_frame.setVisible(False)
        reply_input_layout = QVBoxLayout(reply_input_frame)
        reply_input_layout.setContentsMargins(48, 4, 8, 8)

        reply_text = QTextEdit()
        reply_text.setObjectName(f"reply_text_{comment_data.get('id', 0)}")
        reply_text.setPlaceholderText("Write a reply...")
        reply_text.setMaximumHeight(50)
        reply_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px;
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-size: 10px;
            }
        """)
        reply_input_layout.addWidget(reply_text)

        reply_buttons_layout = QHBoxLayout()
        reply_buttons_layout.setSpacing(4)

        post_reply_btn = QPushButton("Post")
        post_reply_btn.setObjectName(f"post_reply_{comment_data.get('id', 0)}")
        post_reply_btn.setStyleSheet("font-size: 9px; padding: 2px 6px;")
        reply_buttons_layout.addWidget(post_reply_btn)

        cancel_reply_btn = QPushButton("Cancel")
        cancel_reply_btn.setObjectName(f"cancel_reply_{comment_data.get('id', 0)}")
        cancel_reply_btn.setStyleSheet("font-size: 9px; padding: 2px 6px;")
        reply_buttons_layout.addWidget(cancel_reply_btn)

        reply_buttons_layout.addStretch()
        reply_input_layout.addLayout(reply_buttons_layout)
        comment_layout.addWidget(reply_input_frame)

        # Replies container
        replies_container = QWidget()
        replies_container.setObjectName(f"replies_{comment_data.get('id', 0)}")
        replies_layout = QVBoxLayout(replies_container)
        replies_layout.setContentsMargins(0, 0, 0, 0)
        replies_layout.setSpacing(4)

        # Add existing replies
        replies = comment_data.get("replies", [])
        for reply_data in replies:
            reply_widget = create_reply_widget(reply_data)
            replies_layout.addWidget(reply_widget)

        comment_layout.addWidget(replies_container)

        # Connect reply button to show/hide input
        from horus.comments.comment_handlers import show_reply_input, hide_reply_input, post_reply
        reply_btn.clicked.connect(lambda: show_reply_input(comment_data.get('id', 0)))
        cancel_reply_btn.clicked.connect(lambda: hide_reply_input(comment_data.get('id', 0)))
        post_reply_btn.clicked.connect(lambda: post_reply(comment_data.get('id', 0)))

        # Store references
        comment_widget.reply_input_frame = reply_input_frame
        comment_widget.replies_container = replies_container

        return comment_widget

    except Exception as e:
        print(f"Error creating comment widget: {e}")
        from PySide2.QtWidgets import QWidget
        return QWidget()


def create_reply_widget(reply_data):
    """Create a reply widget with indentation."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                       QPushButton, QFrame)
        from PySide2.QtCore import Qt

        # Reply container with left margin for threading
        reply_widget = QWidget()
        reply_layout = QVBoxLayout(reply_widget)
        reply_layout.setContentsMargins(24, 4, 0, 4)  # Left indent for threading
        reply_layout.setSpacing(2)

        # Reply header
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(8, 4, 8, 2)
        header_layout.setSpacing(6)

        # Smaller avatar for replies
        avatar_label = QLabel(reply_data.get("avatar", "??"))
        avatar_label.setFixedSize(24, 24)
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet("""
            QLabel {
                background-color: #666666;
                color: white;
                border-radius: 12px;
                font-weight: bold;
                font-size: 9px;
            }
        """)
        header_layout.addWidget(avatar_label)

        # User and time
        username_label = QLabel(reply_data.get("user", "Unknown User"))
        username_label.setStyleSheet("font-weight: bold; color: #e0e0e0; font-size: 10px;")
        header_layout.addWidget(username_label)

        time_label = QLabel(reply_data.get("time", ""))
        time_label.setStyleSheet("color: #888888; font-size: 9px;")
        header_layout.addWidget(time_label)

        header_layout.addStretch()
        reply_layout.addWidget(header_frame)

        # Reply text
        text_label = QLabel(reply_data.get("text", ""))
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 10px;
                padding: 2px 8px 4px 32px;
                line-height: 1.3;
            }
        """)
        reply_layout.addWidget(text_label)

        # Reply actions (smaller)
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(32, 0, 8, 2)
        actions_layout.setSpacing(8)

        # Like button for reply
        likes_count = reply_data.get("likes", 0)
        like_btn = QPushButton(f"👍 {likes_count}" if likes_count > 0 else "👍")
        like_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #888888;
                font-size: 9px;
                padding: 1px 3px;
            }
            QPushButton:hover {
                color: #0078d4;
                background-color: rgba(0, 120, 212, 0.1);
                border-radius: 2px;
            }
        """)
        actions_layout.addWidget(like_btn)

        actions_layout.addStretch()
        reply_layout.addWidget(actions_frame)

        return reply_widget

    except Exception as e:
        print(f"Error creating reply widget: {e}")
        from PySide2.QtWidgets import QWidget
        return QWidget()
