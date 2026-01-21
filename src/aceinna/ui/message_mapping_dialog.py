from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox, 
                               QSpinBox, QDialogButtonBox, QLabel, QWidget)
from ..models.data_source import MessageMapping
from ..core.dbc_manager import DBCManager
from .field_list_widget import FieldListWidget

class MessageMappingDialog(QDialog):
    def __init__(self, parent=None, encoding_mapping: MessageMapping = None, dbc_path: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Message Mapping")
        self.mapping = encoding_mapping
        self.dbc_path = dbc_path
        self.db = None
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # ID selector: Combo (if DBC) or SpinBox
        self.id_combo = QComboBox()
        # self.id_spin = QSpinBox()
        # self.id_spin.setRange(0, 0x1FFFFFFF) # Full 29 bit range
        
        form.addRow("Message ID/PGN:", self.id_combo)
        # form.addRow("Manual ID:", self.id_spin)
        
        layout.addLayout(form)
        
        # Field List
        self.field_widget = FieldListWidget(dbc_path=dbc_path) # Pass DBC path for field selection
        layout.addWidget(QLabel("Fields:"))
        layout.addWidget(self.field_widget)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Load DBC
        self._populate_dbc()
        
        if self.mapping:
            # Set ID
            cid = self.mapping.identifier
            # Match PGN if we have it
            # The combo has full IDs or PGNs depending on DBC.
            # We need to find the item that matches.
            
            found = False
            for i in range(self.id_combo.count()):
                 data = self.id_combo.itemData(i)
                 if data == -1 or data is None: continue
                 
                 fid = int(data)
                 pgn = fid
                 if fid > 0x1FFFF:
                     pgn = (fid >> 8) & 0x1FFFF
                     
                 if pgn == cid or fid == cid:
                     self.id_combo.setCurrentIndex(i)
                     found = True
                     break
            
            # self.id_spin.setValue(self.mapping.identifier)
            self.field_widget.set_fields(self.mapping.fields)
            
        self.id_combo.currentIndexChanged.connect(self.on_combo_changed)

    def _populate_dbc(self):
        if not self.dbc_path:
            self.id_combo.setEnabled(False)
            return
            
        try:
            self.db = DBCManager.load_dbc(self.dbc_path)
            if self.db:
                self.id_combo.addItem("Select from DBC...", -1)
                for msg in self.db.messages:
                    self.id_combo.addItem(f"{msg.name} (0x{msg.frame_id:X})", msg.frame_id)
        except:
            self.id_combo.setEnabled(False)

    def on_combo_changed(self):
        data = self.id_combo.currentData()
        if data and data != -1:
            frame_id = int(data)
            # Try to handle J1939 PGN vs Full ID
            # If > 0x1FFFF, likely a full frame ID, extract PGN
            if frame_id > 0x1FFFF:
                 frame_id = (frame_id >> 8) & 0x1FFFF
            
            # self.id_spin.setValue(frame_id)
            self.field_widget.set_current_message_id(int(data)) # Use original ID to find signals in DBC

    def get_mapping(self) -> MessageMapping:
        data = self.id_combo.currentData()
        frame_id = int(data) if data else 0
        if frame_id > 0x1FFFF:
             frame_id = (frame_id >> 8) & 0x1FFFF
             
        m = MessageMapping(identifier=frame_id)
        m.fields = self.field_widget.get_fields()
        return m
