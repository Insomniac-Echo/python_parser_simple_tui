async def get_description(session, id, basket_number, name):
    if basket_number in ["01"]:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:2]}/part{str(id)[:4]}/{str(id)}/info/ru/card.json"
    elif basket_number in ["02", "03", "04", "05"]:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:3]}/part{str(id)[:5]}/{str(id)}/info/ru/card.json"
    else:
        url = f"https://basket-{basket_number}.wbbasket.ru/vol{str(id)[:4]}/part{str(id)[:6]}/{str(id)}/info/ru/card.json"
    try:
        response = await session.get(url, impersonate="chrome")
        if response.status_code != 200:
            logger.error(f"Status code other than 200. Local or Server error? Status code: {response.status_code}")
            return None
        desc = response.json()   
        if "description" in desc:
            return desc["description"]
        else:
            logger.warning(f"Description not found for {name}")
            return None
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logger.error(f"Error occurred: {e}")
        return None
