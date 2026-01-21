from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                               QSpinBox, QDoubleSpinBox, QCheckBox, QHBoxLayout, 
                               QListWidget, QPushButton, QLabel, QInputDialog)
from ..models.convert_rule import PlotRule, AxisBinding

class PlotRuleEditor(QWidget):
    def __init__(self, rule: PlotRule = None):
        super().__init__()
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.x_axis_edit = QLineEdit() # Binding name
        
        if rule:
            self.title_edit.setText(rule.title)
            if rule.x_axis:
                self.x_axis_edit.setText(rule.x_axis.binding)
                
        form.addRow("Title:", self.title_edit)
        form.addRow("X Axis Binding (Empty for Index):", self.x_axis_edit)
        
        layout.addLayout(form)
        
        # Y Axes
        layout.addWidget(QLabel("Y Axis Bindings:"))
        self.y_list = QListWidget()
        layout.addWidget(self.y_list)
        
        y_btn_layout = QHBoxLayout()
        self.btn_add_y = QPushButton("Add")
        self.btn_del_y = QPushButton("Delete")
        self.btn_add_y.clicked.connect(self.add_y)
        self.btn_del_y.clicked.connect(self.del_y)
        y_btn_layout.addWidget(self.btn_add_y)
        y_btn_layout.addWidget(self.btn_del_y)
        layout.addLayout(y_btn_layout)
        
        if rule:
            for y in rule.y_axes:
                self.y_list.addItem(y.binding)

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
        layout.addWidget(QLabel("Styles:"))
        layout.addWidget(style_group)
        
        self.setLayout(layout)

    def _h_layout(self, widgets):
        w = QWidget()
        l = QHBoxLayout()
        l.setContentsMargins(0,0,0,0)
        for widget in widgets:
            l.addWidget(widget)
        w.setLayout(l)
        return w

    def add_y(self):
        binding, ok = QInputDialog.getText(self, "Add Y Axis", "Binding Name:")
        if ok and binding:
            self.y_list.addItem(binding)

    def del_y(self):
        row = self.y_list.currentRow()
        if row >= 0:
            self.y_list.takeItem(row)

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
