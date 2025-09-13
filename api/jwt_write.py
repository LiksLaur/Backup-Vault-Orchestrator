from fastapi import FastAPI, Depends, Response, Request 
from authx import AuthX, AuthXConfig
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "csrf_access_token"

origins = [
    "http://127.0.0.1:5500"  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Список разрешенных источников
    allow_credentials=True,  # Разрешить отправку кук и учетных данных
    allow_methods=["*"],     # Разрешить все HTTP-методы (GET, POST, OPTIONS и т.д.)
    allow_headers=["*"],     # Разрешить все заголовки
)

auth = AuthX(config=config)

@app.get("/get_jwt")
def get_jwt(username: str, password: str, responce: Response):
    token = auth.create_access_token(uid=username)
    responce.set_cookie(config.JWT_ACCESS_CSRF_COOKIE_NAME, token, httponly=True, samesite="lax")
    return {
        "access_token": token,
        "status": "written in cookies"
    }

@app.get("/check")
def check_jwt(request: Request):
    # Извлекаем токен из cookie
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        return {"error": "Token missing in cookies"}

    # Вручную проверяем токен
    try:
        auth._decode_token(token)  # Декодируем и проверяем токен
        return {"status": "ok, jwt true"}
    except Exception as e:
        return {"error": str(e)}
