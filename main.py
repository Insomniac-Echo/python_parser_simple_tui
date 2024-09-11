#!/usr/bin/env python3

from app.start import parse_start
from app.clear import clear_console

def main():
    while True:
        print("Список доступных команд: \n1) help - страница помощи \n2) parse - начало работы \n3) quit - выход")
        command = input("Введите команду:")
        if command in ['help', '1']:
            clear_console()
            print("help placeholder")
            input("Нажмите ENTER, чтобы вернуться обратно")
            clear_console()
        elif command in ['parse', '2']:
            parse_start()
        elif command in ['quit', '3']:
            clear_console()
            print("Завершение работы.")
            break
        else:
            clear_console()
            print("Неизвестная команда.")
        
if __name__ == '__main__':
    main()