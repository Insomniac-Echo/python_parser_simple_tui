import sys
from app.ozon import ozon_parser
from app.wildberries import wb_parser


def parse_start():
    while True:
        print("1) Wildberries \n2) Ozon \n3) Back")
        command = input("Выберите площадку: ")
        if command in ['wildberries', 'wb', '1']:
            wb_parser()
            sys.exit()
        elif command in ['ozon', 'oz', '2']:
            ozon_parser()
            sys.exit()
        elif command in ['back', '3']:
            print("Переход в главное меню")
            print("Список доступных команд: \n1) help - страница помощи \n2) parse - начало работы \n3) quit - выход")
            break
        else:
            print("Неверная команда.")