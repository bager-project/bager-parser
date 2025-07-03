# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Entry file with UI

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QLineEdit,
    QVBoxLayout, QCheckBox, QPushButton, QSizePolicy
)

import sys

class ConfigWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("B.A.G.E.R. parser - config window")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Parser type
        layout.addWidget(QLabel("Parser Type:"))
        self.parser_combo = QComboBox()
        self.parser_combo.addItems(["dxf", "image", "GIS"])
        self.parser_combo.setCurrentText("dxf")
        self.parser_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.parser_combo)

        # Path
        layout.addWidget(QLabel("Path:"))
        self.path_input = QLineEdit()
        self.path_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.path_input)

        # Position path
        layout.addWidget(QLabel("Position Path:"))
        self.position_input = QLineEdit()
        self.position_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.position_input)

        # Depth
        layout.addWidget(QLabel("Depths:"))
        self.path_input = QLineEdit()
        self.path_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.path_input)

        # Hole checkbox
        self.hole_checkbox = QCheckBox("Hole")
        self.hole_checkbox.setChecked(True)
        self.hole_checkbox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.hole_checkbox)

        # Button
        self.save_button = QPushButton("Append section")
        self.save_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.save_button.clicked.connect(self.append_config)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def append_config(self):
        pass

if __name__ == "__main__":
    config_path: str = ""

    if len(sys.argv) >= 2:
        config_path = sys.argv[1]

    app = QApplication(sys.argv)
    window = ConfigWidget()
    window.show()
    app.exec()
