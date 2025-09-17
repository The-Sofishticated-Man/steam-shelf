#!/usr/bin/env python3
"""Steam Shelf GUI entry point."""

import sys
import subprocess
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gui.main_window import SteamShelfGUI

def kill_steam_process():
    """Kill the Steam process if it's running."""
    try:
        subprocess.run(["taskkill", "/f", "/im", "steam.exe"], 
                      capture_output=True, check=False)
        print("Steam process killed (if it was running)")
    except Exception as killing_steam_error:
        print(f"Error killing Steam process: {killing_steam_error}")

if __name__ == "__main__":
    kill_steam_process()
    app = SteamShelfGUI()
    app.run()
