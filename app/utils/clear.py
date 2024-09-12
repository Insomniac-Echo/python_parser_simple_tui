import os

def clear_console():
    # Для Windows
    if os.name == 'nt':
        os.system('cls')
    # Для Linux и macOS
    else:
        os.system('clear')
