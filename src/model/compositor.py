from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
import textwrap
from enum import Enum
import winreg # For Windows Registry Font Lookup

from model.xml_parser import GameEntry

class LayerType(Enum):
    TEXT = "text"
    IMAGE = "image"        # Static single image
    IMAGE_FOLDER = "folder" # Variable image from folder based on rom name

class TextSource(Enum):
    DESCRIPTION = "description"
    YEAR = "year"
    GENRE = "genre"
    MANUFACTURER = "manufacturer"
    NAME = "name"
    CUSTOM = "custom" # Maybe allow custom static text?

@dataclass
class Layer:
    name: str # "Layer #1"
    type: LayerType
    enabled: bool = False  # True if an input is configured (not None)
    visible: bool = True   # Eye toggle - show/hide in preview (independent of enabled)
    
    # Position & Size
    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 100
    
    # Text Properties
    text_source: TextSource = TextSource.DESCRIPTION
    font_path: str = "arial.ttf" # Default system font logic needed
    font_size: int = 24
    font_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    text_align: str = "left" # left, center, right
    max_chars: int = 0 # 0 = unlimited
    word_wrap: bool = True
    is_bold: bool = False
    is_italic: bool = False
    is_underline: bool = False
    text_prefix: str = ""
    text_suffix: str = ""
    use_game_name_tag: bool = False # If True, use <name>, else use rom filename 
    
    # Image Properties
    image_path: str = "" # For static image
    folder_path: str = "" # For folder source
    fallback_text_layer: bool = False # If image missing, use text? (Simple boolean for now, or index)
    
    # Image Transformations
    mirror: bool = False
    stretch: bool = False
    rotation: int = 0  # 0, 90, 180, 270

