from fastapi import FastAPI, Depends, Response, Request 
from authx import AuthX, AuthXConfig
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "csrf_access_token"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth = AuthX(config=config)

@app.get("/get_jwt")
def get_jwt(username: str, password: str, responce: Response):
    token = auth.create_access_token(uid=username)
    responce.set_cookie(config.JWT_ACCESS_CSRF_COOKIE_NAME, token)
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
