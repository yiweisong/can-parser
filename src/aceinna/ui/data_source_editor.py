from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox, 
                               QLineEdit, QPushButton, QHBoxLayout, QFileDialog)
from PySide6.QtCore import Qt
from ..models.data_source import DataSource, CommonCANDataSource, J1939DataSource
from .mapping_list_widget import MappingListWidget

class DataSourceEditor(QWidget):
    def __init__(self, data_source: DataSource = None):
        super().__init__()
        layout = QVBoxLayout()
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(['common_can', 'j1939'])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        
        dbc_layout = QHBoxLayout()
        self.dbc_path_edit = QLineEdit()
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self.browse_dbc)
        dbc_layout.addWidget(self.dbc_path_edit)
        dbc_layout.addWidget(self.btn_browse)
        
        form.addRow("Type:", self.type_combo)
        form.addRow("DBC File:", dbc_layout)
        
        layout.addLayout(form)
        
        # Mapping List
        self.mapping_widget = MappingListWidget()
        layout.addWidget(self.mapping_widget)
        
        # J1939 distinct fields
        self.sa_filter_widget = QWidget()
        sa_layout = QHBoxLayout()
        self.sa_edit = QLineEdit()
        sa_layout.addWidget(self.sa_edit)
        self.sa_filter_widget.setLayout(sa_layout)
        
        self.sa_form = QFormLayout()
        self.sa_form.addRow("Source Filters (comma sep):", self.sa_edit)
        layout.addLayout(self.sa_form)
        
        self.setLayout(layout)
        
        if data_source:
            self.type_combo.setCurrentText(data_source.type)
            self.dbc_path_edit.setText(data_source.dbc_file_path)
            
            # Auto-load DBC for mapping widget so it can populate signals
            if data_source.dbc_file_path:
                self.mapping_widget.load_dbc(data_source.dbc_file_path)

            if data_source.type == 'common_can':
                self.mapping_widget.set_mappings(data_source.message_mappings)
                self.sa_filter_widget.hide()
            elif data_source.type == 'j1939':
                self.mapping_widget.set_mappings(data_source.pgn_mappings)
                self.sa_edit.setText(", ".join([f"0x{sa:X}" for sa in data_source.source_address_filters]))
                self.sa_filter_widget.show()
        else:
            self.on_type_changed() # Trigger default visibility

    def on_type_changed(self):
        t = self.type_combo.currentText()
        if t == 'common_can':
            self.sa_filter_widget.hide()
        else:
            self.sa_filter_widget.show()

    def browse_dbc(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select DBC", "", "DBC Files (*.dbc);;All Files (*)")
        if path:
            self.dbc_path_edit.setText(path)
            self.mapping_widget.load_dbc(path) # Notify mapping widget to load DBC for dropdowns

    def get_data_source(self) -> DataSource:
        t = self.type_combo.currentText()
        path = self.dbc_path_edit.text()
        mappings = self.mapping_widget.get_mappings()
        
        if t == 'common_can':
            return CommonCANDataSource(
                name="DataSource", # Generic
                dbc_file_path=path,
                message_mappings=mappings
            )
        else:
            sa_str = self.sa_edit.text()
            sas = []
            for s in sa_str.split(','):
                s = s.strip()
                if not s: continue
                try:
                    if s.lower().startswith('0x'):
                        sas.append(int(s, 16))
                    else:
                        sas.append(int(s))
                except ValueError:
                    pass # Ignore invalid inputs
            return J1939DataSource(
                name="DataSource",
                dbc_file_path=path,
                pgn_mappings=mappings,
                source_address_filters=sas
            )
