from pathlib import Path

def show_help():
    file_path = Path('app/src/help.txt')
    with file_path.open('r') as file:
        help_text = file.read()
    print(help_text)