from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from .convertor_manager import ConvertorManager
from .fetch_rule_manager import FetchRuleManager
from .io_config_manager import IOConfigManager

class ConfigPage(QWidget):
    def __init__(self, config_store):
        super().__init__()
        self.config_store = config_store
        
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        
        self.convertor_manager = ConvertorManager(config_store)
        self.fetch_rule_manager = FetchRuleManager(config_store)
        self.io_manager = IOConfigManager(config_store)
        
        self.tabs.addTab(self.convertor_manager, "Convertors")
        self.tabs.addTab(self.fetch_rule_manager, "Data File Mappings")
        self.tabs.addTab(self.io_manager, "Import/Export")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
