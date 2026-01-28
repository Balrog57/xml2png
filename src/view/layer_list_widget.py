from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
from PyQt6.QtCore import pyqtSignal, Qt

class LayerListItem(QFrame):
    """A single item in the layer list with an eye toggle button."""
    visibility_changed = pyqtSignal(int, bool)  # (index, is_visible)
    clicked = pyqtSignal(int)  # index
    
    def __init__(self, index: int, name: str, is_visible: bool = True, parent=None):
        super().__init__(parent)
        self.index = index
        self._is_selected = False
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 3, 5, 3)
        
        # Eye button - subtle like Photoshop
        self.btn_eye = QPushButton()
        self.btn_eye.setFixedSize(20, 20)
        self.btn_eye.setCheckable(True)
        self.btn_eye.setChecked(is_visible)
        self.btn_eye.setToolTip("Toggle visibility")
        self._update_eye_style()
        self.btn_eye.clicked.connect(self._on_eye_clicked)
        
        # Layer name
        self.lbl_name = QLabel(name)
        
        layout.addWidget(self.btn_eye)
        layout.addWidget(self.lbl_name, 1)
        
        self._update_selection_style()
    
    def _on_eye_clicked(self):
        self._update_eye_style()
        self.visibility_changed.emit(self.index, self.btn_eye.isChecked())
    
    def _update_eye_style(self):
        if self.btn_eye.isChecked():
            # Visible: filled circle
            self.btn_eye.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid #888;
                    border-radius: 10px;
                }
                QPushButton::after {
                    background-color: #aaa;
                }
            """)
            self.btn_eye.setText("●")
        else:
            # Hidden: empty circle
            self.btn_eye.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 2px solid #555;
                    border-radius: 10px;
                    color: #555;
                }
            """)
            self.btn_eye.setText("")
    
    def set_visible_state(self, is_visible: bool):
        self.btn_eye.blockSignals(True)
        self.btn_eye.setChecked(is_visible)
        self._update_eye_style()
        self.btn_eye.blockSignals(False)
    
    def set_selected(self, selected: bool):
        self._is_selected = selected
        self._update_selection_style()
    
    def _update_selection_style(self):
        if self._is_selected:
            self.setStyleSheet("LayerListItem { background-color: #0078d7; }")
            self.lbl_name.setStyleSheet("color: white; font-weight: bold;")
        else:
            self.setStyleSheet("LayerListItem { background-color: transparent; }")
            self.lbl_name.setStyleSheet("")
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self.index)


class LayerListWidget(QWidget):
    """Widget to display a list of layers with visibility toggles."""
    layer_selected = pyqtSignal(int)
    layer_visibility_changed = pyqtSignal(int, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._selected_index = -1
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Scroll area for layers
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(2, 2, 2, 2)
        self._container_layout.setSpacing(2)
        self._container_layout.addStretch()
        
        scroll.setWidget(self._container)
        layout.addWidget(scroll)
    
    def set_layers(self, layer_names: list, visibilities: list):
        """Initialize or reset the layer list."""
        # Clear existing
        for item in self._items:
            item.setParent(None)
            item.deleteLater()
        self._items.clear()
        
        # Create new items - Background at top, then layers in order (1, 2, 3...)
        for i, (name, vis) in enumerate(zip(layer_names, visibilities)):
            item = LayerListItem(i, name, vis)
            item.clicked.connect(self._on_item_clicked)
            item.visibility_changed.connect(self._on_visibility_changed)
            self._container_layout.insertWidget(self._container_layout.count() - 1, item)  # Before stretch
            self._items.append(item)
        
        # Select first by default
        if self._items:
            self.select_layer(0)
    
    def _on_item_clicked(self, index: int):
        self.select_layer(index)
        self.layer_selected.emit(index)
    
    def _on_visibility_changed(self, index: int, is_visible: bool):
        self.layer_visibility_changed.emit(index, is_visible)
    
    def select_layer(self, index: int):
        self._selected_index = index
        for item in self._items:
            item.set_selected(item.index == index)
    
    def update_visibility(self, index: int, is_visible: bool):
        """Update the eye state for a specific layer."""
        for item in self._items:
            if item.index == index:
                item.set_visible_state(is_visible)
                break
