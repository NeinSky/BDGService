from fastapi import APIRouter

router = APIRouter()


@router.get('/')
def hello():
    return {"hello": "Приветствую! Но увы здесь ничего нет. Документация здесь: http://0.0.0.0:8000/docs"}