class ImageCompositor:
    def __init__(self):
        self._font_cache = {}

    def _find_font_filename_in_registry(self, font_name, bold=False, italic=False):
        # normalize name
        search_name = font_name.lower().strip()
        
        # Suffixes in registry keys
        # "Arial (TrueType)"
        # "Arial Bold (TrueType)"
        # "Arial Bold Italic (TrueType)"
        
        needed_styles = []
        if bold: needed_styles.append("bold")
        if italic: needed_styles.append("italic")
        
        key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                count = winreg.QueryInfoKey(key)[1]
                for i in range(count):
                    try:
                        name, filename, _ = winreg.EnumValue(key, i)
                        name_lower = name.lower()
                        
                        # Check availability of styles
                        # Logic: if we want Bold, name must contain "bold" (usually).
                        # But strict matching is hard.
                        # Simple Heuristic: 
                        # 1. Name must start with font family or contain it distinctly
                        # 2. Check for attributes
                        
                        # Remove "(TrueType)" etc
                        clean_reg_name = name_lower.replace("(truetype)", "").replace("(opentype)", "").strip()
                        
                        # Match family
                        if not clean_reg_name.startswith(search_name):
                             continue
                        
                        # Now check if it's the specific variant we want
                        # If we want regular (no bold/italic), name shouldn't have them
                        # But some fonts are just "Impact", no "Regular"
                        
                        has_bold = "bold" in clean_reg_name
                        has_italic = "italic" in clean_reg_name
                        
                        if bold == has_bold and italic == has_italic:
                             return filename
                    except:
                        continue
        except Exception:
            pass
        return None

    def get_font(self, font_name: str, size: int, bold=False, italic=False) -> ImageFont.FreeTypeFont:
        key = (font_name, size, bold, italic)
        if key not in self._font_cache:
            
            # 1. Try Registry Lookup (Best for "Century Gothic", etc)
            reg_filename = self._find_font_filename_in_registry(font_name, bold, italic)
            
            potential_paths = []
            system_fonts_dir = "C:\\Windows\\Fonts"
            
            if reg_filename:
                # Registry gives filename only usually, sometimes full path
                if os.path.isabs(reg_filename):
                    potential_paths.append(reg_filename)
                else:
                    potential_paths.append(os.path.join(system_fonts_dir, reg_filename))
            
            # 2. Fallback to common mappings and heuristics (Legacy/Backup)
            # ... (Existing logic shortened or kept as fallback)
            # Let's keep a simplified fallback dict for standard stuff
            font_map = {
                "times new roman": "times", "arial": "arial", "verdana": "verdana",
                "tahoma": "tahoma", "impact": "impact", "comic sans ms": "comic",
                "courier new": "cour", "segoe ui": "segoeui"
            }
            clean_name = font_name
            if font_name.lower().endswith(".ttf"): clean_name = font_name[:-4]
            base = font_map.get(clean_name.lower(), clean_name)
            
            suffix = ""
            if bold and italic: suffix = "bi"
            elif bold: suffix = "bd"
            elif italic: suffix = "i"
            
            potential_paths.append(os.path.join(system_fonts_dir, f"{base}{suffix}.ttf"))
            potential_paths.append(os.path.join(system_fonts_dir, f"{base}.ttf"))
            
            found_font = None
            for p in potential_paths:
                if os.path.exists(p):
                    try:
                        found_font = ImageFont.truetype(p, size)
                        break
                    except: continue
            
            if not found_font:
                # Try loading by name directly (works if library installed)
                try: 
                    found_font = ImageFont.truetype(font_name, size)
                except: 
                    try: found_font = ImageFont.truetype("arial.ttf", size) # Final Fallback
                    except: found_font = ImageFont.load_default()
            
            self._font_cache[key] = found_font
            
        return self._font_cache[key]

    def composit(self, 
                 game: GameEntry, 
                 layers: List[Layer], 
                 background_path: str,
                 output_size: Optional[Tuple[int, int]] = None) -> Image.Image:
        
        # 1. Canvas Setup logic
        # - If Background Layer (Layer 0) has an image, use its size as canvas default.
        # - Initialize canvas with Transparent (0,0,0,0).
        
        bg_layer = layers[0]
        bg_img = None
        
        # Always load background to get dimensions, even if hidden
        if bg_layer.image_path and os.path.exists(bg_layer.image_path):
            try:
                bg_img = Image.open(bg_layer.image_path).convert("RGBA")
            except Exception:
                pass
        
        # Determine Target Size from background (even if hidden)
        target_w, target_h = (1024, 768) # Default fallback
        if bg_img:
            target_w, target_h = bg_img.size
            
        if output_size:
            target_w, target_h = output_size

        # Create Transparent Canvas
        canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        
        # Draw Background Image only if layer is enabled AND visible
        if bg_img and bg_layer.enabled and bg_layer.visible:
            # If output_size forced a different size, resize background?
            # Or center it?
            # User wants "preview adapts to background", so usually 1:1.
            # If explicit output_size is given, we likely want to stretch bg to it.
            if (target_w, target_h) != bg_img.size:
                 bg_img = bg_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            canvas.paste(bg_img, (0, 0))

        for i, layer in enumerate(layers):
            # Skip if not enabled (no input configured) or not visible (eye off)
            if not layer.enabled or not layer.visible:
                continue
            
            # Skip Layer 0 (Background) as it is handled above
            if i == 0: continue 

            if layer.type == LayerType.TEXT:
                self._render_text_layer(canvas, draw, layer, game)
            
            elif layer.type == LayerType.IMAGE:
                self._render_static_image_layer(canvas, layer)

            elif layer.type == LayerType.IMAGE_FOLDER:
                success = self._render_folder_image_layer(canvas, layer, game)
                if not success and layer.fallback_text_layer:
                    pass 
        
        return canvas

    def _render_text_layer(self, canvas: Image.Image, draw: ImageDraw.Draw, layer: Layer, game: GameEntry):
        # 1. Get Text Content
        text = ""
        
        if game is None:
            # Default examples when no gamelist is loaded
            if layer.text_source == TextSource.NAME:
                text = "Sonic The Hedgehog 2"
            elif layer.text_source == TextSource.DESCRIPTION:
                text = "Dr. Robotnik is back and he's planning to take over the world again! It's up to Sonic and his new pal Tails to stop him."
            elif layer.text_source == TextSource.GENRE:
                text = "Platformer"
            elif layer.text_source == TextSource.YEAR:
                text = "1992"
            elif layer.text_source == TextSource.MANUFACTURER:
                text = "SEGA"
        else:
            if layer.text_source == TextSource.DESCRIPTION:
                text = game.description
            elif layer.text_source == TextSource.NAME:
                # Default: rom_name. Option: display_name (<name>)
                text = game.display_name if layer.use_game_name_tag else game.rom_name
            elif layer.text_source == TextSource.YEAR:
                text = game.year
            elif layer.text_source == TextSource.GENRE:
                text = game.genre
            elif layer.text_source == TextSource.MANUFACTURER:
                text = game.manufacturer
        
        if not text:
            return

        # Apply Prefix/Suffix
        if layer.text_prefix:
            text = f"{layer.text_prefix}{text}"
        if layer.text_suffix:
            text = f"{text}{layer.text_suffix}"

        if layer.max_chars > 0 and len(text) > layer.max_chars:
            text = text[:layer.max_chars] + "..."

        # 2. Get Font
        font = self.get_font(layer.font_path, layer.font_size, bold=layer.is_bold, italic=layer.is_italic)

        # 3. Wrapping
        lines = []
        if layer.word_wrap and layer.width > 0:
            avg_char_width = font.getlength("x")
            if avg_char_width > 0:
                wrap_width = max(1, int(layer.width / avg_char_width))
                lines = textwrap.wrap(text, width=wrap_width)
            else: 
                lines = [text]
        else:
            lines = [text]

        # 4. Draw
        current_y = layer.y
        # Use font metric for line height
        bbox = font.getbbox("Tg")
        line_height = int(bbox[3] - bbox[1] + 4)

        for line in lines:
            if current_y + line_height > layer.y + layer.height:
                break # Clip at bottom
            
            # X alignment
            line_width = font.getlength(line)
            draw_x = layer.x
            
            if layer.text_align == "center":
                draw_x = layer.x + (layer.width - line_width) / 2
            elif layer.text_align == "right":
                draw_x = layer.x + layer.width - line_width
            
            draw.text((draw_x, current_y), line, font=font, fill=layer.font_color)
            
            # Underline
            if layer.is_underline:
                underline_y = current_y + line_height - 2
                draw.line([(draw_x, underline_y), (draw_x + line_width, underline_y)], fill=layer.font_color, width=1)

            current_y += line_height

    def _render_static_image_layer(self, canvas: Image.Image, layer: Layer):
        if not layer.image_path or not os.path.exists(layer.image_path):
            return
        
        try:
            img = Image.open(layer.image_path).convert("RGBA")
            self._paste_image(canvas, img, layer)
        except Exception:
            pass

    def _render_folder_image_layer(self, canvas: Image.Image, layer: Layer, game: GameEntry) -> bool:
        if not layer.folder_path or not os.path.exists(layer.folder_path):
            return False
            
        # Try finding image: rom_name.png, rom_name.jpg, game.name??
        # Usually rom_name.png
        
        if not game:
            return False
            
        filename = f"{game.rom_name}.png"
        full_path = os.path.join(layer.folder_path, filename)
        
        if not os.path.exists(full_path):
            # Try jpg?
             full_path = os.path.join(layer.folder_path, f"{game.rom_name}.jpg")
             if not os.path.exists(full_path):
                 return False

        try:
            img = Image.open(full_path).convert("RGBA")
            self._paste_image(canvas, img, layer)
            return True
        except Exception:
            return False

    def _paste_image(self, canvas: Image.Image, overlay: Image.Image, layer: Layer):
        # Apply transformations: Mirror -> Rotation
        if layer.mirror:
            overlay = overlay.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        
        if layer.rotation in (90, 180, 270):
            # PIL rotates counter-clockwise, so negate for clockwise
            overlay = overlay.rotate(-layer.rotation, expand=True)
        
        box_w = layer.width
        box_h = layer.height
        
        if box_w <= 0 or box_h <= 0:
            # No constraints, use original size
            overlay_resized = overlay
            paste_x = layer.x
            paste_y = layer.y
        elif layer.stretch:
            # Stretch: Ignore aspect ratio, fill the box exactly
            overlay_resized = overlay.resize((box_w, box_h), Image.Resampling.LANCZOS)
            paste_x = layer.x
            paste_y = layer.y
        else:
            # Aspect Fit logic
            img_w, img_h = overlay.size
            ratio_w = box_w / img_w
            ratio_h = box_h / img_h
            scale = min(ratio_w, ratio_h)
            
            target_w = int(img_w * scale)
            target_h = int(img_h * scale)
            
            overlay_resized = overlay.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            # Center in box
            off_x = (box_w - target_w) // 2
            off_y = (box_h - target_h) // 2
            
            paste_x = layer.x + off_x
            paste_y = layer.y + off_y
        
        canvas.alpha_composite(overlay_resized, (paste_x, paste_y))
