from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox, QLabel, QHBoxLayout

class IOConfigManager(QWidget):
    def __init__(self, config_store):
        super().__init__()
        self.config_store = config_store
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Manage Configuration Import/Export"))
        
        btn_layout = QHBoxLayout()
        self.btn_import = QPushButton("Import Configuration")
        self.btn_import.clicked.connect(self.import_config)
        btn_layout.addWidget(self.btn_import)
        
        self.btn_export = QPushButton("Export Configuration")
        self.btn_export.clicked.connect(self.export_config)
        btn_layout.addWidget(self.btn_export)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        self.setLayout(layout)

    def import_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Config", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                self.config_store.load_from_file(file_path)
                # We should probably notify other widgets to refresh?
                # ConfigStore could emit an event. Or widgets refresh on show.
                QMessageBox.information(self, "Success", "Configuration imported successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import configuration: {e}")

    def export_config(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Config", "config.json", "JSON Files (*.json);;All Files (*)")
        if file_path:
            try:
                self.config_store.save_to_file(file_path)
                QMessageBox.information(self, "Success", "Configuration exported successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export configuration: {e}")
