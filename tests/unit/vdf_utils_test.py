import pytest
import tempfile
import os
import struct
from core.utils.vdf_utils import parse_vdf, write_binary_vdf  


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)


@pytest.fixture
def create_vdf_file(temp_dir):
    """Helper fixture to create VDF test files"""
    def _create_file(content_bytes, filename="test.vdf"):
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(content_bytes)
        return file_path
    return _create_file


class TestVDFParser:
    """Tests for the parse_vdf function"""
    
    def test_parse_empty_file(self, create_vdf_file):
        """Test parsing an empty file"""
        file_path = create_vdf_file(b'\x08')  # Just end marker
        result = parse_vdf(file_path)
        assert result == {}
    
    def test_parse_single_string(self, create_vdf_file):
        """Test parsing a single string value"""
        content = b'\x01' + b'name\x00' + b'test\x00' + b'\x08'
        file_path = create_vdf_file(content)
        
        result = parse_vdf(file_path)
        expected = {"name": "test"}
        assert result == expected
    
    def test_parse_single_integer(self, create_vdf_file):
        """Test parsing a single integer value"""
        content = b'\x02' + b'appid\x00' + struct.pack('<I', 440) + b'\x08'
        file_path = create_vdf_file(content)
        
        result = parse_vdf(file_path)
        expected = {"appid": 440}
        assert result == expected
    
    def test_parse_single_float(self, create_vdf_file):
        """Test parsing a single float value"""
        content = b'\x03' + b'rating\x00' + struct.pack('<f', 4.5) + b'\x08'
        file_path = create_vdf_file(content)
        
        result = parse_vdf(file_path)
        expected = {"rating": 4.5}
        assert abs(result["rating"] - expected["rating"]) < 0.001
    
    def test_parse_large_integer(self, create_vdf_file):
        """Test parsing a 64-bit integer"""
        large_int = 9223372036854775807
        content = b'\x07' + b'timestamp\x00' + struct.pack('<Q', large_int) + b'\x08'
        file_path = create_vdf_file(content)
        
        result = parse_vdf(file_path)
        expected = {"timestamp": large_int}
        assert result == expected
    
    def test_parse_mixed_data_types(self, create_vdf_file):
        """Test parsing different data types together"""
        content = bytearray()
        content.extend(b'\x01' + b'name\x00' + b'Team Fortress 2\x00')  # String
        content.extend(b'\x02' + b'appid\x00' + struct.pack('<I', 440))  # Int32
        content.extend(b'\x03' + b'rating\x00' + struct.pack('<f', 4.5))  # Float
        content.extend(b'\x08')  # End
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        assert result["name"] == "Team Fortress 2"
        assert result["appid"] == 440
        assert abs(result["rating"] - 4.5) < 0.001
    
    def test_parse_nested_sections(self, create_vdf_file):
        """Test parsing nested subsections"""
        content = bytearray()
        # Root section "AppInfo"
        content.extend(b'\x00' + b'AppInfo\x00')
        content.extend(b'\x01' + b'name\x00' + b'Test Game\x00')
        # Nested section "config"
        content.extend(b'\x00' + b'config\x00')
        content.extend(b'\x01' + b'launch_type\x00' + b'0\x00')
        content.extend(b'\x08')  # End of config
        content.extend(b'\x08')  # End of AppInfo
        content.extend(b'\x08')  # End of root
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        expected = {
            "AppInfo": {
                "name": "Test Game",
                "config": {
                    "launch_type": "0"
                }
            }
        }
        assert result == expected
    
    def test_parse_steam_shortcuts_structure(self, create_vdf_file):
        """Test parsing a Steam shortcuts-like structure"""
        content = bytearray()
        
        # shortcuts section
        content.extend(b'\x00' + b'shortcuts\x00')
        
        # First shortcut "0"
        content.extend(b'\x00' + b'0\x00')
        content.extend(b'\x02' + b'appid\x00' + struct.pack('<I', 2789567361))
        content.extend(b'\x01' + b'AppName\x00' + b'isaac-ng\x00')
        content.extend(b'\x01' + b'Exe\x00' + b'game.exe\x00')
        content.extend(b'\x02' + b'IsHidden\x00' + struct.pack('<I', 0))
        
        # Empty tags section
        content.extend(b'\x00' + b'tags\x00')
        content.extend(b'\x08')  # End of tags
        
        content.extend(b'\x08')  # End of shortcut "0"
        content.extend(b'\x08')  # End of shortcuts
        content.extend(b'\x08')  # End of root
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        expected = {
            "shortcuts": {
                "0": {
                    "appid": 2789567361,
                    "AppName": "isaac-ng",
                    "Exe": "game.exe",
                    "IsHidden": 0,
                    "tags": {}
                }
            }
        }
        assert result == expected
    
    def test_parse_unicode_strings(self, create_vdf_file):
        """Test parsing Unicode strings"""
        unicode_name = "测试游戏"  # Chinese characters
        content = b'\x01' + b'name\x00' + unicode_name.encode('utf-8') + b'\x00' + b'\x08'
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        expected = {"name": unicode_name}
        assert result == expected
    
    def test_parse_empty_strings(self, create_vdf_file):
        """Test parsing empty strings"""
        content = b'\x01' + b'icon\x00' + b'\x00' + b'\x08'  # Empty string
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        expected = {"icon": ""}
        assert result == expected
    
    def test_parse_file_not_found(self):
        """Test handling of non-existent files"""
        with pytest.raises(FileNotFoundError):
            parse_vdf("nonexistent.vdf")
    
    def test_parse_malformed_file(self, create_vdf_file):
        """Test handling of malformed/truncated files"""
        # Truncated file - starts a string but file ends
        content = b'\x01' + b'name\x00' + b'incomplete'  # No null terminator
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        # Should handle gracefully
        assert isinstance(result, dict)


