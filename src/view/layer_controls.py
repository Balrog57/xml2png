from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QSpinBox, QCheckBox, QGroupBox, QLineEdit, QPushButton, QSlider, QFormLayout,
    QFileDialog, QColorDialog
)
from PyQt6.QtGui import QColor, QFontDatabase, QAction, QDesktopServices
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
import os

from model.compositor import Layer, LayerType, TextSource

class LayerControlWidget(QWidget):
    # Signal emitted when any parameter changes, sending the updated Layer object
    layer_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_layer = None
        self._block_signals = False
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # -- Layer Type Selection --
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Select Input:"))
        self.combo_type = QComboBox()
        self.combo_type.addItem("None", None)
        self.combo_type.addItem("Text Name (Game Title)", TextSource.NAME)
        self.combo_type.addItem("Text Description", TextSource.DESCRIPTION)
        self.combo_type.addItem("Text Genre", TextSource.GENRE)
        self.combo_type.addItem("Text Year", TextSource.YEAR)
        self.combo_type.addItem("Text Manufacturer", TextSource.MANUFACTURER)
        self.combo_type.addItem("Picture File (Static)", LayerType.IMAGE)
        self.combo_type.addItem("Picture Folder (Variable)", LayerType.IMAGE_FOLDER)
        type_layout.addWidget(self.combo_type)
        layout.addLayout(type_layout)

        # -- File/Folder Input (Dynamic visibility) --
        self.file_group = QGroupBox("Resource Path")
        file_layout = QHBoxLayout()
        # Normal path input
        self.path_input = QLineEdit()
        self.btn_browse = QPushButton("...")
        # Background selector (hidden by default)
        self.combo_bg = QComboBox()
        self.combo_bg.setVisible(False)
        self.btn_open_folder = QPushButton("📂") # Folder icon
        self.btn_open_folder.setToolTip("Open Backgrounds Folder")
        self.btn_open_folder.setVisible(False)
        self.btn_open_folder.setFixedWidth(30)
        
        file_layout.addWidget(self.path_input)
        file_layout.addWidget(self.btn_browse)
        file_layout.addWidget(self.combo_bg)
        file_layout.addWidget(self.btn_open_folder)
        
        self.file_group.setLayout(file_layout)
        layout.addWidget(self.file_group)

        # Text Properties
        self.text_group = QGroupBox("Text Options")
        text_layout = QFormLayout()
        
        self.font_combo = QComboBox()
        self.font_combo.setEditable(True) # Searchable
        # Populate with system fonts
        # In PyQt6 QFontDatabase.families() might need WritingSystem or be an instance method
        # Let's try sticking to "Any" writing system or just standard instantiation
        self.font_combo.addItems(QFontDatabase.families(QFontDatabase.WritingSystem.Any)) 
              
        # Default to Times New Roman if available
        idx = self.font_combo.findText("Times New Roman")
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        else:
             # Try determining a default or leave at 0
             pass
            
        self.font_size = QSpinBox()
        self.font_size.setRange(1, 500)
        self.font_size.setValue(24)
        
        text_layout.addRow("Font:", self.font_combo)
        text_layout.addRow("Size:", self.font_size)
        
        # Color
        self.btn_color = QPushButton("Color: White")
        self.btn_color.clicked.connect(self._pick_color)
        text_layout.addRow("Color:", self.btn_color)
        
        # Alignment
        self.combo_align = QComboBox()
        self.combo_align.addItems(["Left", "Center", "Right"])
        text_layout.addRow("Align:", self.combo_align)
        
        # Max Chars
        self.spin_max_chars = QSpinBox()
        self.spin_max_chars.setRange(0, 9999)
        text_layout.addRow("Max Chars:", self.spin_max_chars)
        
        style_layout = QHBoxLayout()
        self.chk_bold = QCheckBox("Bold")
        self.chk_italic = QCheckBox("Italic")
        self.chk_underline = QCheckBox("Underline")
        style_layout.addWidget(self.chk_bold)
        style_layout.addWidget(self.chk_italic)
        style_layout.addWidget(self.chk_underline)
        text_layout.addRow(style_layout)
        
        # Prefix / Suffix
        self.txt_prefix = QLineEdit()
        self.txt_prefix.setPlaceholderText("Prefix")
        self.txt_suffix = QLineEdit()
        self.txt_suffix.setPlaceholderText("Suffix")
        
        ps_layout = QHBoxLayout()
        ps_layout.addWidget(self.txt_prefix)
        ps_layout.addWidget(self.txt_suffix)
        text_layout.addRow("Pre/Suf:", ps_layout)
        
        # Game Name Option (Specific to Text Name)
        self.chk_use_tag_name = QCheckBox("Use XML <name> tag")
        self.chk_use_tag_name.setToolTip("If checked, use <name> content. If unchecked, use filename.")
        text_layout.addRow(self.chk_use_tag_name)

        self.text_group.setLayout(text_layout)
        layout.addWidget(self.text_group)

        # -- Position & Size --
        self.pos_group = QGroupBox("Dimensions")
        pos_layout = QFormLayout()
        
        self.spin_x = self._create_slider_spin("X", 0, 2000, pos_layout)
        self.spin_y = self._create_slider_spin("Y", 0, 2000, pos_layout)
        self.spin_w = self._create_slider_spin("Width", 0, 2000, pos_layout)
        self.spin_h = self._create_slider_spin("Height", 0, 2000, pos_layout)
        
        self.pos_group.setLayout(pos_layout)
        layout.addWidget(self.pos_group)
        
        layout.addStretch()

        # Connect signals
        # Connect signals
        self.combo_type.currentIndexChanged.connect(self._on_change)
        self.path_input.textChanged.connect(self._on_change)
        self.combo_bg.currentIndexChanged.connect(self._on_change)
        self.btn_browse.clicked.connect(self._on_browse)
        self.btn_open_folder.clicked.connect(self._open_bg_folder)
        self.font_combo.currentTextChanged.connect(self._on_change)
        self.font_size.valueChanged.connect(self._on_change)
        self.combo_align.currentIndexChanged.connect(self._on_change)
        self.spin_max_chars.valueChanged.connect(self._on_change)
        self.chk_bold.toggled.connect(self._on_change)
        self.chk_italic.toggled.connect(self._on_change)
        self.chk_underline.toggled.connect(self._on_change)
        self.txt_prefix.textChanged.connect(self._on_change)
        self.txt_suffix.textChanged.connect(self._on_change)
        self.chk_use_tag_name.toggled.connect(self._on_change)

    def _pick_color(self):
        if not self._current_layer: return
        
        # initial color
        r, g, b, a = self._current_layer.font_color
        initial = QColor(r, g, b, a)
        
        color = QColorDialog.getColor(initial, self, "Select Font Color", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        
        if color.isValid():
            self._current_layer.font_color = (color.red(), color.green(), color.blue(), color.alpha())
            self._update_color_btn()
            self._on_change() # Trigger update

    def _update_color_btn(self):
        r, g, b, a = self._current_layer.font_color
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.btn_color.setText(f"Color: {hex_color}")
        self.btn_color.setStyleSheet(f"background-color: {hex_color}; color: {'black' if (r+g+b)/3 > 128 else 'white'}")

    def _on_browse(self):
        if not self._current_layer: return
        
        path = ""
        if self._current_layer.type == LayerType.IMAGE_FOLDER:
            path = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Select Image", filter="Images (*.png *.jpg *.jpeg)")
            
        if path:
            self.path_input.setText(path)

    def _create_slider_spin(self, label, min_val, max_val, parent_layout):
        container = QWidget()
        h = QHBoxLayout(container)
        h.setContentsMargins(0,0,0,0)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        
        h.addWidget(slider)
        h.addWidget(spin)
        
        # Sync
        slider.valueChanged.connect(spin.setValue)
        spin.valueChanged.connect(slider.setValue)
        
        # Connect to main change handler
        spin.valueChanged.connect(self._on_change)
        
        parent_layout.addRow(label, container)
        return spin

    def set_layer(self, layer: Layer):
        self._block_signals = True
        self._current_layer = layer
        
        if layer is None:
            self.setEnabled(False)
            self._block_signals = False
            return
        
        self.setEnabled(True)
        
        # Map LayerType/TextSource to Combo
        # Logic to select correct index.
        idx = 0
        if layer.enabled:
             if layer.type == LayerType.TEXT:
                 if layer.text_source == TextSource.NAME: idx = 1
                 elif layer.text_source == TextSource.DESCRIPTION: idx = 2
                 elif layer.text_source == TextSource.GENRE: idx = 3
                 elif layer.text_source == TextSource.YEAR: idx = 4
                 elif layer.text_source == TextSource.MANUFACTURER: idx = 5
             elif layer.type == LayerType.IMAGE: idx = 6
             elif layer.type == LayerType.IMAGE_FOLDER: idx = 7
        
        self.combo_type.setCurrentIndex(idx)
        
        # UI Visiblity based on type
        # UI Visiblity based on type
        is_text = layer.type == LayerType.TEXT
        is_media = layer.type in [LayerType.IMAGE, LayerType.IMAGE_FOLDER]
        is_background = layer.name == "Background"
        
        self.text_group.setVisible(is_text)
        self.file_group.setVisible(is_media)
        
        if is_background and layer.type == LayerType.IMAGE:
             # Show background combo, hide normal input
             self.path_input.setVisible(False)
             self.btn_browse.setVisible(False)
             self.combo_bg.setVisible(True)
             self.btn_open_folder.setVisible(True)
             self._populate_backgrounds(layer.image_path)
        else:
             self.path_input.setVisible(True)
             self.btn_browse.setVisible(True)
             self.combo_bg.setVisible(False)
             self.btn_open_folder.setVisible(False)
        
        # Lock Input type for background and hide dimensions
        if is_background:
             self.combo_type.setEnabled(False) 
             if hasattr(self, 'pos_group'):
                 self.pos_group.setVisible(False)
        else:
             self.combo_type.setEnabled(True)
             if hasattr(self, 'pos_group'):
                 self.pos_group.setVisible(True)

        # Values
        self.path_input.setText(layer.image_path if layer.type == LayerType.IMAGE else layer.folder_path)
        self.font_combo.setCurrentText(layer.font_path.replace(".ttf", "")) # Simple name match
        self.font_size.setValue(layer.font_size)
        self._update_color_btn()
        
        align_map = {"left": 0, "center": 1, "right": 2} # lowercase in model
        self.combo_align.setCurrentIndex(align_map.get(layer.text_align, 0))
        
        self.spin_max_chars.setValue(layer.max_chars)
        self.chk_bold.setChecked(layer.is_bold)
        self.chk_italic.setChecked(layer.is_italic)
        self.chk_underline.setChecked(layer.is_underline)
        
        self.txt_prefix.setText(layer.text_prefix)
        self.txt_suffix.setText(layer.text_suffix)
        
        # Name option visibility
        self.chk_use_tag_name.setVisible(layer.text_source == TextSource.NAME)
        self.chk_use_tag_name.setChecked(layer.use_game_name_tag)
        
        self.spin_x.setValue(layer.x)
        self.spin_y.setValue(layer.y)
        self.spin_w.setValue(layer.width)
        self.spin_h.setValue(layer.height)

        self._block_signals = False

    def _on_change(self):
        if self._block_signals or self._current_layer is None:
            return
            
        # Update model from UI
        idx = self.combo_type.currentIndex()
        data = self.combo_type.currentData()
        
        if idx == 0: 
            self._current_layer.enabled = False
        else:
            self._current_layer.enabled = True
            if isinstance(data, TextSource):
                self._current_layer.type = LayerType.TEXT
                self._current_layer.text_source = data
            elif isinstance(data, LayerType):
                self._current_layer.type = data
        
        if self._current_layer.type == LayerType.IMAGE:
            if self._current_layer.name == "Background" and self.combo_bg.isVisible():
                 # Use combo selection
                 bg_name = self.combo_bg.currentText()
                 if bg_name:
                     self._current_layer.image_path = os.path.abspath(os.path.join("assets", "backgrounds", bg_name))
            else:
                 self._current_layer.image_path = self.path_input.text()
        elif self._current_layer.type == LayerType.IMAGE_FOLDER:
            self._current_layer.folder_path = self.path_input.text()
            
        self._current_layer.font_path = f"{self.font_combo.currentText()}.ttf" # Dummy extension
        self._current_layer.font_size = self.font_size.value()
        
        # font_color handled by picker
        
        self._current_layer.text_align = self.combo_align.currentText().lower()
        self._current_layer.max_chars = self.spin_max_chars.value()
        self._current_layer.is_bold = self.chk_bold.isChecked()
        self._current_layer.is_italic = self.chk_italic.isChecked()
        self._current_layer.is_underline = self.chk_underline.isChecked()
        self._current_layer.text_prefix = self.txt_prefix.text()
        self._current_layer.text_suffix = self.txt_suffix.text()
        self._current_layer.use_game_name_tag = self.chk_use_tag_name.isChecked()
        
        self._current_layer.x = self.spin_x.value()
        self._current_layer.y = self.spin_y.value()
        self._current_layer.width = self.spin_w.value()
        self._current_layer.height = self.spin_h.value()
        
        # Name option visibility update
        self.chk_use_tag_name.setVisible(self._current_layer.text_source == TextSource.NAME)
        
        self.text_group.setVisible(self._current_layer.type == LayerType.TEXT)
        self.file_group.setVisible(self._current_layer.type != LayerType.TEXT)

        self.layer_changed.emit()

    def _open_bg_folder(self):
        bg_dir = os.path.abspath(os.path.join("assets", "backgrounds"))
        if not os.path.exists(bg_dir):
            os.makedirs(bg_dir)
        QDesktopServices.openUrl(QUrl.fromLocalFile(bg_dir))

    def _populate_backgrounds(self, current_path):
        self.combo_bg.blockSignals(True)
        self.combo_bg.clear()
        
        bg_dir = os.path.join("assets", "backgrounds")
        if not os.path.exists(bg_dir):
            os.makedirs(bg_dir)
            
        files = [f for f in os.listdir(bg_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.combo_bg.addItems(files)
        
        # Select current
        if current_path:
            name = os.path.basename(current_path)
            index = self.combo_bg.findText(name)
            if index >= 0:
                self.combo_bg.setCurrentIndex(index)
        elif files:
            # If no path set but we have files, select first and Sync to Model
            self.combo_bg.setCurrentIndex(0)
            # FORCE UPDATE MODEL
            if self._current_layer:
                self._current_layer.image_path = os.path.abspath(os.path.join(bg_dir, files[0]))
                
        self.combo_bg.blockSignals(False)
