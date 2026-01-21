from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from .home_page import HomePage
from .config_page import ConfigPage
from ..core.config_store import ConfigStore

class MainWindow(QMainWindow):
    def __init__(self, config_store: ConfigStore):
        super().__init__()
        self.setWindowTitle("CAN Data Parser")
        self.resize(800, 600)
        self.config_store = config_store
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Navigation Bar
        self.nav_bar = QHBoxLayout()
        self.btn_home = QPushButton("Home")
        self.btn_config = QPushButton("Configuration")
        
        self.btn_home.clicked.connect(self.show_home)
        self.btn_config.clicked.connect(self.show_config)
        
        self.nav_bar.addWidget(self.btn_home)
        self.nav_bar.addWidget(self.btn_config)
        self.nav_bar.addStretch()
        
        self.main_layout.addLayout(self.nav_bar)
        
        # Stacked Pages
        self.stacked_widget = QStackedWidget()
        self.home_page = HomePage(self.config_store)
        self.config_page = ConfigPage(self.config_store)
        
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.config_page)
        
        self.main_layout.addWidget(self.stacked_widget)
        
        self.show_home()

    def show_home(self):
        self.stacked_widget.setCurrentWidget(self.home_page)
        self.btn_home.setEnabled(False)
        self.btn_config.setEnabled(True)

    def show_config(self):
        self.stacked_widget.setCurrentWidget(self.config_page)
        self.btn_home.setEnabled(True)
        self.btn_config.setEnabled(False)
