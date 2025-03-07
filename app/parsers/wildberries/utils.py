import re

#Функция для получения числа 'basket' для получения ссылки на изображение.
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
    else:
        return "19" 

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