class TestVDFEncoder:
    """Tests for the write_binary_vdf function"""
    
    def test_encode_simple_data(self, temp_dir):
        """Test encoding simple data"""
        data = {"name": "test", "appid": 440}
        file_path = os.path.join(temp_dir, "encode_test.vdf")
        
        write_binary_vdf(data, file_path)
        
        # Verify file was created and has content
        assert os.path.exists(file_path)
        with open(file_path, 'rb') as f:
            content = f.read()
        assert len(content) > 0
    
    def test_encode_nested_data(self, temp_dir):
        """Test encoding nested dictionary data"""
        data = {
            "AppInfo": {
                "name": "Test Game",
                "appid": 440
            }
        }
        file_path = os.path.join(temp_dir, "nested_test.vdf")
        
        write_binary_vdf(data, file_path)
        
        # Verify file exists
        assert os.path.exists(file_path)
    
    def test_encode_various_types(self, temp_dir):
        """Test encoding different data types"""
        data = {
            "string_val": "hello",
            "int32_val": 440,
            "int64_val": 9223372036854775807,
            "float_val": 3.14,
            "empty_string": "",
            "zero_int": 0
        }
        file_path = os.path.join(temp_dir, "types_test.vdf")
        
        write_binary_vdf(data, file_path)
        assert os.path.exists(file_path)


