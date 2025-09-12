#!/usr/bin/env python3
"""Steam Shelf GUI entry point."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gui.main_window import SteamShelfGUI

if __name__ == "__main__":
    app = SteamShelfGUI()
    app.run()
