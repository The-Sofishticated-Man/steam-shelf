import zlib

def generate_shortcut_appid(name: str, exe: str) -> int:
    """Generate a shortcut app ID for non-Steam games.
    
    This function generates a unique app ID for non-Steam games using
    the same algorithm that Steam uses internally for shortcuts.
    
    Args:
        name: The name of the game
        exe: The executable path/name of the game
        
    Returns:
        A unique 32-bit app ID for the non-Steam game
    """
    key = exe + name
    crc = zlib.crc32(key.encode('utf-8')) & 0xFFFFFFFF
    appid = crc | 0x80000000
    return appid
