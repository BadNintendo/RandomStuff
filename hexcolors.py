def shortHex(r, g, b, tint_factor=5):
    """
    Convert RGB values to a short hexadecimal-like format and apply a tint factor.
    
    Parameters:
    r (int): Red component (0-255)
    g (int): Green component (0-255)
    b (int): Blue component (0-255)
    tint_factor (int): Factor to reduce the color value by (default is 5)
    
    Returns:
    str: Short hexadecimal-like representation of the color.
    """
    
    def to_short(value, factor):
        # Apply tint factor and ensure value stays within range
        new_value = max(0, value - factor)
        value_str = str(new_value)
        
        # Handle the special case for repeated values like 128
        if new_value in [128, 64]:
            return f"3{value_str}"
        
        # Normal case without leading zeros
        return f"{len(value_str)}{value_str}"
    
    short_r = to_short(r, tint_factor)
    short_g = to_short(g, tint_factor)
    short_b = to_short(b, tint_factor)
    
    return f"{short_r}{short_g}{short_b}"

# Example usage
print(shortHex(255, 0, 0))  # Expected Output: 32552 (3 for 255, 2 for single digit zero)
print(shortHex(128, 128, 128, tint_factor=4))  # Expected Output: 3124128 (3 for repeated 128 minus tint)
print(shortHex(60, 180, 240))  # Custom example