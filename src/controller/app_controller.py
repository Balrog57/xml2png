from PyQt6.QtCore import QObject, QThread, pyqtSignal
from typing import List

from model.xml_parser import XMLParser, GameEntry
from model.compositor import ImageCompositor, Layer, LayerType
from view.main_window import MainWindow

import os
import sys

from utils.updater import Updater
from PyQt6.QtWidgets import QMessageBox

VERSION = "1.0.4"

class UpdateWorker(QThread):
    finished = pyqtSignal(bool, str, str) # found, version, url

    def __init__(self, current_version):
        super().__init__()
        self.updater = Updater(current_version)

    def run(self):
        found, ver, url = self.updater.check_for_updates()
        self.finished.emit(found, ver, url)

class BatchWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    
    def __init__(self, games, layers, dest_folder, compositor):
        super().__init__()
        self.games = games
        self.layers = layers
        self.dest_folder = dest_folder
        self.compositor = compositor
        self.running = True

    def run(self):
        total = len(self.games)
        for i, game in enumerate(self.games):
            if not self.running:
                break
                
            try:
                # Determine background path from layers[0] (Background)
                # In our model, Layer 0 is treated as a layer too, but we pass it as BG path?
                # Actually compositor takes list of layers AND specific bg_path.
                # Let's assume Layer 0 IS the background layer if type=IMAGE.
                
                # Logic: The Compositor iterates all layers.
                # If Layer 0 is just an image, we can pass it as background or just let it render first.
                # Our compositor implementation clears to black, then renders layers.
                # So we just pass all layers.
                
                # BUT, compositor.composit signature is: (game, layers, background_path)
                # And we logic'd that background_path is separate.
                # Let's adjust: Layer 0 = Background. If type=Image, use its path as bg_path.
                
                bg_layer = self.layers[0]
                bg_path = bg_layer.image_path if bg_layer.type == LayerType.IMAGE else ""
                
                # Render (excluding 'background' layer from the list passed as 'layers' if we use bg_path arg? 
                # Or just pass all and let it overdraw?
                # Best: Pass all layers including #0. The compositor draws them in order.
                # If Layer #0 is "Background", it draws first.
                # The 'background_path' arg in compositor was for the base canvas.
                # We can just ignore that arg if Layer #0 covers it, or pass Layer 0 path.
                
                img = self.compositor.composit(game, self.layers, bg_path)
                
                # Save
                save_name = f"{game.rom_name}.png"
                save_path = os.path.join(self.dest_folder, save_name)
                img.save(save_path)
                
            except Exception as e:
                print(f"Error processing {game.rom_name}: {e}")
            
            self.progress.emit(int(((i + 1) / total) * 100))
        
        self.finished.emit()

    def stop(self):
        self.running = False


