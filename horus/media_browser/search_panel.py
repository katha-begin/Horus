"""
Horus Search Panel
=================

Search panel with Horus project selection and filtering capabilities.
"""

from horus.utils.globals import search_dock, current_project_id, horus_connector
from horus.media_browser.search_handlers import (
    on_project_changed, apply_filters, on_scale_changed, on_media_table_double_click
)


def create_search_panel():
    """Create search panel with Horus project selection."""
    try:
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                       QComboBox, QLineEdit, QPushButton, QTableWidget,
                                       QTableWidgetItem, QHeaderView, QFrame, QSizePolicy)
        from PySide2.QtCore import Qt
        from PySide2.QtGui import QPixmap

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header with project selection
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(5)

        # Project selection
        project_layout = QHBoxLayout()
        project_layout.setSpacing(5)

        project_label = QLabel("Project:")
        project_label.setStyleSheet("font-weight: bold; color: #e0e0e0;")
        project_layout.addWidget(project_label)

        project_combo = QComboBox()
        project_combo.setObjectName("project_combo")
        project_combo.addItems(["Select Project...", "SWA", "Project_B", "Project_C"])
        project_combo.setMinimumWidth(150)
        project_layout.addWidget(project_combo)

        project_layout.addStretch()

        # Scale control
        scale_label = QLabel("Scale:")
        scale_label.setStyleSheet("color: #e0e0e0;")
        project_layout.addWidget(scale_label)

        scale_combo = QComboBox()
        scale_combo.setObjectName("scale_combo")
        scale_combo.addItems(["Small", "Medium", "Large"])
        scale_combo.setCurrentText("Small")
        scale_combo.setMaximumWidth(80)
        project_layout.addWidget(scale_combo)

        header_layout.addLayout(project_layout)

        # Filter controls
        filter_frame = QFrame()
        filter_layout = QVBoxLayout(filter_frame)
        filter_layout.setContentsMargins(0, 5, 0, 5)
        filter_layout.setSpacing(5)

        # First row of filters
        filter_row1 = QHBoxLayout()
        filter_row1.setSpacing(5)

        # Department filter
        dept_label = QLabel("Dept:")
        dept_label.setMinimumWidth(40)
        dept_label.setStyleSheet("color: #e0e0e0;")
        filter_row1.addWidget(dept_label)

        dept_combo = QComboBox()
        dept_combo.setObjectName("dept_combo")
        dept_combo.addItems(["All", "Animation", "Lighting", "Compositing", "FX", "Modeling"])
        dept_combo.setMinimumWidth(100)
        filter_row1.addWidget(dept_combo)

        # Episode filter
        episode_label = QLabel("Ep:")
        episode_label.setMinimumWidth(25)
        episode_label.setStyleSheet("color: #e0e0e0;")
        filter_row1.addWidget(episode_label)

        episode_combo = QComboBox()
        episode_combo.setObjectName("episode_combo")
        episode_combo.addItems(["All", "EP01", "EP02", "EP03"])
        episode_combo.setMinimumWidth(70)
        filter_row1.addWidget(episode_combo)

        # Sequence filter
        sequence_label = QLabel("Seq:")
        sequence_label.setMinimumWidth(30)
        sequence_label.setStyleSheet("color: #e0e0e0;")
        filter_row1.addWidget(sequence_label)

        sequence_combo = QComboBox()
        sequence_combo.setObjectName("sequence_combo")
        sequence_combo.addItems(["All", "SQ0010", "SQ0020", "SQ0030"])
        sequence_combo.setMinimumWidth(80)
        filter_row1.addWidget(sequence_combo)

        filter_row1.addStretch()
        filter_layout.addLayout(filter_row1)

        # Second row of filters
        filter_row2 = QHBoxLayout()
        filter_row2.setSpacing(5)

        # Shot filter
        shot_label = QLabel("Shot:")
        shot_label.setMinimumWidth(40)
        shot_label.setStyleSheet("color: #e0e0e0;")
        filter_row2.addWidget(shot_label)

        shot_combo = QComboBox()
        shot_combo.setObjectName("shot_combo")
        shot_combo.addItems(["All"])
        shot_combo.setMinimumWidth(100)
        filter_row2.addWidget(shot_combo)

        # Text search
        search_label = QLabel("Search:")
        search_label.setMinimumWidth(50)
        search_label.setStyleSheet("color: #e0e0e0;")
        filter_row2.addWidget(search_label)

        search_text = QLineEdit()
        search_text.setObjectName("search_text")
        search_text.setPlaceholderText("Search files...")
        filter_row2.addWidget(search_text)

        # Apply button
        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("apply_btn")
        apply_btn.setMaximumWidth(60)
        filter_row2.addWidget(apply_btn)

        filter_layout.addLayout(filter_row2)
        header_layout.addWidget(filter_frame)
        layout.addWidget(header_frame)

        # Media table
        table = QTableWidget()
        table.setObjectName("media_table")
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Thumbnail", "Task Entity", "Name", "Version", "Department", "Created"
        ])

        # Configure table
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setSortingEnabled(True)
        table.verticalHeader().setVisible(False)

        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Thumbnail
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Task Entity
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(3, QHeaderView.Fixed)   # Version
        header.setSectionResizeMode(4, QHeaderView.Fixed)   # Department
        header.setSectionResizeMode(5, QHeaderView.Fixed)   # Created

        table.setColumnWidth(0, 80)   # Thumbnail
        table.setColumnWidth(3, 80)   # Version
        table.setColumnWidth(4, 100)  # Department
        table.setColumnWidth(5, 120)  # Created

        # Set row height based on scale
        table.setRowHeight(0, 60)  # Default small scale

        layout.addWidget(table)

        # Store references
        widget.project_combo = project_combo
        widget.scale_combo = scale_combo
        widget.dept_combo = dept_combo
        widget.episode_combo = episode_combo
        widget.sequence_combo = sequence_combo
        widget.shot_combo = shot_combo
        widget.search_text = search_text
        widget.apply_btn = apply_btn
        widget.media_table = table

        # Connect signals
        project_combo.currentTextChanged.connect(on_project_changed)
        scale_combo.currentTextChanged.connect(on_scale_changed)
        apply_btn.clicked.connect(apply_filters)
        table.itemDoubleClicked.connect(on_media_table_double_click)

        # Auto-apply filters when dropdowns change
        dept_combo.currentTextChanged.connect(apply_filters)
        episode_combo.currentTextChanged.connect(apply_filters)
        sequence_combo.currentTextChanged.connect(apply_filters)
        shot_combo.currentTextChanged.connect(apply_filters)

        print("✅ Search panel created successfully")
        return widget

    except Exception as e:
        print(f"❌ Error creating search panel: {e}")
        import traceback
        traceback.print_exc()
        return None
