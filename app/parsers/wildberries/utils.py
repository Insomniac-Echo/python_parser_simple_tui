import re

#Функция для получения числа 'basket' для получения ссылки на изображение. ссылка в которой есть все значения баскетов https://static-basket-01.wbbasket.ru/vol2/site/j/spa/index.67ffbe076a38f980d963.js
def get_basket_number(id):
    vol = id // 100000
    if 0 <= vol <= 143:
        return "01"
    elif 144 <= vol <= 287:
        return "02"
    elif 288 <= vol <= 431:
        return "03"
    elif 432 <= vol <= 719:
        return "04"
    elif 720 <= vol <= 1007:
        return "05"
    elif 1008 <= vol <= 1061:
        return "06"
    elif 1062 <= vol <= 1115:
        return "07"
    elif 1116 <= vol <= 1169:
        return "08"
    elif 1170 <= vol <= 1313:
        return "09"
    elif 1314 <= vol <= 1601:
        return "10"
    elif 1602 <= vol <= 1655:
        return "11"
    elif 1656 <= vol <= 1919:
        return "12"
    elif 1920 <= vol <= 2045:
        return "13"
    elif 2046 <= vol <= 2189:
        return "14"
    elif 2190 <= vol <= 2405:
        return "15"         
    elif 2406 <= vol <= 2621: 
        return "16"
    elif 2622 <= vol <= 2837:
        return "17" 
    elif 2838 <= vol <= 3053:
        return "18"
    elif 3054 <= vol <= 3269:
        return "19"
    elif 3270 <= vol <= 3485:
        return "20"
    elif 3486 <= vol <= 3701:
        return "21"
    elif 3702 <= vol <= 3917:
        return "22"
    elif 3918 <= vol <= 4133:
        return "23"
    elif 4134 <= vol <= 4349:
        return "24"
    elif 4350 <= vol <= 4565:
        return "25"
    elif 4566 <= vol <= 4877:
        return "26"
    elif 4878 <= vol <= 5189:
        return "27"
    elif 5190 <= vol <= 5501:
        return "28"
    else:
        return "29" 
    
def get_review_basket_number(photo_id):
    vol = photo_id // 1000000
    if 0 <= photo_id <= 4:
        return "01"
    elif 20 <= photo_id <= 35:
        return "02"
    elif 40 <= photo_id <= 54:
        return "03"
    elif 70 <= photo_id <= 113:
        return "04"
    elif 114 <= photo_id <= 125:
        return "05"
    elif 126 <= photo_id <= 137:
        return "06"
    elif 138 <= photo_id <= 149:
        return "07"
    else:
        return "08"

#Как я понял, функция, которая обрабатывает одно из полей для исключения эмоджи.
def remove_emojis(text):
    emoji_remove = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_remove.sub(r'', text)
