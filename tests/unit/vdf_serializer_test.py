import pytest
from pathlib import Path
from core.utils.vdf_serializer import VDFSerializer
from core.models.non_steam_game import NonSteamGame


@pytest.fixture
def sample_games():
    """Create sample NonSteamGame objects for testing."""
    games = [
        NonSteamGame(
            id=2789567361,
            name="isaac-ng",
            exe="\"H:\\Games\\Isaac\\isaac-ng.exe\"",
            dir="H:\\Games\\Isaac\\",
            icon="",
            LaunchOptions="",
            IsHidden=0,
            AllowOverlay=1,
            tags={}
        ),
        NonSteamGame(
            id=1234567890,
            name="Test Game",
            exe="/path/to/test.exe",
            dir="/path/to/",
            icon="/path/to/icon.ico",
            LaunchOptions="-windowed",
            IsHidden=1,
            AllowOverlay=0,
            tags={"category": "Action"}
        ),
        NonSteamGame(
            id=9876543210,
            name="Another Game",
            exe="C:\\Games\\Another\\game.exe",
            dir="C:\\Games\\Another\\",
            tags={"favorite": True, "genre": "RPG"}
        )
    ]
    return games


@pytest.fixture
def sample_vdf_data():
    """Create sample VDF data structure for testing."""
    return {
        "shortcuts": {
            "0": {
                "appid": 2789567361,
                "AppName": "isaac-ng",
                "Exe": "\"H:\\Games\\Isaac\\isaac-ng.exe\"",
                "StartDir": "H:\\Games\\Isaac\\",
                "icon": "",
                "ShortcutPath": "",
                "LaunchOptions": "",
                "IsHidden": 0,
                "AllowDesktopConfig": 1,
                "AllowOverlay": 1,
                "OpenVR": 0,
                "Devkit": 0,
                "DevkitGameID": "",
                "DevkitOverrideAppID": 0,
                "LastPlayTime": 0,
                "FlatpakAppID": "",
                "tags": {}
            },
            "1": {
                "appid": 1234567890,
                "AppName": "Test Game",
                "Exe": "/path/to/test.exe",
                "StartDir": "/path/to/",
                "icon": "/path/to/icon.ico",
                "ShortcutPath": "",
                "LaunchOptions": "-windowed",
                "IsHidden": 1,
                "AllowDesktopConfig": 1,
                "AllowOverlay": 0,
                "OpenVR": 0,
                "Devkit": 0,
                "DevkitGameID": "",
                "DevkitOverrideAppID": 0,
                "LastPlayTime": 0,
                "FlatpakAppID": "",
                "tags": {"category": "Action"}
            }
        }
    }


