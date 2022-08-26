from distutils.util import strtobool

def input_bool(x):
    x = strtobool(x)  # True returns 1, False returns 0
    if x: return True  # if 1 executes return True
    else: return False