class TestRoundTrip:
    """Test that parse -> encode -> parse gives same result"""
    
    def test_round_trip_simple(self, temp_dir):
        """Test round trip with simple data"""
        original_data = {
            "name": "Half-Life",
            "appid": 70,
            "rating": 4.5
        }
        
        file_path = os.path.join(temp_dir, "round_trip.vdf")
        
        # Write original data
        write_binary_vdf(original_data, file_path)
        
        # Read it back
        parsed_data = parse_vdf(file_path)
        
        # Should be identical (except for float precision)
        assert parsed_data["name"] == original_data["name"]
        assert parsed_data["appid"] == original_data["appid"]
        assert abs(parsed_data["rating"] - original_data["rating"]) < 0.001
    
    def test_round_trip_nested(self, temp_dir):
        """Test round trip with nested data"""
        original_data = {
            "shortcuts": {
                "0": {
                    "appid": 2789567361,
                    "AppName": "isaac-ng",
                    "Exe": "game.exe",
                    "IsHidden": 0,
                    "tags": {}
                }
            }
        }
        
        file_path = os.path.join(temp_dir, "nested_round_trip.vdf")
        
        # Write and read back
        write_binary_vdf(original_data, file_path)
        parsed_data = parse_vdf(file_path)
        
        # Should be identical
        assert parsed_data == original_data
    
    def test_round_trip_steam_shortcuts(self, temp_dir):
        """Test round trip with real Steam shortcuts data"""
        original_data = {
            "shortcuts": {
                "0": {
                    "appid": 2789567361,
                    "AppName": "isaac-ng",
                    "Exe": "\"H:\\Games\\The-Binding-of-Isaac-R-SteamRIP.com\\The Binding of Isaac Repentance\\isaac-ng.exe\"",
                    "StartDir": "H:\\Games\\The-Binding-of-Isaac-R-SteamRIP.com\\The Binding of Isaac Repentance\\",
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
                }
            }
        }
        
        file_path = os.path.join(temp_dir, "steam_shortcuts.vdf")
        
        # Write and read back
        write_binary_vdf(original_data, file_path)
        parsed_data = parse_vdf(file_path)
        
        # Verify structure
        assert "shortcuts" in parsed_data
        assert "0" in parsed_data["shortcuts"]
        
        shortcut = parsed_data["shortcuts"]["0"]
        assert shortcut["appid"] == 2789567361
        assert shortcut["AppName"] == "isaac-ng"
        assert "isaac-ng.exe" in shortcut["Exe"]
        assert shortcut["IsHidden"] == 0


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_parse_zero_values(self, create_vdf_file):
        """Test parsing zero integers and empty strings"""
        content = bytearray()
        content.extend(b'\x02' + b'zero_int\x00' + struct.pack('<I', 0))
        content.extend(b'\x01' + b'empty_str\x00' + b'\x00')
        content.extend(b'\x08')
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        expected = {"zero_int": 0, "empty_str": ""}
        assert result == expected
    
    def test_parse_special_characters(self, create_vdf_file):
        """Test strings with special characters"""
        special_string = "path\\with\\backslashes and \"quotes\""
        content = b'\x01' + b'path\x00' + special_string.encode('utf-8') + b'\x00' + b'\x08'
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        assert result["path"] == special_string
    
    def test_parse_large_integers(self, create_vdf_file):
        """Test parsing large integers that require int64"""
        large_int = 9223372036854775807  # Max int64
        content = b'\x07' + b'big_num\x00' + struct.pack('<Q', large_int) + b'\x08'
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        assert result["big_num"] == large_int
    
    def test_parse_unicode_strings(self, create_vdf_file):
        """Test parsing Unicode strings"""
        unicode_name = "测试游戏 🎮"  # Chinese + emoji
        content = b'\x01' + b'name\x00' + unicode_name.encode('utf-8') + b'\x00' + b'\x08'
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        assert result["name"] == unicode_name
    
    def test_parse_deeply_nested(self, create_vdf_file):
        """Test parsing deeply nested structures"""
        content = bytearray()
        # Level 1
        content.extend(b'\x00' + b'level1\x00')
        # Level 2
        content.extend(b'\x00' + b'level2\x00')
        # Level 3
        content.extend(b'\x00' + b'level3\x00')
        content.extend(b'\x01' + b'deep_value\x00' + b'found it\x00')
        content.extend(b'\x08')  # End level 3
        content.extend(b'\x08')  # End level 2
        content.extend(b'\x08')  # End level 1
        content.extend(b'\x08')  # End root
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        assert result["level1"]["level2"]["level3"]["deep_value"] == "found it"
    
    def test_parse_malformed_file(self, create_vdf_file):
        """Test handling of malformed files"""
        # Truncated file
        content = b'\x01' + b'name\x00' + b'incomplete'  # No null terminator
        
        file_path = create_vdf_file(content)
        result = parse_vdf(file_path)
        
        # Should return a dict (even if incomplete)
        assert isinstance(result, dict)
    
    def test_file_not_found(self):
        """Test handling of non-existent files"""
        with pytest.raises(FileNotFoundError):
            parse_vdf("this_file_does_not_exist.vdf")


