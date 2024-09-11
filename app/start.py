import sys
from app.ozon import ozon_parser
from app.wildberries import wb_parser
from app.clear import clear_console

def parse_start():
    while True:
        clear_console()
        print("1) Wildberries \n2) Ozon \n3) Back")
        command = input("Выберите площадку: ")
        if command in ['wildberries', 'wb', '1']:
            clear_console()
            wb_parser()
            sys.exit()
        elif command in ['ozon', 'oz', '2']:
            clear_console()
            ozon_parser()
            sys.exit()
        elif command in ['back', '3']:
            clear_console()
            break
        else:
            print("Неверная команда.")