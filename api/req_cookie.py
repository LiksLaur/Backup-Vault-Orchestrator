from fastapi import Depends, FastAPI, Response #депендс для проверки jwt в куках, респонс для записи в куки
from authx import AuthXConfig, AuthX # библиотека для решистрации и использования jwt 
from pydantic import BaseModel


app = FastAPI() 
config = AuthXConfig() 
config.JWT_SECRET_KEY = "SECRET_KEY" # ключ для подписи JWT токенов ПОТОМ ПОМЕНЯТЬ НА НАДЕЖНЫЙ
config.JWT_ACCESS_COOKIE_NAME = "my_access_token" # имя cookie в котором будет храниться  токен
config.JWT_TOKEN_LOCATION = ["cookies"] # токены будут храниться в куках
security = AuthX(config=config)

@app.get("/get_jwt")
def get_cookie_jwt(username: str):
    token = security.create_access_token(uid=username)
    return{
        "jwt_token": token
    }
    

