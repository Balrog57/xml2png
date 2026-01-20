import requests
import os
import sys
import subprocess
import tempfile
from packaging import version
from PyQt6.QtWidgets import QMessageBox

class Updater:
    def __init__(self, current_version, repo_owner="Balrog57", repo_name="xml2png"):
        self.current_version = current_version
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    
    def check_for_updates(self):
        """
        Checks for updates. Returns (is_available, latest_version, download_url)
        """
        try:
            print(f"Checking for updates against {self.api_url}...")
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            latest_tag = data.get("tag_name", "v0.0.0")
            latest_version_str = latest_tag.lstrip("v")
            
            if version.parse(latest_version_str) > version.parse(self.current_version):
                # Find asset
                assets = data.get("assets", [])
                download_url = None
                for asset in assets:
                    # Look for the installer
                    if "Setup" in asset["name"] and asset["name"].endswith(".exe"):
                         download_url = asset["browser_download_url"]
                         break
                
                # If specific setup not found, try any exe? No, safer to be specific or fallback to first exe
                if not download_url:
                     for asset in assets:
                         if asset["name"].endswith(".exe"):
                             download_url = asset["browser_download_url"]
                             break

                return True, latest_version_str, download_url
            
        except Exception as e:
            print(f"Update check failed: {e}")
            
        return False, None, None

    def download_and_install(self, url):
        try:
            print(f"Downloading update from {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Save to temp
            fd, path = tempfile.mkstemp(suffix=".exe")
            with os.fdopen(fd, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Installer saved to {path}. Launching...")
            # Run Installer
            # Using Popen to launch and detach slightly
            subprocess.Popen([path])
            
            return True
            
        except Exception as e:
            print(f"Download failed: {e}")
            return False
