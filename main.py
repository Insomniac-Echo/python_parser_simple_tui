#!/usr/bin/env python3

from app.start import parse_start

def main():
    print("Список доступных команд: \n1) help - страница помощи \n2) parse - начало работы \n3) quit - выход")
    while True:
        command = input("Введите команду:")
        if command in ['help', '1']:
            print("help placeholder")
        elif command in ['parse', '2']:
            parse_start()
        elif command in ['quit', '3']:
            print("Завершение работы.")
            break
        else:
            print("Неизвестная команда.")
        
if __name__ == '__main__':
    main()