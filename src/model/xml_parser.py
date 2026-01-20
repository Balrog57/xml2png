import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional
import os

@dataclass
class GameEntry:
    rom_name: str # Filename without extension (used for output file)
    display_name: str # <name> tag content (used for Text Name)
    description: str
    year: str = ""
    genre: str = ""
    manufacturer: str = ""
    
    # Store original name/path just in case? 
    # For ES: path="./roms/mario.zip" -> rom_name="mario"
    # For HS: name="mario" -> rom_name="mario"

class XMLParser:
    @staticmethod
    def parse(file_path: str) -> List[GameEntry]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"XML file not found: {file_path}")
            
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML file: {e}")

        # Detect format based on root tag
        if root.tag == 'menu':
             return XMLParser._parse_hyperspin(root)
        elif root.tag == 'gameList':
             return XMLParser._parse_emulationstation(root)
        else:
            # Fallback or unknown
             raise ValueError(f"Unknown XML format. Root tag: {root.tag}")

    @staticmethod
    def _parse_hyperspin(root: ET.Element) -> List[GameEntry]:
        games = []
        for game_node in root.findall('game'):
            name = game_node.get('name', '')
            
            # Skip header or non-game entries if any
            if not name: 
                continue

            desc = game_node.findtext('description', '')
            year = game_node.findtext('year', '')
            genre = game_node.findtext('genre', '')
            manufacturer = game_node.findtext('manufacturer', '')

            games.append(GameEntry(
                rom_name=name, # HS uses name as the key/filename usually
                display_name=name, # HS <description> acts as full name sometimes? No, HS has <description> separate
                description=desc,
                year=year,
                genre=genre,
                manufacturer=manufacturer
            ))
        return games

    @staticmethod
    def _parse_emulationstation(root: ET.Element) -> List[GameEntry]:
        games = []
        for game_node in root.findall('game'):
            path = game_node.findtext('path', '')
            name = game_node.findtext('name', '') 
            # In ES, <name> is the display name, <path> implies the filename.
            # Usually for assets we want the filename (without extension) matches.
            
            if not path:
                # Some ES implementations might rely on just name? Rare.
                continue

            # Extract filename from path: ./roms/game.zip -> game
            basename = os.path.basename(path)
            rom_name = os.path.splitext(basename)[0]

            desc = game_node.findtext('desc', '')
            
            # Dates in ES are usually "YYYYMMDDT..."
            releasedate = game_node.findtext('releasedate', '')
            year = releasedate[:4] if releasedate and len(releasedate) >= 4 else ""

            genre = game_node.findtext('genre', '')
            developer = game_node.findtext('developer', '') 
            publisher = game_node.findtext('publisher', '')
            manufacturer = developer if developer else publisher

            games.append(GameEntry(
                rom_name=rom_name,
                display_name=name if name else rom_name,
                description=desc if desc else name, # Fallback to name if desc empty
                year=year,
                genre=genre,
                manufacturer=manufacturer
            ))
        return games
