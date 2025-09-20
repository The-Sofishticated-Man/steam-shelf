import pytest
import json
from pathlib import Path
from core.models.non_steam_game import NonSteamGame


class TestNonSteamGame:
    """Tests for NonSteamGame class."""
    
    def test_init_minimal(self):
        """Test NonSteamGame initialization with minimal parameters."""
        game = NonSteamGame(
            id=123456,
            name="Test Game",
            exe="/path/to/game.exe",
            dir="/path/to/game"
        )
        
        assert game.appid == 123456
        assert game.AppName == "Test Game"
        assert game.Exe == "/path/to/game.exe"
        assert game.StartDir == "/path/to/game"
        
        # Check default values
        assert game.icon == ""
        assert game.ShortcutPath == ""
        assert game.LaunchOptions == ""
        assert game.IsHidden == 0
        assert game.AllowDesktopConfig == 1
        assert game.AllowOverlay == 1
        assert game.OpenVR == 0
        assert game.Devkit == 0
        assert game.DevkitGameID == ""
        assert game.DevkitOverrideAppID == 0
        assert game.LastPlayTime == 0
        assert game.FlatpakAppID == ""
        assert game.tags == {}
    
    def test_init_all_parameters(self):
        """Test NonSteamGame initialization with all parameters."""
        tags = {"category": "Action", "favorite": True}
        
        game = NonSteamGame(
            id=123456,
            name="Test Game",
            exe="/path/to/game.exe",
            dir="/path/to/game",
            icon="/path/to/icon.ico",
            ShortcutPath="/path/to/shortcut",
            LaunchOptions="-windowed -debug",
            IsHidden=1,
            AllowDesktopConfig=0,
            AllowOverlay=0,
            OpenVR=1,
            Devkit=1,
            DevkitGameID="dev123",
            DevkitOverrideAppID=789,
            LastPlayTime=1234567890,
            FlatpakAppID="org.example.game",
            tags=tags
        )
        
        assert game.appid == 123456
        assert game.AppName == "Test Game"
        assert game.Exe == "/path/to/game.exe"
        assert game.StartDir == "/path/to/game"
        assert game.icon == "/path/to/icon.ico"
        assert game.ShortcutPath == "/path/to/shortcut"
        assert game.LaunchOptions == "-windowed -debug"
        assert game.IsHidden == 1
        assert game.AllowDesktopConfig == 0
        assert game.AllowOverlay == 0
        assert game.OpenVR == 1
        assert game.Devkit == 1
        assert game.DevkitGameID == "dev123"
        assert game.DevkitOverrideAppID == 789
        assert game.LastPlayTime == 1234567890
        assert game.FlatpakAppID == "org.example.game"
        assert game.tags == tags
    
    def test_from_candidate(self):
        """Test creating NonSteamGame from GameCandidate."""
        from collections import namedtuple
        
        # Create a mock GameCandidate
        GameCandidate = namedtuple('GameCandidate', 
                                   ['shortcut_id', 'name', 'exe_path', 'start_dir'])
        
        candidate = GameCandidate(
            shortcut_id=987654321,
            name="Test Game",
            exe_path=Path("/path/to/game.exe"),
            start_dir=Path("/path/to/game")
        )
        
        game = NonSteamGame.from_candidate(candidate)
        
        assert game.appid == 987654321
        assert game.AppName == "Test Game"
        assert game.Exe == str(candidate.exe_path)  # Use str() for cross-platform compatibility
        assert game.StartDir == str(candidate.start_dir)
        
        # Should have default values for other fields
        assert game.icon == ""
        assert game.IsHidden == 0
        assert game.AllowOverlay == 1
    
    def test_str_representation(self):
        """Test string representation of NonSteamGame."""
        game = NonSteamGame(
            id=123456,
            name="Test Game",
            exe="/path/to/game.exe",
            dir="/path/to/game"
        )
        
        str_repr = str(game)
        
        # Should be valid JSON
        parsed = json.loads(str_repr)
        
        assert parsed["name"] == "Test Game"
        assert parsed["steamID"] == 123456
        assert parsed["exe"] == "/path/to/game.exe"
        assert parsed["StartDir"] == "/path/to/game"
        
        # Should be formatted (indented)
        assert "\n" in str_repr
        assert "    " in str_repr
    
    def test_as_dict(self):
        """Test dictionary representation of NonSteamGame."""
        tags = {"genre": "RPG"}
        
        game = NonSteamGame(
            id=123456,
            name="Test Game",
            exe="/path/to/game.exe",
            dir="/path/to/game",
            icon="/path/to/icon.ico",
            LaunchOptions="-fullscreen",
            tags=tags
        )
        
        game_dict = game.as_dict()
        
        # Should contain all attributes
        assert game_dict["appid"] == 123456
        assert game_dict["AppName"] == "Test Game"
        assert game_dict["Exe"] == "/path/to/game.exe"
        assert game_dict["StartDir"] == "/path/to/game"
        assert game_dict["icon"] == "/path/to/icon.ico"
        assert game_dict["LaunchOptions"] == "-fullscreen"
        assert game_dict["tags"] == tags
        
        # Should contain all other attributes with default values
        assert game_dict["IsHidden"] == 0
        assert game_dict["AllowOverlay"] == 1
        assert game_dict["OpenVR"] == 0


class TestNonSteamGameEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_unicode_name(self):
        """Test NonSteamGame with Unicode characters in name."""
        game = NonSteamGame(
            id=123456,
            name="测试游戏 🎮",
            exe="/path/to/game.exe",
            dir="/path/to/game"
        )
        
        assert game.AppName == "测试游戏 🎮"
        
        # String representation should handle Unicode
        str_repr = str(game)
        parsed = json.loads(str_repr)
        assert parsed["name"] == "测试游戏 🎮"
    
    def test_windows_paths(self):
        """Test NonSteamGame with Windows-style paths."""
        game = NonSteamGame(
            id=123456,
            name="Test Game",
            exe="C:\\Games\\Test Game\\game.exe",
            dir="C:\\Games\\Test Game",
            icon="C:\\Games\\Test Game\\icon.ico"
        )
        
        assert game.Exe == "C:\\Games\\Test Game\\game.exe"
        assert game.StartDir == "C:\\Games\\Test Game"
        assert game.icon == "C:\\Games\\Test Game\\icon.ico"
    
    def test_quoted_exe_path(self):
        """Test NonSteamGame with quoted executable path."""
        game = NonSteamGame(
            id=123456,
            name="Test Game",
            exe="\"C:\\Games\\Test Game\\game.exe\"",
            dir="C:\\Games\\Test Game"
        )
        
        assert game.Exe == "\"C:\\Games\\Test Game\\game.exe\""
    
    def test_empty_strings(self):
        """Test NonSteamGame with empty strings."""
        game = NonSteamGame(
            id=123456,
            name="",
            exe="",
            dir=""
        )
        
        assert game.AppName == ""
        assert game.Exe == ""
        assert game.StartDir == ""
        
        # Should still work with string representation
        str_repr = str(game)
        parsed = json.loads(str_repr)
        assert parsed["name"] == ""
    
    def test_zero_and_negative_values(self):
        """Test NonSteamGame with zero and negative values."""
        game = NonSteamGame(
            id=0,
            name="Test Game",
            exe="/path/to/game.exe",
            dir="/path/to/game",
            LastPlayTime=-1,
            DevkitOverrideAppID=-999
        )
        
        assert game.appid == 0
        assert game.LastPlayTime == -1
        assert game.DevkitOverrideAppID == -999
    
    def test_complex_tags(self):
        """Test NonSteamGame with complex tags structure."""
        complex_tags = {
            "categories": ["Action", "RPG"],
            "metadata": {
                "rating": 4.5,
                "playtime": 120
            },
            "flags": {
                "completed": True,
                "favorite": False
            }
        }
        
        game = NonSteamGame(
            id=123456,
            name="Test Game",
            exe="/path/to/game.exe",
            dir="/path/to/game",
            tags=complex_tags
        )
        
        assert game.tags == complex_tags
        
        # Should preserve complex structure in as_dict
        game_dict = game.as_dict()
        assert game_dict["tags"] == complex_tags
        
        # Should handle in string representation
        str_repr = str(game)
        assert "Test Game" in str_repr
    
    def test_very_long_paths(self):
        """Test NonSteamGame with very long file paths."""
        long_path = "C:\\" + "very_long_directory_name\\" * 10 + "game.exe"
        
        game = NonSteamGame(
            id=123456,
            name="Test Game",
            exe=long_path,
            dir=long_path[:-8]  # Remove "game.exe"
        )
        
        assert game.Exe == long_path
        assert len(game.Exe) > 260  # Longer than Windows MAX_PATH
    
    def test_special_characters_in_paths(self):
        """Test NonSteamGame with special characters in paths."""
        game = NonSteamGame(
            id=123456,
            name="Test & Game (2023)",
            exe="/path/to/game & more/game.exe",
            dir="/path/to/game & more",
            LaunchOptions="--option=\"value with spaces\" --flag"
        )
        
        assert game.AppName == "Test & Game (2023)"
        assert game.Exe == "/path/to/game & more/game.exe"
        assert game.LaunchOptions == "--option=\"value with spaces\" --flag"


class TestNonSteamGameIntegration:
    """Integration tests for NonSteamGame with other components."""
    
    def test_steam_shortcuts_compatibility(self):
        """Test that NonSteamGame produces Steam-compatible data."""
        game = NonSteamGame(
            id=2789567361,  # Typical Steam shortcut ID
            name="isaac-ng",
            exe="\"H:\\Games\\Isaac\\isaac-ng.exe\"",
            dir="H:\\Games\\Isaac\\",
            icon="",
            ShortcutPath="",
            LaunchOptions="",
            IsHidden=0,
            AllowDesktopConfig=1,
            AllowOverlay=1,
            OpenVR=0,
            Devkit=0,
            DevkitGameID="",
            DevkitOverrideAppID=0,
            LastPlayTime=0,
            FlatpakAppID="",
            tags={}
        )
        
        game_dict = game.as_dict()
        
        # Verify all Steam shortcut fields are present
        required_fields = [
            "appid", "AppName", "Exe", "StartDir", "icon", "ShortcutPath",
            "LaunchOptions", "IsHidden", "AllowDesktopConfig", "AllowOverlay",
            "OpenVR", "Devkit", "DevkitGameID", "DevkitOverrideAppID",
            "LastPlayTime", "FlatpakAppID", "tags"
        ]
        
        for field in required_fields:
            assert field in game_dict
        
        # Verify data types match Steam expectations
        assert isinstance(game_dict["appid"], int)
        assert isinstance(game_dict["AppName"], str)
        assert isinstance(game_dict["IsHidden"], int)
        assert isinstance(game_dict["AllowOverlay"], int)
        assert isinstance(game_dict["tags"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])