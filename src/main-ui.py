# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Entry file with UI

import colorama
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QLineEdit,
    QMessageBox, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QSizePolicy, QFileDialog
)
import sys
import toml

from embedder.embedder import *
from extractor.dxf import *
from extractor.image import *
from positioner.positioner import *
from separator.separator import *


def merge_dicts(d1, d2):
    """
        Merge two dictionaries.
    """

    for key, value in d2.items():
        if (
            key in d1
            and isinstance(d1[key], dict)
            and isinstance(value, dict)
        ):
            merge_dicts(d1[key], value)
        else:
            d1[key] = value


def parse(parsed_toml, section_name):
    """
        Parse (run extractor, separator, positioner and embedder) each
        TOML section in `config.toml`.
    """

    extractor = None

    match parsed_toml[section_name]['parser_type']:
        case "dxf":
            extractor = DXF(parsed_toml[section_name]['path'])

        case "image":
            extractor = Image(parsed_toml[section_name]['path'])

        case _:
            pass

    if extractor != None:
        extractor.extract_entities()
        elements = extractor.get_elements()

        separator = Separator(elements)
        separator.execute()
        polygons, grids = separator.get_shapes()

        positioner = Positioner(parsed_toml[section_name]['position_path'],
                                parsed_toml[section_name]['depth'], polygons, grids)
        positioner.execute()
        transformed_polygons, transformed_grids = positioner.get_elements()

        embedder = Embedder(transformed_polygons,
                            transformed_grids, parsed_toml, section_name)
        embedder.execute()
        embedder.plot_polygons()


class ConfigWidget(QWidget):
    """
        Class managing all of the widgets on the window.
    """

    def __init__(self, config_path):
        """
            Initialize all the variables.
        """

        super().__init__()

        self.config_path = config_path

        self.setWindowTitle("B.A.G.E.R. parser - config window")
        self.init_ui()

    def browse_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a file")
        if file_path:
            self.path_input.setText(file_path)
            print(file_path)

    def init_ui(self):
        """
            Run the UI.
        """

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Section name
        layout.addWidget(QLabel("Section name:"))
        self.section_name_input = QLineEdit()
        self.section_name_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.section_name_input)

        # Parser type
        layout.addWidget(QLabel("Parser Type:"))
        self.parser_combo = QComboBox()
        self.parser_combo.addItems(["dxf", "image", "GIS"])
        self.parser_combo.setCurrentText("dxf")
        self.parser_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.parser_combo)

        # Path
        # layout.addWidget(QLabel("Path:"))
        # self.path_input = QLineEdit()
        # self.path_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # layout.addWidget(self.path_input)

        layout.addWidget(QLabel("Path:"))

        # Create a container widget to hold QLineEdit + button horizontally
        path_container = QWidget()
        path_layout = QHBoxLayout()
        # no margins for tight packing
        path_layout.setContentsMargins(0, 0, 0, 0)
        path_container.setLayout(path_layout)

        self.path_input = QLineEdit()
        self.path_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        path_layout.addWidget(self.path_input)

        browse_button = QPushButton("...")
        browse_button.setFixedWidth(30)
        browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_button)

        layout.addWidget(path_container)

        # Position path
        layout.addWidget(QLabel("Position Path:"))
        self.position_input = QLineEdit()
        self.position_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.position_input)

        # Depth
        layout.addWidget(QLabel("Depths:"))
        self.depths_input = QLineEdit()
        self.depths_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.depths_input)

        # Hole checkbox
        self.hole_checkbox = QCheckBox("Hole")
        self.hole_checkbox.setChecked(True)
        self.hole_checkbox.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.hole_checkbox)

        # Append config button
        self.append_button = QPushButton("Append section")
        self.append_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.append_button.clicked.connect(self.append_config)
        layout.addWidget(self.append_button)

        # Print config button
        self.print_button = QPushButton("Print config")
        self.print_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.print_button.clicked.connect(self.print_config)
        layout.addWidget(self.print_button)

        # Run parser button
        self.run_button = QPushButton("Run parser")
        self.run_button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.run_button.clicked.connect(self.run_parser)
        layout.addWidget(self.run_button)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

    def append_config(self):
        """
            Append the new section in `config.toml`
        """

        if self.section_name_input.text() == "":
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText(
                f"Section name is necessary, even in empty sections!")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
            msg_box.exec()

            return

        depths_array = []
        if self.depths_input.text() != "":
            depths_array = list(map(int, self.depths_input.text().split(',')))

        dictionary = {
            "parser_type": self.parser_combo.currentText(),
            "path": self.path_input.text(),
            "position_path": self.position_input.text(),
            "depth": depths_array,
            "hole": self.hole_checkbox.isChecked()
        }

        new_section = {self.section_name_input.text(): dictionary}

        # ---------------------------------------------------------------------

        if not os.path.exists(self.config_path):
            existing_data = {}

            self.config_path = "config.toml"
            with open(self.config_path, "a+") as file:
                pass

        with open(self.config_path, "r") as file:
            existing_data = toml.load(file)

        merge_dicts(existing_data, new_section)

        with open(self.config_path, "w") as file:
            toml.dump(existing_data, file)

    def print_config(self):
        if not os.path.exists(self.config_path):
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText(f"File in path '{config_path}' not found!\n" +
                            f"Appending a section will create a new file.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
            msg_box.exec()

            return

        parsed_toml = toml.load(self.config_path)
        print(colorama.Fore.LIGHTRED_EX +
              "B.A.G.E.R. parser" + colorama.Fore.RESET)

        for key, value in parsed_toml.items():
            print(key, value)

    def run_parser(self):
        """
            Run the parser, same as `main.py`.
        """

        if not os.path.exists(self.config_path):
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText(f"File in path '{config_path}' not found!\n" +
                            f"Appending a section will create a new file.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
            msg_box.exec()

            return

        parsed_toml = toml.load(self.config_path)
        print(colorama.Fore.LIGHTRED_EX +
              "B.A.G.E.R. parser" + colorama.Fore.RESET)
        
        window.hide()

        # Loop through each TOML section and parse it
        for key, value in parsed_toml.items():
            if isinstance(value, dict):
                parse(parsed_toml, key)


if __name__ == "__main__":
    config_path: str = ""
    config_found = False

    app = QApplication(sys.argv)

    if len(sys.argv) >= 2:
        config_path = sys.argv[1]
    else:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Warning")
        msg_box.setText("No config file path was provided!\n"+
                        "This may be unintended behavior, if you are sure that this is correct, may ignore this warning.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
        msg_box.exec()

    window = ConfigWidget(config_path)
    window.show()
    app.exec()
