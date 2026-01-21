from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QPushButton, QLineEdit, QFileDialog, 
                               QProgressBar, QMessageBox)
from PySide6.QtCore import Qt
from ..core.convert_engine import ConvertWorker

class HomePage(QWidget):
    def __init__(self, config_store):
        super().__init__()
        self.config_store = config_store
        self.process = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 1. Select Convertor
        self.combo_convertor = QComboBox()
        layout.addWidget(QLabel("Select Convertor:"))
        layout.addWidget(self.combo_convertor)
        
        # 2. Select Data File Mapping
        self.combo_mapping = QComboBox()
        layout.addWidget(QLabel("Select Data File Mapping:"))
        layout.addWidget(self.combo_mapping)
        
        # 3. Data File Selection
        file_layout = QHBoxLayout()
        self.line_file_path = QLineEdit()
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self.browse_file)
        file_layout.addWidget(self.line_file_path)
        file_layout.addWidget(self.btn_browse)
        
        layout.addWidget(QLabel("Source Data File:"))
        layout.addLayout(file_layout)
        
        # 4. Buttons
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.start_process)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.cancel_process)
        self.btn_cancel.setEnabled(False)
        
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        
        # 5. Status
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        self.setLayout(layout)

    def showEvent(self, event):
        self.refresh_lists()
        super().showEvent(event)

    def refresh_lists(self):
        # Convertors
        current_conv = self.combo_convertor.currentText()
        self.combo_convertor.clear()
        for c in self.config_store.convertors:
            self.combo_convertor.addItem(c.name, c)
        
        # Restore selection
        index = self.combo_convertor.findText(current_conv)
        if index >= 0:
            self.combo_convertor.setCurrentIndex(index)
            
        # Mappings
        current_map = self.combo_mapping.currentText()
        self.combo_mapping.clear()
        for m in self.config_store.fetch_rules:
            self.combo_mapping.addItem(m.name, m)
            
        index = self.combo_mapping.findText(current_map)
        if index >= 0:
            self.combo_mapping.setCurrentIndex(index)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Data File", "", "Data Files (*.xlsx *.csv);;All Files (*)")
        if file_path:
            self.line_file_path.setText(file_path)

    def start_process(self):
        convertor = self.combo_convertor.currentData()
        mapping = self.combo_mapping.currentData()
        file_path = self.line_file_path.text()
        
        if not convertor:
            QMessageBox.warning(self, "Error", "Please select a Convertor.")
            return
        if not mapping:
            QMessageBox.warning(self, "Error", "Please select a Data File Mapping.")
            return
        if not file_path:
            QMessageBox.warning(self, "Error", "Please select a Source Data File.")
            return

        self.process = ConvertWorker(convertor, mapping, file_path)
        self.process.progress_update.connect(self.update_progress)
        self.process.finished_signal.connect(self.on_process_finished)
        self.process.error_signal.connect(self.on_process_error)
        
        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.combo_convertor.setEnabled(False)
        self.combo_mapping.setEnabled(False)
        
        self.process.start()

    def cancel_process(self):
        if self.process:
            self.process.cancel()

    def update_progress(self, message, percent):
        self.status_label.setText(message)
        self.progress_bar.setValue(percent)

    def on_process_finished(self):
        self._reset_ui()
        if self.progress_bar.value() < 100:
             self.status_label.setText("Stopped.")

    def on_process_error(self, msg):
        self._reset_ui()
        QMessageBox.critical(self, "Error", msg)

    def _reset_ui(self):
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.combo_convertor.setEnabled(True)
        self.combo_mapping.setEnabled(True)
