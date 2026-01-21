from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                               QCheckBox, QHBoxLayout, QListWidget, QPushButton, 
                               QLabel, QInputDialog)
from ..models.convert_rule import DataListRule, DataListField

class DataListRuleEditor(QWidget):
    def __init__(self, rule: DataListRule = None):
        super().__init__()
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.delimiter = QLineEdit()
        self.delimiter.setText(",")
        self.header = QCheckBox("Include Header")
        self.header.setChecked(True)
        
        if rule:
            self.delimiter.setText(rule.delimiter)
            self.header.setChecked(rule.include_header)
            
        form.addRow("Delimiter:", self.delimiter)
        form.addRow("Header:", self.header)
        layout.addLayout(form)
        
        # Fields
        layout.addWidget(QLabel("Fields:"))
        self.field_list = QListWidget()
        layout.addWidget(self.field_list)
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_del = QPushButton("Delete")
        self.btn_add.clicked.connect(self.add_field)
        self.btn_del.clicked.connect(self.del_field)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_del)
        layout.addLayout(btn_layout)
        
        if rule:
            for f in rule.fields:
                self.field_list.addItem(f.binding)
        
        self.setLayout(layout)

    def add_field(self):
        binding, ok = QInputDialog.getText(self, "Add Field", "Binding Name:")
        if ok and binding:
            self.field_list.addItem(binding)

    def del_field(self):
        row = self.field_list.currentRow()
        if row >= 0:
            self.field_list.takeItem(row)

    def get_rule(self) -> DataListRule:
        rule = DataListRule(
            delimiter=self.delimiter.text(),
            include_header=self.header.isChecked()
        )
        fields = []
        for i in range(self.field_list.count()):
            fields.append(DataListField(binding=self.field_list.item(i).text()))
        rule.fields = fields
        
        return rule
