from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QPushButton, QMessageBox)
from typing import List
from ..models.data_source import FieldSetting
from .field_setting_dialog import FieldSettingDialog

class FieldListWidget(QWidget):
    def __init__(self, dbc_path=""):
        super().__init__()
        self.fields: List[FieldSetting] = []
        self.dbc_path = dbc_path
        self.current_msg_id = None
        
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Field")
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = QPushButton("Delete")
        
        self.btn_add.clicked.connect(self.add_field)
        self.btn_edit.clicked.connect(self.edit_field)
        self.btn_delete.clicked.connect(self.delete_field)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def set_fields(self, fields: List[FieldSetting]):
        self.fields = [f for f in fields] # Shallow copy list
        self.refresh_list()
        
    def get_fields(self) -> List[FieldSetting]:
        return self.fields

    def set_current_message_id(self, msg_id):
        self.current_msg_id = msg_id

    def refresh_list(self):
        self.list_widget.clear()
        for f in self.fields:
            self.list_widget.addItem(f"{f.name} (Start: {f.start_bit}, Len: {f.length})")

    def add_field(self):
        dialog = FieldSettingDialog(self, dbc_path=self.dbc_path, msg_id=self.current_msg_id)
        if dialog.exec():
            self.fields.append(dialog.get_field())
            self.refresh_list()

    def edit_field(self):
        row = self.list_widget.currentRow()
        if row < 0: return
        
        dialog = FieldSettingDialog(self, field=self.fields[row], dbc_path=self.dbc_path, msg_id=self.current_msg_id)
        if dialog.exec():
            self.fields[row] = dialog.get_field()
            self.refresh_list()

    def delete_field(self):
        row = self.list_widget.currentRow()
        if row < 0: return
        del self.fields[row]
        self.refresh_list()
