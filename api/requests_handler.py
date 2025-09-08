from fastapi import Depends, FastAPI, Response #депендс для проверки jwt в куках, респонс для записи в куки
from authx import AuthXConfig, AuthX # библиотека для решистрации и использования jwt 
from pydantic import BaseModel


app = FastAPI() 
config = AuthXConfig() 
config.JWT_SECRET_KEY = "SECRET_KEY" # ключ для подписи JWT токенов ПОТОМ ПОМЕНЯТЬ НА НАДЕЖНЫЙ
config.JWT_ACCESS_COOKIE_NAME = "my_access_token" # имя cookie в котором будет храниться  токен
config.JWT_TOKEN_LOCATION = ["cookies"] # токены будут храниться в куках

security = AuthX(config=config)



class SALogin(BaseModel):   # схемка отвеа для эндпоинта по регистрации 
    status_code: int
    status: str
    cookie_key: str
    input_password: str
    input_login: str
    access_token: str

class SUsersCreds(BaseModel): # схемка для эндпоинта по регистрации 
    password: str
    login: str

@app.post('/login', response_model=SALogin)
def get_login_data(creds: SUsersCreds, response: Response):  # Добавляем параметр response
    token = security.create_access_token(uid="12345") # создание токена
    
    # Устанавливаем cookie с токеном
    response.set_cookie(
        key="my_access_token",  #Ключ cookie
        value=token,            #Значение - JWT-токен
        httponly=True,          #Cookie доступен только на сервере (защита от XSS)
        secure=False,           #Для HTTPS установите True
        samesite="lax"          #Защита от CSRF (можно использовать "strict")
    )
    
    return {
        "status_code": 200,
        "status": "successful",
        "cookie_key": "my_access_token",
        "input_password": creds.password,
        "input_login": creds.login,
        "access_token": token
    }

@app.get("/protected", dependencies=[Depends(security.access_token_required)]) # эндпоинт для проверки валидности jwt в куках, если да то серетдата возвращается 
def protected_data():
    return "secretdata"
