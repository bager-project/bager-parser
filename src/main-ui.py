# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Entry file with UI

import colorama
import os
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSizePolicy,
    QSpinBox, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QIcon
import sys
import toml

from embedder.embedder import *
from extractor.dxf import *
from extractor.image import *
from positioner.positioner import *
from separator.separator import *

import ui.DocumentationEditor as de

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

        separator = Separator(elements, parsed_toml[section_name]['debug'], 
                              parsed_toml[section_name]['grid_size'], 
                              parsed_toml[section_name]['min_spacing'])
        separator.execute()
        polygons, grids = separator.get_shapes()

        positioner = Positioner(parsed_toml[section_name]['position_path'],
                                parsed_toml[section_name]['depth'], polygons, grids)
        positioner.execute()
        transformed_polygons, transformed_grids = positioner.get_elements()

        embedder = Embedder(transformed_polygons, transformed_grids, parsed_toml, section_name)
        embedder.execute()
        embedder.plot_polygons()

class MainWindow(QWidget):
    """
        Class managing all of the widgets on the window.
    """

    def __init__(self, config_path):
        """
            Run the main window.
        """

        super().__init__()

        self.config_path = config_path

        self.setWindowTitle("B.A.G.E.R. - Main Window")

        layout = QVBoxLayout()

        self.title = QLabel("B.A.G.E.R. - Main Window")
        self.title.setStyleSheet("font-size: 48px; font-weight: bold; color: #333;")
        self.title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.title)

        script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of main-ui.py
        icon_path = os.path.join(script_dir, "ui", "icons", "play.png")

        self.run_parser_button = QPushButton("Run B.A.G.E.R. parser")
        self.run_parser_button.setIcon(QIcon(icon_path))
        self.run_parser_button.clicked.connect(self.run_parser)
        layout.addWidget(self.run_parser_button)

        icon_path = os.path.join(script_dir, "ui", "icons", "edit.png")

        self.open_de_button = QPushButton("Open Documentation Editor")
        self.open_de_button.setIcon(QIcon(icon_path))
        self.open_de_button.clicked.connect(lambda: windowDE.show())
        layout.addWidget(self.open_de_button)

        self.about_button = QPushButton("About B.A.G.E.R.")
        self.about_button.setIcon(QIcon(os.path.join(script_dir, "ui", "icons", "info.png")))
        self.about_button.clicked.connect(self.show_about)
        layout.addWidget(self.about_button)

        self.version_label = QLabel("B.A.G.E.R. Software Suite Version: v0.4.0")
        self.version_label.setStyleSheet("font-size: 16px; color: #666;")
        self.version_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.version_label)

        self.setLayout(layout)
        self.setFixedSize(650, 200)

    def show_about(self):
        """
            Shows the about dialog.
        """
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.NoIcon)
        msg_box.setWindowTitle("About B.A.G.E.R.")
        msg_box.setText("B.A.G.E.R. Software Suite\nVersion: v0.4.0\nAuthor: Andrej Bartulin\nUI Development: NotNekodev\nDiscord Server: https://discord.gg/zyzbdrDRQF")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def run_parser(self):
        """
            Run the parser, same as `main.py`.
        """

        if not os.path.exists(self.config_path):
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText(f"File in path '{config_path}' has not been found!\n" +
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
        msg_box.setText("No config file path was provided!\n" +
                        "This may be result in unintended behavior," +
                        "if you are sure that this is correct," +
                        "you may ignore this warning.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
        msg_box.exec()

    window = MainWindow(config_path)
    window.show()

    windowDE = de.DEWindow(config_path)
    # windowDE.show()
    app.exec()
