from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QPushButton, QMessageBox)
from .fetch_rule_dialog import FetchRuleDialog
from ..models.fetch_rule import DataSourceFetchRule

class FetchRuleManager(QWidget):
    def __init__(self, config_store):
        super().__init__()
        self.config_store = config_store
        
        layout = QVBoxLayout()
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = QPushButton("Delete")
        
        self.btn_add.clicked.connect(self.add_rule)
        self.btn_edit.clicked.connect(self.edit_rule)
        self.btn_delete.clicked.connect(self.delete_rule)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for rule in self.config_store.fetch_rules:
            self.list_widget.addItem(rule.name)

    def add_rule(self):
        dialog = FetchRuleDialog(self)
        if dialog.exec():
            new_rule = dialog.get_rule()
            self.config_store.fetch_rules.append(new_rule)
            self.config_store.save()
            self.refresh_list()

    def edit_rule(self):
        row = self.list_widget.currentRow()
        if row < 0: return
        
        rule = self.config_store.fetch_rules[row]
        dialog = FetchRuleDialog(self, rule)
        if dialog.exec():
            updated_rule = dialog.get_rule()
            self.config_store.fetch_rules[row] = updated_rule
            self.config_store.save()
            self.refresh_list()

    def delete_rule(self):
        row = self.list_widget.currentRow()
        if row < 0: return
        
        if QMessageBox.question(self, "Delete", "Are you sure?") == QMessageBox.Yes:
            del self.config_store.fetch_rules[row]
            self.config_store.save()
            self.refresh_list()