class AppController(QObject):
    def __init__(self):
        super().__init__()
        self.view = MainWindow()
        self.compositor = ImageCompositor()
        
        self.games: List[GameEntry] = []
        self.current_game_index = 0
        
        # Initialize Layers (Background + 10 Layers)
        self.layers: List[Layer] = []
        self._init_default_layers()
        
        self.view.set_layers(self.layers)
        self._connect_signals()
        
        self.view.show()
        
        self.view.select_layer(0)  # Select Background by default
        self._on_layer_selected(0)
        self._update_preview()

        # Check for updates
        self.check_updates()

    def check_updates(self):
        self.update_worker = UpdateWorker(VERSION)
        self.update_worker.finished.connect(self._on_update_check_finished)
        self.update_worker.start()

    def _on_update_check_finished(self, found, version, url):
        if found:
            reply = QMessageBox.question(
                self.view, 
                "Update Available", 
                f"A new version ({version}) is available. Do you want to update now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.view.show_info("Downloading update... The application will restart automatically.")
                # We do this in the main thread now or another worker? 
                # Updater.download_and_install is blocking but has no UI feedback except print.
                # Let's run it.
                qt_updater = Updater(VERSION) # Re-instantiate or reuse
                qt_updater.download_and_install(url)
                # It calls sys.exit(0) on success

    def _init_default_layers(self):
        # 0: Background
        bg = Layer(name="Background", type=LayerType.IMAGE, x=0, y=0, width=1024, height=768, enabled=True, visible=True)
        
        # Force default background path from assets
        bg_dir = os.path.join("assets", "backgrounds")
        if os.path.exists(bg_dir):
            files = [f for f in os.listdir(bg_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if files:
                bg.image_path = os.path.abspath(os.path.join(bg_dir, files[0]))

        self.layers.append(bg)
        
        # 1-10: Layers
        for i in range(1, 11):
            self.layers.append(Layer(name=f"Layer #{i}", type=LayerType.TEXT, enabled=False, x=100, y=100))

    def _connect_signals(self):
        self.view.xml_path_changed.connect(self.load_xml)
        self.view.dest_path_changed.connect(self.set_destination)
        self.view.layer_selected.connect(self._on_layer_selected)
        self.view.layer_visibility_toggled.connect(self._on_layer_visibility_toggled)
        self.view.generate_clicked.connect(self.toggle_generation)
        
        self.view.layer_controls.layer_changed.connect(self._on_layer_modified)
        
        self.view.btn_prev.clicked.connect(self.prev_game)
        self.view.btn_next.clicked.connect(self.next_game)

    def load_xml(self, path):
        try:
            self.games = XMLParser.parse(path)
            self.current_game_index = 0
            self.view.show_info(f"Loaded {len(self.games)} games successfully.")
            self._update_preview()
        except Exception as e:
            self.view.show_error(f"Failed to parse XML: {e}")

    def set_destination(self, path):
        self.dest_folder = path

    def _on_layer_selected(self, index):
        if 0 <= index < len(self.layers):
            layer = self.layers[index]
            self.view.layer_controls.set_layer(layer)

    def _on_layer_modified(self):
        # Layer object is modified in place by the widget controls
        self._update_preview()
    
    def _on_layer_visibility_toggled(self, index: int, is_visible: bool):
        if 0 <= index < len(self.layers):
            self.layers[index].visible = is_visible
            self._update_preview()
    
    def prev_game(self):
        if self.games and self.current_game_index > 0:
            self.current_game_index -= 1
            self._update_preview()

    def next_game(self):
        if self.games and self.current_game_index < len(self.games) - 1:
            self.current_game_index += 1
            self._update_preview()

    def _update_preview(self):
        game = None
        if self.games:
            game = self.games[self.current_game_index]
        else:
            # Dummy game for preview if no XML loaded
            game = GameEntry("Sonic The Hedgehog 2", "Sonic The Hedgehog 2", "Dr. Robotnik is back and he's planning to take over the world again! It's up to Sonic and his new pal Tails to stop him.", "1992", "Platformer", "SEGA")

        # Background path logic
        bg_layer = self.layers[0]
        bg_path = bg_layer.image_path if (bg_layer.type == LayerType.IMAGE and bg_layer.enabled) else ""
        
        # Determine the currently selected layer to highlight
        idx = self.view.layer_list._selected_index if hasattr(self.view, 'layer_list') else 0
        highlight_layer = None
        if 0 <= idx < len(self.layers):
            highlight_layer = self.layers[idx]

        # Render
        try:
            img = self.compositor.composit(game, self.layers, bg_path)
            self.view.preview.update_image(img, highlight_layer=highlight_layer)
        except Exception as e:
            print(f"Preview error: {e}")

    def toggle_generation(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            # Stop
            self.worker.stop()
            self.view.btn_generate.setText("Stopping...")
            self.view.btn_generate.setEnabled(False) # Wait for finish
        else:
            # Start
            self.start_batch_generation()

    def start_batch_generation(self):
        if not self.games:
            self.view.show_error("No XML loaded.")
            return
        if not hasattr(self, 'dest_folder') or not self.dest_folder:
             self.view.show_error("No destination selected.")
             return
             
        # Button becomes Stop
        self.view.btn_generate.setText("STOP GENERATION")
        self.view.btn_generate.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #f44336; color: white;")
        
        self.view.progress_bar.setVisible(True)
        self.view.progress_bar.setValue(0)
        
        self.worker = BatchWorker(self.games, self.layers, self.dest_folder, self.compositor)
        self.worker.progress.connect(self.view.progress_bar.setValue)
        self.worker.finished.connect(self._on_batch_finished)
        self.worker.start()

    def _on_batch_finished(self):
        self.view.btn_generate.setText("GENERATE ALL IMAGES")
        self.view.btn_generate.setStyleSheet("font-weight: bold; font-size: 14px; background-color: #4CAF50; color: white;")
        self.view.btn_generate.setEnabled(True)
        self.view.progress_bar.setVisible(False)
        
        if not hasattr(self, 'worker') or not self.worker.running:
             self.view.show_info("Batch generation stopped.")
        else:
             self.view.show_info("Batch generation completed!")
