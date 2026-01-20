from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QRect
from PIL import Image

class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel("No Preview")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Checkered background or dark grey for transparency
        self.image_label.setStyleSheet("background-color: #2b2b2b; color: #888; border: 1px solid #444;")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setScaledContents(False)  # We handle scaling manually or use proper ratio policy
        
        self.layout.addWidget(self.image_label)
        
        self.current_pixmap = None
        self.highlight_layer = None

    def update_image(self, pil_image: Image.Image, highlight_layer=None):
        self.highlight_layer = highlight_layer
        
        if pil_image is None:
            self.image_label.setText("No Preview")
            self.current_pixmap = None
            return

        # Convert PIL to QPixmap
        if pil_image.mode != "RGBA":
            # Forcing RGBA ensures consistency even if original was RGB or L
            pil_image = pil_image.convert("RGBA")
            
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format.Format_RGBA8888)
        self.current_pixmap = QPixmap.fromImage(qimage)
        
        # Draw highlight on the pixmap if needed
        if self.highlight_layer and self.highlight_layer.enabled and self.highlight_layer.name != "Background":
             self._draw_highlight_on_pixmap()
        
        self.image_label.setPixmap(self.current_pixmap)
        self._update_display()
        
    def resizeEvent(self, event):
        self._update_display()
        super().resizeEvent(event)
        
    def _update_display(self):
        if self.current_pixmap and not self.current_pixmap.isNull():
             # Scale to widget size keeping aspect ratio
             scaled = self.current_pixmap.scaled(
                 self.image_label.size(), 
                 Qt.AspectRatioMode.KeepAspectRatio, 
                 Qt.TransformationMode.SmoothTransformation
             )
             self.image_label.setPixmap(scaled)

    def _draw_highlight_on_pixmap(self):
        if not self.current_pixmap or not self.highlight_layer:
            return
            
        # We need to draw on a copy or modify the current one?
        # Drawing on current pixmap is fine as it's regenerated every update
        painter = QPainter(self.current_pixmap)
        
        # Different color? Red is standard highlight
        pen = QPen(QColor(255, 0, 0)) # Red
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        
        x = self.highlight_layer.x
        y = self.highlight_layer.y
        w = self.highlight_layer.width
        h = self.highlight_layer.height
        
        if w > 0 and h > 0:
            painter.drawRect(x, y, w, h)
            
        painter.end()
