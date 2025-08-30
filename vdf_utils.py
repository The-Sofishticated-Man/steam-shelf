import struct

def parse_vdf(file_path):
    """
    Parse a binary VDF file and return a dictionary.
    
    Args:
        file_path (str): Path to the binary VDF file
        
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