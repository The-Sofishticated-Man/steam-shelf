from pathlib import Path
from typing import List

class GameValidator:
    def __init__(self, blacklisted_dirs: set, blacklisted_exes: set):
        self.blacklisted_dirs = blacklisted_dirs
        self.blacklisted_exes = blacklisted_exes
    
    def is_valid_directory(self, directory: Path) -> bool:
        """Check if directory is valid for game discovery."""
        if not directory.is_dir():
            return False
            
        if directory.name.lower() in self.blacklisted_dirs:
            return False
            
        return True
    
    def filter_executables(self, exe_files: List[Path]) -> List[Path]:
        """Filter executables based on blacklisted keywords."""
        return [
            exe for exe in exe_files
            if not any(skip in exe.name.lower() for skip in self.blacklisted_exes)
        ]
    
    def find_main_executable(self, valid_exes: List[Path], game_name: str) -> Path:
        """Find the most likely main executable for a game."""
        if not valid_exes:
            raise ValueError("No valid executables found")
            
        # First priority: exact name match
        for exe in valid_exes:
            if exe.stem.lower() == game_name.lower():
                return exe
        
        # Second priority: biggest file (likely main executable)
        return max(valid_exes, key=lambda f: f.stat().st_size)
