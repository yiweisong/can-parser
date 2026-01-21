from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QComboBox, QSpinBox, QDialogButtonBox)
from ..models.fetch_rule import DataSourceFetchRule

class FetchRuleDialog(QDialog):
    def __init__(self, parent=None, rule: DataSourceFetchRule = None):
        super().__init__(parent)
        self.setWindowTitle("Data File Mapping")
        self.rule = rule
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(['xlsx', 'csv'])
        
        self.msg_id_col = QSpinBox()
        self.msg_id_col.setRange(0, 100)
        self.msg_data_col = QSpinBox()
        self.msg_data_col.setRange(0, 100)
        self.time_col = QSpinBox()
        self.time_col.setRange(0, 100)
        
        if rule:
            self.name_edit.setText(rule.name)
            self.type_combo.setCurrentText(rule.file_type)
            self.msg_id_col.setValue(rule.message_id_col_index)
            self.msg_data_col.setValue(rule.message_data_col_index)
            self.time_col.setValue(rule.timestamp_col_index)
            
        form.addRow("Name:", self.name_edit)
        form.addRow("File Type:", self.type_combo)
        form.addRow("Message ID Column Index:", self.msg_id_col)
        form.addRow("Message Data Column Index:", self.msg_data_col)
        form.addRow("Timestamp Column Index:", self.time_col)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def get_rule(self) -> DataSourceFetchRule:
        return DataSourceFetchRule(
            name=self.name_edit.text(),
            file_type=self.type_combo.currentText(),
            message_id_col_index=self.msg_id_col.value(),
            message_data_col_index=self.msg_data_col.value(),
            timestamp_col_index=self.time_col.value()
        )
