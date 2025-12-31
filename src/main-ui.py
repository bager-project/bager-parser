# AUTHOR Andrej Bartulin, NotNekodev
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Entry file with UI

import colorama
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,QLabel, QMessageBox, QPushButton,
    QSizePolicy,QVBoxLayout, QWidget
)
import sys
import toml

from embedder.embedder import *
from extractor.dxf import *
from extractor.gis import *
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

def parse_section(parsed_toml, section_name):
    """
        Parse (run extractor, separator, positioner and embedder) a TOML section.
        
        :param dict parsed_toml: parsed contents of the TOML file
        :param str section_name: name of the section to be parsed 
    """

    extractor = None

    match parsed_toml[section_name]['parser_type']:
        case "dxf":
            extractor = DXF(parsed_toml[section_name]['path'])

        case "image":
            extractor = Image(parsed_toml[section_name]['path'],
                              parsed_toml[section_name]['debug'],
                              parsed_toml[section_name]['flip_y'],
                              parsed_toml[section_name]['simplify_tolerance'],
                              parsed_toml[section_name]['remove_colinear'])

        case "GIS":
            extractor = GIS(parsed_toml[section_name]['path'])

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

        positioner = Positioner(parsed_toml[section_name]['coords'],
                                parsed_toml[section_name]['depth'],
                                parsed_toml[section_name]['scale'],
                                polygons, grids)
        positioner.execute()
        transformed_polygons, transformed_grids = positioner.get_elements()

        embedder = Embedder(transformed_polygons, transformed_grids, parsed_toml, section_name)
        embedder.execute()
        embedder.plot_polygons()

class MainWindow(QWidget):
    """
        Class for the main window.
        :param str config_path: path to the config file
    """

    def __init__(self, config_path):
        """
            Run the main window.
        """

        super().__init__()

        self.config_path = config_path

        self.setWindowTitle("B.A.G.E.R. - Main Window")

        layout = QVBoxLayout()

        self.title = QLabel("B.A.G.E.R. parser")
        self.title.setStyleSheet("font-size: 48px; font-weight: bold; color: #333;")
        self.title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        self.run_parser_button = QPushButton("Run B.A.G.E.R. parser")
        self.run_parser_button.clicked.connect(self.run_parser)
        layout.addWidget(self.run_parser_button)

        self.open_de_button = QPushButton("Open documentation editor")
        self.open_de_button.clicked.connect(lambda: windowDE.show())
        layout.addWidget(self.open_de_button)

        self.about_button = QPushButton("About B.A.G.E.R.")
        self.about_button.clicked.connect(self.show_about)
        layout.addWidget(self.about_button)

        self.version_label = QLabel("B.A.G.E.R. parser v0.4.4")
        self.version_label.setStyleSheet("font-size: 15px; color: #666;")
        self.version_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.version_label)

        self.setLayout(layout)
        self.setFixedSize(650, 200)

    def show_about(self):
        """
            Show the about dialog.
        """
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.NoIcon)
        msg_box.setWindowTitle("About B.A.G.E.R.")
        msg_box.setText("B.A.G.E.R. (Basic Autonomous Ground Excavation Robot)" +
                        " is an autonomous excavator robot featuring a full" +
                        " project documentation parser.\n" +
                        "For more information, check out" +
                        " main GitHub page: https://github.com/bager-project")
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
                parse_section(parsed_toml, key)

if __name__ == "__main__":
    config_path: str = ""

    app = QApplication(sys.argv)

    if len(sys.argv) >= 2:
        config_path = sys.argv[1]

    else:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Warning")
        msg_box.setText("There was no project documentation file provided!\n" +
                        "If this is intended behavior, because you want to" +
                        " create a new project, please disregard this message.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
        msg_box.exec()

    window = MainWindow(config_path)
    window.show()

    windowDE = de.DEWindow(config_path)
    app.exec()
