from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QFileDialog, QComboBox, QProgressBar, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from view.preview_widget import PreviewWidget
from view.layer_controls import LayerControlWidget
from model.compositor import Layer, LayerType

class MainWindow(QMainWindow):
    # Signals
    xml_path_changed = pyqtSignal(str)
    dest_path_changed = pyqtSignal(str)
    generate_clicked = pyqtSignal()
    layer_selected = pyqtSignal(int) # index 0=BG, 1=Layer1...

    def __init__(self):
        super().__init__()
        self.setWindowTitle("XML2PNG (Python Edition)")
        self.resize(1200, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.init_ui()

    def init_ui(self):
        # Main Layout: Horizontal Split
        main_layout = QHBoxLayout(self.central_widget)
        
        # --- LEFT: Preview ---
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<b>Preview</b>"))
        self.preview = PreviewWidget()
        left_layout.addWidget(self.preview, 1) # Stretch factor 1
        
        # Navigation controls for preview (Next/Prev game)
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("< Previous")
        self.btn_next = QPushButton("Next >")
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        left_layout.addLayout(nav_layout)
        
        main_layout.addLayout(left_layout, 2) # Take 2/3 width

        # --- RIGHT: Controls ---
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 0, 0, 0)

        # 1. File Selection
        right_layout.addWidget(QLabel("<b>Project Settings</b>"))
        
        # XML
        right_layout.addLayout(self._create_file_picker("Select XML File:", self.xml_path_changed, is_folder=False))
        # Destination
        right_layout.addLayout(self._create_file_picker("Select Destination:", self.dest_path_changed, is_folder=True))
        
        right_layout.addSpacing(20)

        # 2. Layer Selection
        right_layout.addWidget(QLabel("<b>Layer Configuration</b>"))
        self.layer_selector = QComboBox()
        self.layer_selector.currentIndexChanged.connect(self._on_layer_changed)
        right_layout.addWidget(self.layer_selector)

        # 3. Layer Controls
        self.layer_controls = LayerControlWidget()
        right_layout.addWidget(self.layer_controls)
        
        right_layout.addStretch()

        # 4. Action
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)
        
        self.btn_generate = QPushButton("GENERATE ALL IMAGES")
        self.btn_generate.setFixedHeight(50)
        self.btn_generate.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #4CAF50; color: white;")
        self.btn_generate.clicked.connect(self.generate_clicked.emit)
        right_layout.addWidget(self.btn_generate)
        
        main_layout.addLayout(right_layout, 1) # Take 1/3 width

    def _create_file_picker(self, label_text, signal, is_folder):
        v = QVBoxLayout()
        v.addWidget(QLabel(label_text))
        
        h = QHBoxLayout()
        line_edit = QLineEdit()
        btn = QPushButton("...")
        btn.setFixedWidth(40)
        
        def pick():
            if is_folder:
                path = QFileDialog.getExistingDirectory(self, "Select Directory")
            else:
                path, _ = QFileDialog.getOpenFileName(self, "Select File", filter="XML Files (*.xml);;All Files (*)")
            
            if path:
                line_edit.setText(path)
                signal.emit(path)

        btn.clicked.connect(pick)
        h.addWidget(line_edit)
        h.addWidget(btn)
        v.addLayout(h)
        v.setSpacing(2)
        return v

    def _on_layer_changed(self, index):
        self.layer_selected.emit(index)

    def set_layer_names(self, count):
        self.layer_selector.blockSignals(True)
        self.layer_selector.clear()
        self.layer_selector.addItem("Background")
        for i in range(1, count + 1):
            self.layer_selector.addItem(f"Layer #{i}")
        self.layer_selector.blockSignals(False)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message):
        QMessageBox.information(self, "Info", message)
