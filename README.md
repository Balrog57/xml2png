# 🖼️ XML2PNG (Python Edition)

Un fork dédié au visuel. Il génère automatiquement des assets (Wheels, cartouches) à partir de fichiers XML pour habiller vos interfaces.

## Features

- **Batch Processing**: Generate thousands of images based on Hyperspin/EmulationStation XML databases.
- **Advanced Layer System**: 
  - **Background Layer**: Automatically adapts canvas size to the background image. Supports transparency.
  - **10 Configurable Layers**: Combine Text, Static Images, and Folder-based Variable Images.
- **Rich Text Customization**:
  - **Styles**: Bold, Italic, Underline.
  - **Formatting**: Color Picker (Hex/Palette), Alignment (Left/Center/Right).
  - **Controls**: Max Characters limit, Prefix & Suffix support.
  - **Dynamic Content**: Use Game Description, Year, Genre, Manufacturer, or Game Name (Filename or XML `<name>` tag).
  - **Fonts**: Scan and use installed System Fonts with search functionality.
- **Real-time Preview**: 
  - Visual editor with accurate Aspect Ratio handling. 
  - Highlights selected layer bounding box.
  - Demo text mode when no XML is loaded (shows example game: Sonic The Hedgehog 2).
- **Layer Visibility Toggles**: Eye icon to show/hide individual layers without losing settings.
- **Image Transformations**: Mirror (horizontal flip), Stretch (ignore aspect ratio), Rotation (0°, 90°, 180°, 270°).
- **User Experience**:
  - Stop/Pause generation.
  - Automatic `assets/backgrounds` detection for easy background selection.
- **High Performance**: Built with Python and Pillow for fast image processing.

## Requirements

- Python 3.10+
- PyQt6
- Pillow

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python src/main.py
   ```

## Usage

1. **Select XML**: Load your Hyperspin or EmulationStation XML file.
2. **Select Destination**: Choose where the generated images will be saved.
3. **Configure Background**:
   - Place your background images in `assets/backgrounds`.
   - Select "Background" layer and choose your image from the dropdown.
   - The output image size will match your background resolution.
4. **Configure Layers**:
   - Enable up to 10 layers.
   - Choose **Text**, **Static Image**, or **Folder Image** (matches ROM filename).
   - Customize position, size, and styles.
5. **Generate**: Click "GENERATE ALL IMAGES". You can stop the process at any time.

## Packaging

To build the standalone `.exe`:
```bash
pyinstaller xml2png.spec
```
The executable will be located in the `dist/XML2PNG_Build/` folder.

## Key Modules

- **src/model**: XML parsing (`xml_parser.py`) and Image Composition logic (`compositor.py`).
- **src/view**: PyQt6 User Interface (`main_window.py`, `layer_controls.py`, `preview_widget.py`).
- **src/controller**: Application logic and threading (`app_controller.py`).

## Credits

This project is a modernized and modular fork of the application originally proposed by [r0man0](http://r0man0.free.fr/).

