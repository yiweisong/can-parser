def parse_hex_string(hex_str: str) -> bytes:
    if not isinstance(hex_str, str):
        return b''
    
    # Handle "x| " prefix
    cleaned = hex_str.strip()
    if cleaned.lower().startswith("x|"):
        cleaned = cleaned[2:].strip()
        
    # Remove spaces
    cleaned = cleaned.replace(" ", "")
    
    try:
        return bytes.fromhex(cleaned)
    except ValueError:
        return b''
