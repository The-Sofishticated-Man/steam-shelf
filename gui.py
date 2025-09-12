#!/usr/bin/env python3
"""Legacy GUI entry point - Use scripts/steam-shelf-gui.py instead."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from gui.main_window import SteamShelfGUI

if __name__ == "__main__":
    print("Warning: This is a legacy entry point.")
    print("Please use: python scripts/steam-shelf-gui.py")
    print("Starting GUI anyway...\n")
    
    app = SteamShelfGUI()
    app.run()