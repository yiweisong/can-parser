from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                               QSpinBox, QDoubleSpinBox, QCheckBox, QHBoxLayout, 
                               QListWidget, QPushButton, QLabel, QInputDialog, QComboBox, 
                               QSplitter, QAbstractItemView)
from PySide6.QtCore import Qt
from ..models.convert_rule import PlotRule, AxisBinding
from .signal_source_tree import SignalSourceTree

class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setPlaceholderText("Drag signal here or type")

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        text = event.mimeData().text()
        # Takes the first line if multiple
        if "\n" in text:
            text = text.split("\n")[0]
        self.setText(text)
        event.acceptProposedAction()

class DropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        text = event.mimeData().text()
        for line in text.split("\n"):
            if line.strip():
                # Check for duplicates? Or allow?
                # Ideally we want unique bindings per list usually, but let's just add
                self.addItem(line.strip())
        event.acceptProposedAction()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
             self._delete_selected()
        else:
            super().keyPressEvent(event)
            
    def _delete_selected(self):
        for item in self.selectedItems():
            self.takeItem(self.row(item))

class PlotRuleEditor(QWidget):
    def __init__(self, rule: PlotRule = None, available_signals_grouped: dict = None):
        super().__init__()
        self.available_signals_grouped = available_signals_grouped or {}
        
        main_layout = QVBoxLayout()
        
        # 1. Title
        form = QFormLayout()
        self.title_edit = QLineEdit()
        if rule:
            self.title_edit.setText(rule.title)
        form.addRow("Title:", self.title_edit)
        main_layout.addLayout(form)
        
        # 2. Binding Area (Splitter)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Signal Tree
        self.tree = SignalSourceTree()
        self.tree.populate(self.available_signals_grouped)
        splitter.addWidget(self.tree)
        
        # Right: Binding Controls
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # X Axis
        x_group = QWidget()
        x_layout = QVBoxLayout()
        x_layout.addWidget(QLabel("X Axis Binding (Drag here):"))
        self.x_axis_edit = DropLineEdit()
        if rule and rule.x_axis:
            self.x_axis_edit.setText(rule.x_axis.binding)
        x_layout.addWidget(self.x_axis_edit)
        x_group.setLayout(x_layout)
        right_layout.addWidget(x_group)
        
        # Y Axis
        y_group = QWidget()
        y_layout = QVBoxLayout()
        y_layout.addWidget(QLabel("Y Axis Bindings (Drag here):"))
        self.y_list = DropListWidget()
        self.y_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        if rule:
            for y in rule.y_axes:
                self.y_list.addItem(y.binding)
        y_layout.addWidget(self.y_list)
        
        # Helper buttons for Y Axis (Delete, Up, Down)
        btn_layout = QHBoxLayout()
        btn_del = QPushButton("Delete Selected Y")
        btn_del.clicked.connect(self.y_list._delete_selected)
        
        btn_up = QPushButton("Up")
        btn_up.clicked.connect(self.move_up)
        btn_down = QPushButton("Down")
        btn_down.clicked.connect(self.move_down)
        
        btn_layout.addWidget(btn_del)
        btn_layout.addWidget(btn_up)
        btn_layout.addWidget(btn_down)
        y_layout.addLayout(btn_layout)
        
        y_group.setLayout(y_layout)
        right_layout.addWidget(y_group)
        
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        # Set splitter sizes (30% tree, 70% controls)
        splitter.setSizes([200, 400])
        
        main_layout.addWidget(splitter)

        # Style Settings (Simplified)
        style_group = QWidget()
        style_form = QFormLayout()
        self.fig_w = QDoubleSpinBox()
        self.fig_w.setValue(6.4)
        self.fig_h = QDoubleSpinBox()
        self.fig_h.setValue(4.8)
        self.dpi = QSpinBox()
        self.dpi.setValue(160)
        
        if rule:
            self.fig_w.setValue(rule.figure_figsize[0])
            self.fig_h.setValue(rule.figure_figsize[1])
            self.dpi.setValue(rule.figure_dpi)
            
        style_form.addRow("Figure Config (W, H, DPI):", self._h_layout([self.fig_w, self.fig_h, self.dpi]))
        style_group.setLayout(style_form)
        main_layout.addWidget(QLabel("Styles:"))
        main_layout.addWidget(style_group)
        
        self.setLayout(main_layout)

    def move_up(self):
        row = self.y_list.currentRow()
        if row <= 0: return
        item = self.y_list.takeItem(row)
        self.y_list.insertItem(row-1, item)
        self.y_list.setCurrentRow(row-1)

    def move_down(self):
        row = self.y_list.currentRow()
        if row < 0 or row >= self.y_list.count() - 1: return
        item = self.y_list.takeItem(row)
        self.y_list.insertItem(row+1, item)
        self.y_list.setCurrentRow(row+1)

    def _h_layout(self, widgets):
        w = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(0,0,0,0)
        for widget in widgets:
            l.addWidget(widget)
        w.setLayout(l)
        return w

    def get_rule(self) -> PlotRule:
        rule = PlotRule(
            title=self.title_edit.text(),
            figure_figsize=(self.fig_w.value(), self.fig_h.value()),
            figure_dpi=self.dpi.value()
        )
        if self.x_axis_edit.text():
            rule.x_axis = AxisBinding(binding=self.x_axis_edit.text())
        
        y_bindings = []
        for i in range(self.y_list.count()):
            y_bindings.append(AxisBinding(binding=self.y_list.item(i).text()))
        rule.y_axes = y_bindings
        
        return rule
