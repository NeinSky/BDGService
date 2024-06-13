import os
from dotenv import load_dotenv, find_dotenv
import logging


if not find_dotenv():
    exit("Файл .env не обнаружен в корне приложения. Завершение работы.")
else:
    load_dotenv()

# Настройки базы данных
DB_DRIVER = 'postgresql+asyncpg'
DB_HOST = '0.0.0.0'  # измените на название контейнера БД, если используется docker compile
DB_PORT = '5432'
DB_ECHO = False
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


# Настройки аутентификации
AUTH_SECRET_KEY = os.getenv('SECRET_KEY')
AUTH_ALGORITHM = "HS256"
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Администратор сервиса по умолчанию. Создаётся при запуске, если в базе нет ни одного администратора.
# При первом заходе стоит либо изменить пароль, либо удалить эту запись из базы.
AUTH_CREATE_DEFAULT_ADMIN = True  # Если не хотите, чтобы администратор по умолчанию создавался, поставьте False
AUTH_DEFAULT_ADMIN = 'admin'
AUTH_DEFAULT_ADMIN_PASSWORD = 'admin'
AUTH_PASSWORD_MIN_LENGTH = 5

# Настройки приложения
# Если True, то пользователи могут самостоятельно регистрироваться,
# в противном случае новых пользователей может добавлять только администратор.
ALLOW_USER_REGISTRATION = True

LOG_LEVEL = logging.INFO
logger = logging.getLogger('BDGService')
logging.basicConfig(level=LOG_LEVEL)
