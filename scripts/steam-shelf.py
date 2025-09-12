#!/usr/bin/env python3
"""Steam Shelf CLI entry point."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cli.commands import main

if __name__ == "__main__":
    main()
