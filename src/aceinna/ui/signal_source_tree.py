from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PySide6.QtCore import Qt, QMimeData
from typing import List, Dict

class SignalSourceTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderLabel("Available Signals")
        self.setSelectionMode(QAbstractItemView.ExtendedSelection) # Allow multiple selection
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        
    def populate(self, grouped_signals: Dict[str, List[str]]):
        self.clear()
        for group_name, signals in grouped_signals.items():
            parent = QTreeWidgetItem(self)
            parent.setText(0, group_name)
            parent.setFlags(parent.flags() & ~Qt.ItemIsDragEnabled) # Disable dragging for group
            
            for sig in sorted(signals):
                child = QTreeWidgetItem(parent)
                child.setText(0, sig)
                child.setFlags(child.flags() | Qt.ItemIsDragEnabled)

    def mimeData(self, items):
        mime_data = QMimeData()
        if items:
            # We only support dragging one item or multiple? 
            # The requirement says "User could drag multiple signals", so let's check selection mode
            texts = [item.text(0) for item in items if item.parent()] # Only signals, not groups
            mime_data.setText("\n".join(texts)) 
            # We use plain text for simplicity: "SignalName"
        return mime_data
