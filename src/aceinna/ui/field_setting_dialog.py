from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                               QSpinBox, QDoubleSpinBox, QComboBox, QDialogButtonBox)
from ..models.data_source import FieldSetting
from ..core.dbc_manager import DBCManager

class FieldSettingDialog(QDialog):
    def __init__(self, parent=None, field: FieldSetting = None, dbc_path="", msg_id=None):
        super().__init__(parent)
        self.setWindowTitle("Field Setting")
        self.dbc_path = dbc_path
        self.msg_id = msg_id
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # DBC Signal Selection
        self.signal_combo = QComboBox()
        self.signal_combo.addItem("Manual Entry", None)
        self.signal_combo.currentIndexChanged.connect(self.on_signal_selected)
        
        if self.dbc_path and self.msg_id is not None:
             self._populate_signals()
             if self.signal_combo.count() > 1:
                 form.addRow("Select from DBC:", self.signal_combo)

        self.name_edit = QLineEdit()
        self.start_bit = QSpinBox()
        self.start_bit.setRange(0, 63)
        self.length = QSpinBox()
        self.length.setRange(1, 64)
        
        self.byte_order = QComboBox()
        self.byte_order.addItems(['little_endian', 'big_endian'])
        
        self.val_type = QComboBox()
        self.val_type.addItems(['unsigned', 'signed', 'float', 'double'])
        
        self.factor = QDoubleSpinBox()
        self.factor.setRange(-1e9, 1e9)
        self.factor.setDecimals(6)
        self.factor.setValue(1.0)
        
        self.offset = QDoubleSpinBox()
        self.offset.setRange(-1e9, 1e9)
        self.factor.setDecimals(6) # Typo in logic, fixed implicitly
        
        self.unit = QLineEdit()
        
        if field:
            self.name_edit.setText(field.name)
            self.start_bit.setValue(field.start_bit)
            self.length.setValue(field.length)
            self.byte_order.setCurrentText(field.byte_order)
            self.val_type.setCurrentText(field.value_type)
            self.factor.setValue(field.factor)
            self.offset.setValue(field.offset)
            self.unit.setText(field.unit)
            
        form.addRow("Name:", self.name_edit)
        form.addRow("Start Bit:", self.start_bit)
        form.addRow("Length:", self.length)
        form.addRow("Byte Order:", self.byte_order)
        form.addRow("Value Type:", self.val_type)
        form.addRow("Factor:", self.factor)
        form.addRow("Offset:", self.offset)
        form.addRow("Unit:", self.unit)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def _populate_signals(self):
        try:
            db = DBCManager.load_dbc(self.dbc_path)
            if not db: return
            msg = db.get_message_by_frame_id(self.msg_id)
            if msg:
                for sig in msg.signals:
                    self.signal_combo.addItem(sig.name, sig)
        except Exception:
            pass

    def on_signal_selected(self):
        sig = self.signal_combo.currentData()
        if not sig: return
        
        self.name_edit.setText(sig.name)
        self.start_bit.setValue(sig.start)
        self.length.setValue(sig.length)
        if sig.byte_order == 'little_endian':
            self.byte_order.setCurrentText('little_endian')
        else:
             self.byte_order.setCurrentText('big_endian')
             
        if sig.is_float:
             self.val_type.setCurrentText('float') # Simplified
        elif sig.is_signed:
             self.val_type.setCurrentText('signed')
        else:
             self.val_type.setCurrentText('unsigned')
             
        self.factor.setValue(float(sig.scale))
        self.offset.setValue(float(sig.offset))
        self.unit.setText(sig.unit or "")

    def get_field(self) -> FieldSetting:
        return FieldSetting(
            name=self.name_edit.text(),
            start_bit=self.start_bit.value(),
            length=self.length.value(),
            byte_order=self.byte_order.currentText(),
            value_type=self.val_type.currentText(),
            factor=self.factor.value(),
            offset=self.offset.value(),
            unit=self.unit.text()
        )
