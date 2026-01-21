from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QDialogButtonBox, QLabel, QWidget, QHBoxLayout, QPushButton, QFileDialog)
from PySide6.QtCore import Qt
from ..models.convertor import Convertor
from .data_source_editor import DataSourceEditor
from .convert_rules_editor import ConvertRulesEditor

class ConvertorDialog(QDialog):
    def __init__(self, parent=None, convertor: Convertor = None):
        super().__init__(parent)
        self.setWindowTitle("Convertor Editor")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        self.name_edit = QLineEdit()
        
        folder_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(self.btn_browse)
        
        if convertor:
            self.name_edit.setText(convertor.name)
            self.folder_edit.setText(convertor.result_folder)
            
        form.addRow("Name:", self.name_edit)
        form.addRow("Result Folder:", folder_layout)
        layout.addLayout(form)
        
        # Data Source Editor
        self.ds_editor = DataSourceEditor(convertor.data_source if convertor else None)
        layout.addWidget(QLabel("Data Source Settings:"))
        layout.addWidget(self.ds_editor)
        
        # Convert Rules Editor
        self.rules_editor = ConvertRulesEditor(convertor.convert_rules if convertor else [])
        layout.addWidget(QLabel("Convert Rules:"))
        layout.addWidget(self.rules_editor)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Result Folder")
        if folder:
            self.folder_edit.setText(folder)

    def get_convertor(self) -> Convertor:
        c = Convertor(
            name=self.name_edit.text(),
            result_folder=self.folder_edit.text()
        )
        c.data_source = self.ds_editor.get_data_source()
        c.convert_rules = self.rules_editor.get_rules()
        return c
