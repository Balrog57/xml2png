import sys
import os

# Add src to python path to facilitate imports if run from root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import QApplication
from controller.app_controller import AppController

def main():
    app = QApplication(sys.argv)
    
    # Initialize Controller (which manages the View)
    controller = AppController()
    
    print("XML2PNG (Python Edition) started.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
