# XML2PNG Development Guide

## Project Overview

🖼️ XML2PNG (Python Edition) : Un fork dédié au visuel. Il génère automatiquement des assets (Wheels, cartouches) à partir de fichiers XML pour habiller vos interfaces. The application follows an MVC architecture with separate layers for model, view, and controller components.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Run from project root
python src/main.py

# Run from src directory
python main.py
```

### Building/Packaging
```bash
# Build standalone executable with PyInstaller
pyinstaller xml2png.spec --clean --noconfirm

# Build with assets included
pyinstaller xml2png.spec --clean --noconfirm
xcopy "assets" "dist\XML2PNG_Build\assets\" /E /I /Y

# Create installer (requires Inno Setup on Windows)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" xml2png.iss
```

### Code Quality
```bash
# No specific linting/testing commands currently configured
# Consider adding:
# pip install black flake8 pytest
# black src/
# flake8 src/
# pytest tests/
```

## Code Style Guidelines

### Import Organization
- Use absolute imports from project root (sys.path is modified in main.py)
- Group imports in this order: standard library, third-party, local imports
- Import individual classes/functions rather than modules when appropriate

```python
# Standard library
import os
import sys
from typing import List, Optional

# Third-party
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PIL import Image

# Local imports
from model.compositor import Layer, LayerType
from view.main_window import MainWindow
```

### Type Hints
- Use type hints consistently throughout the codebase
- Use dataclasses for model objects
- Import types from typing module as needed

```python
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

@dataclass
class Layer:
    name: str
    type: LayerType
    enabled: bool = False     # True if an input is configured (not None)
    visible: bool = True      # Eye toggle - show/hide in preview
    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 100
    
    # Image Transformations (for IMAGE and IMAGE_FOLDER types)
    mirror: bool = False       # Horizontal flip
    stretch: bool = False      # Ignore aspect ratio
    rotation: int = 0          # 0, 90, 180, 270 degrees
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `LayerControlWidget`, `ImageCompositor`)
- **Functions/Methods**: snake_case (e.g., `parse_xml_file`, `update_preview`)
- **Variables**: snake_case (e.g., `current_layer`, `dest_folder`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `VERSION = "1.0.4"`)
- **Private members**: prefix with underscore (e.g., `_current_layer`, `_block_signals`)

### Error Handling
- Use specific exception types
- Include descriptive error messages
- Handle file operations with proper error checking
- Use QMessageBox for user-facing errors in GUI components

```python
def parse_file(file_path: str) -> List[GameEntry]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"XML file not found: {file_path}")
    
    try:
        tree = ET.parse(file_path)
        return process_tree(tree)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML file: {e}")
```

### PyQt6 Patterns
- Use signals/slots for component communication
- Inherit from appropriate Qt widgets
- Use pyqtSignal() for custom signals
- Follow Qt naming conventions for signal/slot methods

```python
class MainWindow(QMainWindow):
    # Signals
    xml_path_changed = pyqtSignal(str)
    layer_selected = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
```

### File Structure
- **model/**: Data structures and business logic (XML parsing, image composition)
- **view/**: PyQt6 UI components and widgets
- **controller/**: Application logic and coordination between MVC components
- **utils/**: Utility functions and helper classes
- **assets/**: Static resources (backgrounds, images)

### Documentation
- Use docstrings for classes and public methods
- Keep comments concise and focused on complex logic
- Use type hints instead of inline documentation where possible

### Qt UI Best Practices
- Use layouts for responsive design
- Set appropriate size policies
- Handle thread operations with QThread for long-running tasks
- Use proper Qt memory management (parent-child relationships)

### Threading
- Use QThread for background operations (XML parsing, image generation)
- Communicate with main thread via signals
- Handle thread lifecycle properly

```python
class BatchWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    
    def run(self):
        for i, item in enumerate(items):
            if not self.running:
                break
            process_item(item)
            self.progress.emit(i + 1)
        self.finished.emit()
```

### Dependencies
- **PyQt6**: GUI framework
- **Pillow**: Image processing
- **lxml**: XML parsing (consider using standard xml.etree.ElementTree instead)
- **requests**: HTTP requests for updates
- **packaging**: Version comparison

### Assets Management
- Background images stored in `assets/backgrounds/`
- UI should auto-detect available backgrounds
- Include assets in build process (see build_windows.yml)

### Testing
- Currently no test framework configured
- Consider adding pytest for unit tests
- Test XML parsing with sample files
- Test image composition with various layer configurations

### Version Management
- Version defined in `controller/app_controller.py`
- Use semantic versioning (e.g., "1.0.3")
- Update version in both code and spec file for releases

### Git Workflow
- Main branch for production releases
- Tag releases with version numbers (v1.0.3)
- Use pull requests for significant changes
- Include .gitignore for Python, build artifacts, and IDE files