class TestDataIntegrity:
    """Test data integrity and specific values"""
    
    def test_integer_ranges(self, temp_dir):
        """Test various integer ranges"""
        test_cases = [
            ("small_int", 1, b'\x02'),      # Small positive
            ("zero", 0, b'\x02'),           # Zero
            ("large_int32", 4294967295, b'\x02'),  # Max uint32
            ("negative", -1, b'\x02'),      # Negative (stored as unsigned)
            ("huge_int", 9223372036854775807, b'\x07')  # Requires int64
        ]
        
        for name, value, expected_type in test_cases:
            file_path = os.path.join(temp_dir, f"{name}.vdf")
            
            # Test encoding
            data = {name: value}
            write_binary_vdf(data, file_path)
            
            # Test parsing
            result = parse_vdf(file_path)
            assert name in result
            
            # For negative numbers, they get stored as unsigned
            if value == -1:
                assert result[name] == 4294967295  # -1 as uint32
            else:
                assert result[name] == value
    
    def test_string_encoding(self, temp_dir):
        """Test various string encodings"""
        test_strings = [
            "simple",
            "",  # Empty
            "with spaces",
            "with\nnewlines\tand\ttabs",
            "unicode: 你好世界",
            "emojis: 🎮🎯⭐",
            "special chars: !@#$%^&*()",
            "quotes: \"hello\" 'world'",
            "backslashes: C:\\path\\to\\file"
        ]
        
        for i, test_string in enumerate(test_strings):
            file_path = os.path.join(temp_dir, f"string_{i}.vdf")
            
            data = {"test_string": test_string}
            write_binary_vdf(data, file_path)
            
            result = parse_vdf(file_path)
            assert result["test_string"] == test_string


@pytest.mark.parametrize("test_data", [
    {"simple": "value"},
    {"number": 123},
    {"float": 3.14},
    {"nested": {"inner": "value"}},
    {"empty_dict": {}},
    {"mixed": {"str": "hello", "num": 42, "nested": {"deep": "value"}}}
])
def test_round_trip_parametrized(test_data, temp_dir):
    """Parametrized test for round-trip data integrity"""
    file_path = os.path.join(temp_dir, "param_test.vdf")
    
    # Write and read back
    write_binary_vdf(test_data, file_path)
    result = parse_vdf(file_path)
    
    # Compare (handling float precision)
    def compare_dicts(d1, d2):
        if type(d1) != type(d2):
            return False
        if isinstance(d1, dict):
            if set(d1.keys()) != set(d2.keys()):
                return False
            return all(compare_dicts(d1[k], d2[k]) for k in d1.keys())
        elif isinstance(d1, float):
            return abs(d1 - d2) < 0.001
        else:
            return d1 == d2
    
    assert compare_dicts(result, test_data)


def test_real_world_steam_data(temp_dir):
    """Integration test with realistic Steam shortcuts data"""
    steam_data = {
        "shortcuts": {
            "0": {
                "appid": 2789567361,
                "AppName": "isaac-ng",
                "Exe": "\"H:\\Games\\The-Binding-of-Isaac-R-SteamRIP.com\\The Binding of Isaac Repentance\\isaac-ng.exe\"",
                "StartDir": "H:\\Games\\The-Binding-of-Isaac-R-SteamRIP.com\\The Binding of Isaac Repentance\\",
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
            }
        }
    }
    
    file_path = os.path.join(temp_dir, "real_world.vdf")
    
    # Full round trip
    write_binary_vdf(steam_data, file_path)
    result = parse_vdf(file_path)
    
    # Verify key fields
    shortcut = result["shortcuts"]["0"]
    assert shortcut["appid"] == 2789567361
    assert shortcut["AppName"] == "isaac-ng"
    assert "isaac-ng.exe" in shortcut["Exe"]
    assert shortcut["IsHidden"] == 0
    assert shortcut["AllowOverlay"] == 1
    assert isinstance(shortcut["tags"], dict)


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])