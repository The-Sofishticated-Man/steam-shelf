from core.utils.shortcut_utils import generate_shortcut_appid


def test_generate_shortcut_appid():
    """Test that generate_shortcut_appid produces consistent results."""
    name = "Test Game"
    exe = "/path/to/game.exe"
    
    # Should produce the same result for same inputs
    appid1 = generate_shortcut_appid(name, exe)
    appid2 = generate_shortcut_appid(name, exe)
    
    assert appid1 == appid2
    assert isinstance(appid1, int)
    # Should have the high bit set (0x80000000)
    assert appid1 & 0x80000000 != 0


def test_generate_shortcut_appid_different_inputs():
    """Test that different inputs produce different app IDs."""
    appid1 = generate_shortcut_appid("Game A", "/path/a.exe")
    appid2 = generate_shortcut_appid("Game B", "/path/b.exe")
    appid3 = generate_shortcut_appid("Game A", "/path/b.exe")  # Same name, different exe
    
    assert appid1 != appid2
    assert appid1 != appid3
    assert appid2 != appid3


def test_generate_shortcut_appid_known_values():
    """Test with known values to ensure algorithm is correct."""
    # Test with simple inputs
    name = "TestGame"
    exe = "test.exe"
    
    appid = generate_shortcut_appid(name, exe)
    
    # The algorithm should be: zlib.crc32((exe + name).encode('utf-8')) & 0xFFFFFFFF | 0x80000000
    import zlib
    key = exe + name  # "test.exeTestGame"
    expected_crc = zlib.crc32(key.encode('utf-8')) & 0xFFFFFFFF
    expected_appid = expected_crc | 0x80000000
    
    assert appid == expected_appid