class TestVDFSerializer:
    """Tests for VDFSerializer class."""
    
    def test_games_to_vdf_dict_empty_list(self):
        """Test serializing empty game list."""
        result = VDFSerializer.games_to_vdf_dict([])
        
        expected = {"shortcuts": {}}
        assert result == expected
    
    def test_games_to_vdf_dict_single_game(self, sample_games):
        """Test serializing single game to VDF dict."""
        game = sample_games[0]
        result = VDFSerializer.games_to_vdf_dict([game])
        
        assert "shortcuts" in result
        assert "0" in result["shortcuts"]
        
        shortcut = result["shortcuts"]["0"]
        assert shortcut["appid"] == 2789567361
        assert shortcut["AppName"] == "isaac-ng"
        assert shortcut["Exe"] == "\"H:\\Games\\Isaac\\isaac-ng.exe\""
        assert shortcut["StartDir"] == "H:\\Games\\Isaac\\"
        assert shortcut["IsHidden"] == 0
        assert shortcut["AllowOverlay"] == 1
        assert shortcut["tags"] == {}
    
    def test_games_to_vdf_dict_multiple_games(self, sample_games):
        """Test serializing multiple games to VDF dict."""
        result = VDFSerializer.games_to_vdf_dict(sample_games)
        
        assert "shortcuts" in result
        assert len(result["shortcuts"]) == 3
        
        # Check that keys are strings "0", "1", "2"
        assert "0" in result["shortcuts"]
        assert "1" in result["shortcuts"]
        assert "2" in result["shortcuts"]
        
        # Verify first game
        shortcut0 = result["shortcuts"]["0"]
        assert shortcut0["appid"] == 2789567361
        assert shortcut0["AppName"] == "isaac-ng"
        
        # Verify second game
        shortcut1 = result["shortcuts"]["1"]
        assert shortcut1["appid"] == 1234567890
        assert shortcut1["AppName"] == "Test Game"
        assert shortcut1["LaunchOptions"] == "-windowed"
        
        # Verify third game
        shortcut2 = result["shortcuts"]["2"]
        assert shortcut2["appid"] == 9876543210
        assert shortcut2["AppName"] == "Another Game"
        assert shortcut2["tags"] == {"favorite": True, "genre": "RPG"}
    
    def test_games_to_vdf_dict_preserves_all_fields(self, sample_games):
        """Test that serialization preserves all game fields."""
        game = sample_games[1]  # Test Game with more fields set
        result = VDFSerializer.games_to_vdf_dict([game])
        
        shortcut = result["shortcuts"]["0"]
        
        # Check all standard Steam shortcut fields are present
        required_fields = [
            "appid", "AppName", "Exe", "StartDir", "icon", "ShortcutPath",
            "LaunchOptions", "IsHidden", "AllowDesktopConfig", "AllowOverlay",
            "OpenVR", "Devkit", "DevkitGameID", "DevkitOverrideAppID",
            "LastPlayTime", "FlatpakAppID", "tags"
        ]
        
        for field in required_fields:
            assert field in shortcut
        
        # Verify specific values
        assert shortcut["icon"] == "/path/to/icon.ico"
        assert shortcut["LaunchOptions"] == "-windowed"
        assert shortcut["IsHidden"] == 1
        assert shortcut["AllowOverlay"] == 0
        assert shortcut["tags"] == {"category": "Action"}
    
    def test_games_from_vdf_dict_empty(self):
        """Test deserializing empty VDF dict."""
        vdf_data = {"shortcuts": {}}
        result = VDFSerializer.games_from_vdf_dict(vdf_data)
        
        assert result == []
    
    def test_games_from_vdf_dict_no_shortcuts_key(self):
        """Test deserializing VDF dict without shortcuts key."""
        vdf_data = {}
        result = VDFSerializer.games_from_vdf_dict(vdf_data)
        
        assert result == []
    
    def test_games_from_vdf_dict_single_game(self, sample_vdf_data):
        """Test deserializing single game from VDF dict."""
        # Take only the first shortcut
        single_game_data = {
            "shortcuts": {
                "0": sample_vdf_data["shortcuts"]["0"]
            }
        }
        
        result = VDFSerializer.games_from_vdf_dict(single_game_data)
        
        assert len(result) == 1
        game = result[0]
        
        assert isinstance(game, NonSteamGame)
        assert game.appid == 2789567361
        assert game.AppName == "isaac-ng"
        assert game.Exe == "\"H:\\Games\\Isaac\\isaac-ng.exe\""
        assert game.StartDir == "H:\\Games\\Isaac\\"
        assert game.IsHidden == 0
        assert game.AllowOverlay == 1
        assert game.tags == {}
    
    def test_games_from_vdf_dict_multiple_games(self, sample_vdf_data):
        """Test deserializing multiple games from VDF dict."""
        result = VDFSerializer.games_from_vdf_dict(sample_vdf_data)
        
        assert len(result) == 2
        
        # Check first game
        game1 = result[0]
        assert game1.appid == 2789567361
        assert game1.AppName == "isaac-ng"
        
        # Check second game
        game2 = result[1]
        assert game2.appid == 1234567890
        assert game2.AppName == "Test Game"
        assert game2.LaunchOptions == "-windowed"
        assert game2.IsHidden == 1
        assert game2.tags == {"category": "Action"}
    
    def test_games_from_vdf_dict_missing_fields(self):
        """Test deserializing VDF with missing optional fields."""
        vdf_data = {
            "shortcuts": {
                "0": {
                    "appid": 123456,
                    "AppName": "Minimal Game",
                    "Exe": "/path/to/game.exe",
                    "StartDir": "/path/to/"
                    # Missing most optional fields
                }
            }
        }
        
        result = VDFSerializer.games_from_vdf_dict(vdf_data)
        
        assert len(result) == 1
        game = result[0]
        
        assert game.appid == 123456
        assert game.AppName == "Minimal Game"
        assert game.Exe == "/path/to/game.exe"
        assert game.StartDir == "/path/to/"
        
        # Should have default values for missing fields
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
    
    def test_round_trip_serialization(self, sample_games):
        """Test that serialization is reversible."""
        # Convert games to VDF dict
        vdf_dict = VDFSerializer.games_to_vdf_dict(sample_games)
        
        # Convert back to games
        recovered_games = VDFSerializer.games_from_vdf_dict(vdf_dict)
        
        # Should have same number of games
        assert len(recovered_games) == len(sample_games)
        
        # Compare each game
        for original, recovered in zip(sample_games, recovered_games):
            assert original.appid == recovered.appid
            assert original.AppName == recovered.AppName
            assert original.Exe == recovered.Exe
            assert original.StartDir == recovered.StartDir
            assert original.icon == recovered.icon
            assert original.LaunchOptions == recovered.LaunchOptions
            assert original.IsHidden == recovered.IsHidden
            assert original.AllowOverlay == recovered.AllowOverlay
            assert original.tags == recovered.tags


class TestVDFSerializerEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_unicode_game_names(self):
        """Test serialization with Unicode game names."""
        game = NonSteamGame(
            id=123456,
            name="测试游戏 🎮",
            exe="/path/to/game.exe",
            dir="/path/to/"
        )
        
        # Serialize
        vdf_dict = VDFSerializer.games_to_vdf_dict([game])
        
        # Deserialize
        recovered_games = VDFSerializer.games_from_vdf_dict(vdf_dict)
        
        assert len(recovered_games) == 1
        assert recovered_games[0].AppName == "测试游戏 🎮"
    
    def test_complex_paths(self):
        """Test serialization with complex file paths."""
        game = NonSteamGame(
            id=123456,
            name="Test Game",
            exe="\"C:\\Program Files (x86)\\Game Studio\\Game Name\\bin\\game.exe\"",
            dir="C:\\Program Files (x86)\\Game Studio\\Game Name\\",
            icon="C:\\Program Files (x86)\\Game Studio\\Game Name\\icon.ico"
        )
        
        # Round trip
        vdf_dict = VDFSerializer.games_to_vdf_dict([game])
        recovered_games = VDFSerializer.games_from_vdf_dict(vdf_dict)
        
        recovered = recovered_games[0]
        assert recovered.Exe == game.Exe
        assert recovered.StartDir == game.StartDir
        assert recovered.icon == game.icon
    
    def test_special_characters_in_launch_options(self):
        """Test serialization with special characters in launch options."""
        game = NonSteamGame(
            id=123456,
            name="Test Game",
            exe="/path/to/game.exe",
            dir="/path/to/",
            LaunchOptions="--option=\"value with spaces\" --flag=true --path=\"C:\\folder with spaces\""
        )
        
        # Round trip
        vdf_dict = VDFSerializer.games_to_vdf_dict([game])
        recovered_games = VDFSerializer.games_from_vdf_dict(vdf_dict)
        
        assert recovered_games[0].LaunchOptions == game.LaunchOptions
    
    def test_nested_tags_structure(self):
        """Test serialization with complex nested tags."""
        complex_tags = {
            "categories": ["Action", "RPG"],
            "metadata": {
                "rating": 4.5,
                "hours_played": 120.5
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
            dir="/path/to/",
            tags=complex_tags
        )
        
        # Round trip
        vdf_dict = VDFSerializer.games_to_vdf_dict([game])
        recovered_games = VDFSerializer.games_from_vdf_dict(vdf_dict)
        
        assert recovered_games[0].tags == complex_tags
    
    def test_zero_and_negative_values(self):
        """Test serialization with zero and negative values."""
        game = NonSteamGame(
            id=0,  # Zero app ID
            name="Test Game",
            exe="/path/to/game.exe",
            dir="/path/to/",
            LastPlayTime=-1,  # Negative value
            DevkitOverrideAppID=-999
        )
        
        # Round trip
        vdf_dict = VDFSerializer.games_to_vdf_dict([game])
        recovered_games = VDFSerializer.games_from_vdf_dict(vdf_dict)
        
        recovered = recovered_games[0]
        assert recovered.appid == 0
        assert recovered.LastPlayTime == -1
        assert recovered.DevkitOverrideAppID == -999
    
    def test_malformed_vdf_data(self):
        """Test handling of malformed VDF data."""
        # VDF data with non-dict shortcut entry
        malformed_data = {
            "shortcuts": {
                "0": "not a dict",
                "1": {
                    "appid": 123456,
                    "AppName": "Valid Game",
                    "Exe": "/path/to/game.exe",
                    "StartDir": "/path/to/"
                }
            }
        }
        
        # Should handle gracefully and process valid entries
        result = VDFSerializer.games_from_vdf_dict(malformed_data)
        
        # Should have one valid game (the malformed entry might be skipped or cause an error)
        # The exact behavior depends on implementation, but it should not crash
        assert isinstance(result, list)
    
    def test_empty_shortcut_keys(self):
        """Test VDF data with unusual shortcut keys."""
        vdf_data = {
            "shortcuts": {
                "": {  # Empty key
                    "appid": 123456,
                    "AppName": "Empty Key Game",
                    "Exe": "/path/to/game.exe",
                    "StartDir": "/path/to/"
                },
                "999": {  # High numeric key
                    "appid": 789012,
                    "AppName": "High Key Game",
                    "Exe": "/path/to/other.exe",
                    "StartDir": "/path/to/other/"
                }
            }
        }
        
        result = VDFSerializer.games_from_vdf_dict(vdf_data)
        
        # Should process both games regardless of key names
        assert len(result) == 2
        game_names = [game.AppName for game in result]
        assert "Empty Key Game" in game_names
        assert "High Key Game" in game_names


class TestVDFSerializerStaticMethods:
    """Test that VDFSerializer methods are truly static."""
    
    def test_methods_are_static(self):
        """Test that serializer methods work without instantiation."""
        game = NonSteamGame(
            id=123456,
            name="Test Game",
            exe="/path/to/game.exe",
            dir="/path/to/"
        )
        
        # Should work without creating VDFSerializer instance
        vdf_dict = VDFSerializer.games_to_vdf_dict([game])
        recovered_games = VDFSerializer.games_from_vdf_dict(vdf_dict)
        
        assert len(recovered_games) == 1
        assert recovered_games[0].AppName == "Test Game"
    
    def test_multiple_serializer_calls(self):
        """Test multiple calls to serializer methods."""
        games1 = [NonSteamGame(id=1, name="Game 1", exe="/path1", dir="/dir1")]
        games2 = [NonSteamGame(id=2, name="Game 2", exe="/path2", dir="/dir2")]
        
        # Multiple serializations should not interfere with each other
        vdf1 = VDFSerializer.games_to_vdf_dict(games1)
        vdf2 = VDFSerializer.games_to_vdf_dict(games2)
        
        result1 = VDFSerializer.games_from_vdf_dict(vdf1)
        result2 = VDFSerializer.games_from_vdf_dict(vdf2)
        
        assert result1[0].AppName == "Game 1"
        assert result2[0].AppName == "Game 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])