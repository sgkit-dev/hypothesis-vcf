def str_is_int(x: str) -> bool:
    """Test if a string can be parsed as an int"""
    try:
        int(x)
        return True
    except ValueError:
        return False
