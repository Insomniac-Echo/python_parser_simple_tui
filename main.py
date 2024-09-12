#!/usr/bin/env python3

from app.utils.start import parse_start
from app.utils.clear import clear_console
from app.utils.help import show_help

def main():
    while True:
        print("Список доступных команд: \n1) help - Страница помощи \n2) parse - Начало работы \n3) quit - Выход")
        command = input("Введите команду: ")
        if command in ['help', '1']:
            clear_console()
            show_help()
            input("Нажмите ENTER, чтобы вернуться в главное меню.")
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