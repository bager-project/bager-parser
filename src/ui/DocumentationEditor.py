import os
import toml
from PyQt6.QtWidgets import (
    QWidget, QTableView, QVBoxLayout, QHBoxLayout,
    QStyledItemDelegate, QComboBox, QLineEdit, QFileDialog,
    QSpinBox, QDoubleSpinBox, QPushButton, QSizePolicy,
    QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt6.QtGui import QIcon

class DETableModel(QAbstractTableModel):
    headers = [
        "Section Name", "Parser Type", "File Path", "Position File Path",
        "Depth", "Hole?", "Debug?", "Grid Size", "Min Spacing"
    ]
    parser_types = ["dxf", "Image", "GIS"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()
        row, col = index.row(), index.column()
        value = self._data[row][col]
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if isinstance(value, bool):
                return "" if role == Qt.ItemDataRole.DisplayRole else value
            return value
        if role == Qt.ItemDataRole.CheckStateRole:
            if isinstance(value, bool):
                return Qt.CheckState.Checked if value else Qt.CheckState.Unchecked
        return QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        col = index.column()
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
        if col in [5, 6]:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        row, col = index.row(), index.column()
        if col in [5, 6]:
            if role == Qt.ItemDataRole.CheckStateRole:
                self._data[row][col] = (value == Qt.CheckState.Checked)
                self.dataChanged.emit(index, index)
                return True
        if role == Qt.ItemDataRole.EditRole:
            if col == 1 and value in self.parser_types:
                self._data[row][col] = value
            elif col in [2, 3, 4]:
                self._data[row][col] = value
            elif col == 7:
                try:
                    ivalue = int(value)
                    self._data[row][col] = ivalue
                except ValueError:
                    return False
            elif col == 8:
                try:
                    fvalue = float(value)
                    self._data[row][col] = fvalue
                except ValueError:
                    return False
            elif col == 0:
                self._data[row][col] = value
            else:
                self._data[row][col] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def addRow(self, section_name="NewSection", type="dxf", file_path="", position_file_path="",
               depth="[0]", hole=False, debug=False, grid_size=0, min_spacing=0.0):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        new_row = [section_name, type, file_path, position_file_path, depth, hole, debug, grid_size, min_spacing]
        self._data.append(new_row)
        self.endInsertRows()

    def removeRow(self, row):
        if 0 <= row < self.rowCount():
            self.beginRemoveRows(QModelIndex(), row, row)
            self._data.pop(row)
            self.endRemoveRows()
            return True
        return False

class DEDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        col = index.column()
        model = index.model()
        if col == 0:
            return QLineEdit(parent)
        if col == 1:
            combo = QComboBox(parent)
            combo.addItems(model.parser_types)
            return combo
        if col in [2, 3]:
            editor_widget = QWidget(parent)
            layout = QHBoxLayout(editor_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(2)
            line_edit = QLineEdit(editor_widget)
            line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button = QPushButton("...", editor_widget)
            button.setFixedWidth(30)
            button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            layout.addWidget(line_edit)
            layout.addWidget(button)
            layout.setStretch(0, 1)
            layout.setStretch(1, 0)
            button.clicked.connect(lambda: self.open_file_dialog(line_edit, index))
            return editor_widget
        if col == 4:
            return QLineEdit(parent)
        if col in [5, 6]:
            return None
        if col == 7:
            spin = QSpinBox(parent)
            spin.setMinimum(0)
            spin.setMaximum(1000000)
            return spin
        if col == 8:
            double_spin = QDoubleSpinBox(parent)
            double_spin.setDecimals(3)
            double_spin.setMinimum(0.0)
            double_spin.setMaximum(1e9)
            return double_spin
        return super().createEditor(parent, option, index)

    def open_file_dialog(self, line_edit, index):
        file_path, _ = QFileDialog.getOpenFileName(line_edit, "Select File")
        if file_path:
            model = index.model()
            model.setData(index, file_path, Qt.ItemDataRole.EditRole)
            line_edit.setText(file_path)
            self.commitData.emit(line_edit)
            self.closeEditor.emit(line_edit, QStyledItemDelegate.EndEditHint.NoHint)
        else:
            self.closeEditor.emit(line_edit, QStyledItemDelegate.EndEditHint.NoHint)

    def setEditorData(self, editor, index):
        col = index.column()
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        if col == 0 and isinstance(editor, QLineEdit):
            editor.setText(str(value) if value else "")
        elif col == 1 and isinstance(editor, QComboBox):
            idx = editor.findText(value)
            if idx >= 0:
                editor.setCurrentIndex(idx)
        elif col in [2, 3] and isinstance(editor, QWidget):
            line_edit = editor.findChild(QLineEdit)
            if line_edit:
                line_edit.setText(str(value) if value else "")
        elif col == 4 and isinstance(editor, QLineEdit):
            editor.setText(str(value) if value else "")
        elif col == 7 and isinstance(editor, QSpinBox):
            editor.setValue(int(value) if value else 0)
        elif col == 8 and isinstance(editor, QDoubleSpinBox):
            editor.setValue(float(value) if value else 0.0)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        col = index.column()
        if col == 0 and isinstance(editor, QLineEdit):
            model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)
        elif col == 1 and isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)
        elif col in [2, 3] and isinstance(editor, QWidget):
            line_edit = editor.findChild(QLineEdit)
            if line_edit:
                model.setData(index, line_edit.text(), Qt.ItemDataRole.EditRole)
        elif col == 4 and isinstance(editor, QLineEdit):
            model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)
        elif col == 7 and isinstance(editor, QSpinBox):
            model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)
        elif col == 8 and isinstance(editor, QDoubleSpinBox):
            model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)
        else:
            super().setModelData(editor, model, index)

    def editorEvent(self, event, model, option, index):
        col = index.column()
        if col in [5, 6]:
            if event.type() == event.Type.MouseButtonRelease:
                current = model.data(index, Qt.ItemDataRole.CheckStateRole)
                new_val = Qt.CheckState.Unchecked if current == Qt.CheckState.Checked else Qt.CheckState.Checked
                model.setData(index, new_val, Qt.ItemDataRole.CheckStateRole)
                return True
        return super().editorEvent(event, model, option, index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class DEWindow(QWidget):
    def __init__(self, config_file):
        super().__init__()
        self.setWindowTitle("B.A.G.E.R. - Project Documentation Editor")
        self.config_path = config_file
        self.local_config = {}
        self.changed_config = False
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as file:
                self.local_config = toml.load(file)
        else:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Error Loading Existing Project Documentation")
            msg_box.setText("Documentation File not found!")
            if self.config_path == "":
                msg_box.setInformativeText("No documentation file was specified. Please create a new one or specify an existing one.")
            else:
                msg_box.setInformativeText(f"Documentation file '{self.config_path}' not found. Please create a new one or specify an existing one.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
        layout = QVBoxLayout(self)
        self.table = QTableView()
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.model = DETableModel()
        self.table.setModel(self.model)
        self.delegate = DEDelegate()
        self.table.setItemDelegate(self.delegate)
        self.table.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.SelectedClicked)
        layout.addWidget(self.table)
        self.load_toml_to_table(self.local_config)
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Documentation Entry")
        self.remove_button = QPushButton("Remove Documentation Entry")
        self.save_button = QPushButton("Save Documentation Entries")
        self.close_button = QPushButton("Close Editor")
        self.add_button.clicked.connect(self.add_section)
        self.remove_button.clicked.connect(self.remove_section)
        self.save_button.clicked.connect(self.save_config)
        self.close_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.remove_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.close_button)
        layout.addLayout(self.button_layout)

    def add_section(self):
        self.model.addRow()
        self.changed_config = True

    def remove_section(self):
        self.model.removeRow(self.table.currentIndex().row())
        self.changed_config = True

    def load_toml_to_table(self, parsed_toml):
        for section_name, values in parsed_toml.items():
            row_data = [
                section_name,
                values.get('parser_type', 'dxf'),
                values.get('path', ''),
                values.get('position_path', ''),
                str(values.get('depth', '[0]')),
                values.get('hole', False),
                values.get('debug', False),
                values.get('grid_size', 0),
                values.get('min_spacing', 0.0)
            ]
            self.model.beginInsertRows(QModelIndex(), self.model.rowCount(), self.model.rowCount())
            self.model._data.append(row_data)
            self.model.endInsertRows()

    def save_config(self):
        if not self.config_path:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Error Saving Project Documentation")
            msg_box.setText("No documentation file specified!")
            msg_box.setInformativeText("Please specify a file to save the documentation.")
            open_button = QPushButton("Open")
            open_icon = QIcon.fromTheme("document-open")
            open_button.setIcon(open_icon)
            msg_box.addButton(open_button, QMessageBox.ButtonRole.ActionRole)
            create_button = QPushButton("Create New")
            create_icon = QIcon.fromTheme("document-new")
            create_button.setIcon(create_icon)
            msg_box.addButton(create_button, QMessageBox.ButtonRole.ActionRole)
            discard_button = QPushButton("Close")
            discard_icon = QIcon.fromTheme("dialog-cancel")
            discard_button.setIcon(discard_icon)
            msg_box.addButton(discard_button, QMessageBox.ButtonRole.RejectRole)
            msg_box.setDefaultButton(open_button)
            msg_box.exec()
            clicked = msg_box.clickedButton()
            if clicked == open_button:
                file_path, _ = QFileDialog.getOpenFileName(self, "Open Configuration File", "", "Configuration Files (*.toml)")
                if file_path:
                    self.config_path = file_path
                    self.save_config()
            elif clicked == create_button:
                file_path, _ = QFileDialog.getSaveFileName(self, "Create Configuration File", "", "Configuration Files (*.toml)")
                if file_path:
                    self.config_path = file_path
                    self.save_config()
            return
        new_config = {}
        for row in self.model._data:
            section_name = row[0]
            new_config[section_name] = {
                'parser_type': row[1],
                'path': row[2],
                'position_path': row[3],
                'depth': eval(row[4]) if row[4] else [0],
                'hole': row[5],
                'debug': row[6],
                'grid_size': row[7],
                'min_spacing': row[8]
            }
        self.local_config.update(new_config)
        with open(self.config_path, 'w') as file:
            toml.dump(self.local_config, file)
        self.changed_config = False

    def closeEvent(self, event):
        if self.changed_config:
            confirm_box = QMessageBox()
            confirm_box.setIcon(QMessageBox.Icon.Question)
            confirm_box.setWindowTitle("Discard Changes?")
            confirm_box.setText("Do you want to discard the changes made in the documentation editor?")
            confirm_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            confirm_box.setDefaultButton(QMessageBox.StandardButton.No)
            result = confirm_box.exec()
            if result == QMessageBox.StandardButton.Yes:
                event.accept()
                self.hide()
            else:
                event.ignore()
        else:
            event.accept()
            self.hide()

    def close(self):
        if self.changed_config:
            confirm_box = QMessageBox()
            confirm_box.setIcon(QMessageBox.Icon.Question)
            confirm_box.setWindowTitle("Discard Changes?")
            confirm_box.setText("Do you want to discard the changes made in the documentation editor?")
            confirm_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            confirm_box.setDefaultButton(QMessageBox.StandardButton.No)
            result = confirm_box.exec()
            if result == QMessageBox.StandardButton.Yes:
                self.changed_config = False
                super().close()
                self.hide()
        else:
            self.changed_config = False
            super().close()
            self.hide()