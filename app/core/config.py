# Здесь задаются и используются в дальнейшем переменные окружения
# В Docker переменные передаются автоматически внешним .env файлом, алгоритм отработан
import os
from dotenv import load_dotenv

if os.getenv("ENV", "develop") != "prod":
    load_dotenv(".env.dev")
def get_sales_token():
    return os.getenv("SALES_API_TOKEN")

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
LIKESTATS_EMAIL = os.getenv("LIKESTATS_EMAIL")
LIKESTATS_PASS = os.getenv("LIKESTATS_PASS")

DATABASE_URL = f"mysql+aiomysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
