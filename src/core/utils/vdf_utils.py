from pathlib import Path
import struct

def parse_vdf(file_path:Path)->dict:
    """
    Parse a binary VDF file and return a dictionary.
    
    Args:
        file_path (Path): Path to the binary VDF file
        
    Returns:
        dict: Parsed VDF data
    """
    with open(file_path, 'rb') as f:
        data = f.read()
    
    offset = 0
    length = len(data)
    
    def read_byte():
        nonlocal offset
        if offset >= length:
            return None
        byte = data[offset]
        offset += 1
        return byte
    
    def read_cstring():
        nonlocal offset
        start = offset
        while offset < length and data[offset] != 0:
            offset += 1
        if offset >= length:
            return ""
        string_data = data[start:offset]
        offset += 1  # Skip null terminator
        try:
            return string_data.decode('utf-8', errors='replace')
        except:
            return string_data.decode('latin1', errors='replace')
    
    def read_int32():
        nonlocal offset
        if offset + 4 > length:
            return 0
        value = struct.unpack('<I', data[offset:offset + 4])[0]
        offset += 4
        return value
    
    def read_int64():
        nonlocal offset
        if offset + 8 > length:
            return 0
        value = struct.unpack('<Q', data[offset:offset + 8])[0]
        offset += 8
        return value
    
    def read_float32():
        nonlocal offset
        if offset + 4 > length:
            return 0.0
        value = struct.unpack('<f', data[offset:offset + 4])[0]
        offset += 4
        return value
    
    def parse_section():
        result = {}
        
        while offset < length:
            data_type = read_byte()
            if data_type is None or data_type == 0x08:  # End of section
                break
            
            key = read_cstring()
            if not key and data_type != 0x00:
                continue
            
            if data_type == 0x00:  # Subsection
                if not key:
                    key = f"_subsection_{len(result)}"
                result[key] = parse_section()
            elif data_type == 0x01:  # String
                result[key] = read_cstring()
            elif data_type == 0x02:  # Int32
                result[key] = read_int32()
            elif data_type == 0x03:  # Float32
                result[key] = read_float32()
            elif data_type == 0x07:  # Int64
                result[key] = read_int64()
            else:  # Unknown type, try as string
                try:
                    result[key] = read_cstring()
                except:
                    continue
        
        return result
    
    return parse_section()



def write_binary_vdf(data:dict, path:Path):
    """
    Encode a dictionary to binary VDF format and write to file.
    
    Args:
        data (dict): Dictionary to encode
        file_path (Path): Path where to save the binary VDF file
    """
    
    def write_cstring(string):
        """Encode string as null-terminated UTF-8"""
        if isinstance(string, str):
            return string.encode('utf-8', errors='replace') + b'\x00'
        return str(string).encode('utf-8', errors='replace') + b'\x00'
    
    def encode_value(key, value):
        """Encode a key-value pair"""
        result = b''
        
        if isinstance(value, dict):
            # Subsection
            result += b'\x00'  # Subsection type
            result += write_cstring(key)
            for sub_key, sub_value in value.items():
                result += encode_value(sub_key, sub_value)
            result += b'\x08'  # End of subsection
        
        elif isinstance(value, str):
            # String
            result += b'\x01'  # String type
            result += write_cstring(key)
            result += write_cstring(value)
        
        elif isinstance(value, int):
            # Determine if int32 or int64 based on value range
            if -2147483648 <= value <= 4294967295:  # Int32 range
                result += b'\x02'  # Int32 type
                result += write_cstring(key)
                result += struct.pack('<I', value & 0xFFFFFFFF)
            else:  # Int64
                result += b'\x07'  # Int64 type
                result += write_cstring(key)
                result += struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF)
        
        elif isinstance(value, float):
            # Float32
            result += b'\x03'  # Float32 type
            result += write_cstring(key)
            result += struct.pack('<f', value)
        
        else:
            # Convert to string as fallback
            result += b'\x01'  # String type
            result += write_cstring(key)
            result += write_cstring(str(value))
        
        return result
    
    # Build the binary data
    binary_data = b''
    
    # Encode all root-level key-value pairs
    for key, value in data.items():
        binary_data += encode_value(key, value)
    
    # Add final end marker
    binary_data += b'\x08'
    
    # Write to file
    with open(path, 'wb') as f:
        f.write(binary_data)