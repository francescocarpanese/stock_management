def is_positive_null_integer(s):
    try:
        num = int(s)
        return num >= 0
    except ValueError:
        return False
    
def is_positive_integer(s):
    try:
        num = int(s)
        return num > 0
    except ValueError:
        return False
    
