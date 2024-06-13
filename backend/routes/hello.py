from fastapi import APIRouter

from config import DB_USER, DB_PASSWORD, DB_NAME


router = APIRouter()


@router.get('/')
async def hello_world():
    result = {
        'greeting': 'Hello, World!',
        'DB_USER': DB_USER,
        'DB_PASSWORD': DB_PASSWORD,
        'DB_NAME': DB_NAME,
    }
    return result
