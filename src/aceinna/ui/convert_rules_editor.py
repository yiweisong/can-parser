from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QPushButton, QMessageBox, QDialog, QComboBox, 
                               QDialogButtonBox, QStackedWidget)
from typing import List
from ..models.convert_rule import ConvertRule, PlotRule, DataListRule
from .plot_rule_editor import PlotRuleEditor
from .datalist_rule_editor import DataListRuleEditor

class ConvertRulesEditor(QWidget):
    def __init__(self, rules: List[ConvertRule]):
        super().__init__()
        self.rules = rules
        
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
        for i, rule in enumerate(self.rules):
            if rule.type == 'plot':
                self.list_widget.addItem(f"{i+1}. [Plot] {rule.title}")
            else:
                self.list_widget.addItem(f"{i+1}. [DataList] {len(rule.fields)} fields")

    def get_rules(self) -> List[ConvertRule]:
        return self.rules

    def add_rule(self):
        # Ask for type
        dialog = RuleTypeDialog(self)
        if dialog.exec():
            rtype = dialog.get_type()
            if rtype == 'plot':
                editor = PlotRuleDialog(self)
                if editor.exec():
                    self.rules.append(editor.get_rule())
            else:
                editor = DataListRuleDialog(self)
                if editor.exec():
                    self.rules.append(editor.get_rule())
            self.refresh_list()

    def edit_rule(self):
        row = self.list_widget.currentRow()
        if row < 0: return
        
        rule = self.rules[row]
        if rule.type == 'plot':
            editor = PlotRuleDialog(self, rule)
        else:
            editor = DataListRuleDialog(self, rule)
            
        if editor.exec():
            self.rules[row] = editor.get_rule()
            self.refresh_list()

    def delete_rule(self):
        row = self.list_widget.currentRow()
        if row < 0: return
        
        if QMessageBox.question(self, "Delete", "Are you sure?") == QMessageBox.Yes:
            del self.rules[row]
            self.refresh_list()

class RuleTypeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Rule Type")
        layout = QVBoxLayout()
        self.combo = QComboBox()
        self.combo.addItems(['plot', 'data_list'])
        layout.addWidget(self.combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_type(self):
        return self.combo.currentText()
        
# Placeholder for specific editors, need to be implemented in separate files or here
# Using classes imported (which I need to create)
class PlotRuleDialog(QDialog):
     def __init__(self, parent=None, rule=None):
        super().__init__(parent)
        self.setWindowTitle("Plot Rule")
        self.resize(600, 400)
        self.editor = PlotRuleEditor(rule)
        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)
        
     def get_rule(self):
         return self.editor.get_rule()

class DataListRuleDialog(QDialog):
     def __init__(self, parent=None, rule=None):
        super().__init__(parent)
        self.setWindowTitle("Data List Rule")
        self.editor = DataListRuleEditor(rule)
        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)
        
     def get_rule(self):
         return self.editor.get_rule()
