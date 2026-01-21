from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QPushButton, QMessageBox)
from typing import List
from ..models.data_source import MessageMapping
from .message_mapping_dialog import MessageMappingDialog

class MappingListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.mappings: List[MessageMapping] = []
        self.dbc_path = ""
        
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Message Mapping")
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = QPushButton("Delete")
        
        self.btn_add.clicked.connect(self.add_mapping)
        self.btn_edit.clicked.connect(self.edit_mapping)
        self.btn_delete.clicked.connect(self.delete_mapping)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def set_mappings(self, mappings: List[MessageMapping]):
        self.mappings = mappings # Direct ref? Better copy? keeping ref logic simple for now
        self.refresh_list()

    def get_mappings(self) -> List[MessageMapping]:
        return self.mappings

    def load_dbc(self, path: str):
        self.dbc_path = path

    def refresh_list(self):
        self.list_widget.clear()
        for m in self.mappings:
            self.list_widget.addItem(f"ID/PGN: {m.identifier} ({len(m.fields)} fields)")

    def add_mapping(self):
        dialog = MessageMappingDialog(self, dbc_path=self.dbc_path)
        if dialog.exec():
            self.mappings.append(dialog.get_mapping())
            self.refresh_list()

    def edit_mapping(self):
        row = self.list_widget.currentRow()
        if row < 0: return
        
        dialog = MessageMappingDialog(self, encoding_mapping=self.mappings[row], dbc_path=self.dbc_path)
        if dialog.exec():
            self.mappings[row] = dialog.get_mapping()
            self.refresh_list()

    def delete_mapping(self):
        row = self.list_widget.currentRow()
        if row < 0: return
        del self.mappings[row]
        self.refresh_list()
