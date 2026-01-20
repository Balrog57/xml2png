import sys
import os
from PIL import Image

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from model.xml_parser import XMLParser
from model.compositor import ImageCompositor, Layer, LayerType, TextSource

def run_test():
    print("Running Headless Verification...")
    
    # 1. Create Dummy XML
    xml_content = """<?xml version="1.0"?>
    <gameList>
        <game>
            <path>./roms/super_mario.zip</path>
            <name>Super Mario</name>
            <desc>A plumber saves a princess.</desc>
            <releasedate>19850913T000000</releasedate>
            <publisher>Nintendo</publisher>
        </game>
    </gameList>
    """
    
    with open("test_gamelist.xml", "w") as f:
        f.write(xml_content)
        
    print("[OK] Created test_gamelist.xml")

    # 2. Parse XML
    games = XMLParser.parse("test_gamelist.xml")
    if len(games) != 1:
        print("[FAIL] Game count mismatch")
        return
    game = games[0]
    if game.rom_name != "super_mario" or game.year != "1985":
        print(f"[FAIL] Game data incorrect: {game}")
        return
    print(f"[OK] Parsed Game: {game.rom_name} ({game.year})")
    
    # 3. Compositor Test
    comp = ImageCompositor()
    layers = [
        Layer("BG", LayerType.IMAGE, enabled=True, width=500, height=500), # Empty bg path logic test
        Layer("Desc", LayerType.TEXT, enabled=True, x=10, y=10, width=400, height=100, text_source=TextSource.DESCRIPTION),
        Layer("Year", LayerType.TEXT, enabled=True, x=10, y=200, text_source=TextSource.YEAR, font_size=50)
    ]
    
    # Create output dir
    if not os.path.exists("test_output"):
        os.mkdir("test_output")
        
    img = comp.composit(game, layers, "") # Empty BG path
    img.save("test_output/super_mario.png")
    
    if os.path.exists("test_output/super_mario.png"):
        print("[OK] Generated test_output/super_mario.png")
    else:
        print("[FAIL] Image not generated")
        
    print("Verification Successful.")

if __name__ == "__main__":
    run_test()
