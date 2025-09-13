from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from authx import AuthX, AuthXConfig


app = FastAPI(title="Multi-Page Application")
templates = Jinja2Templates(directory="templates")
users = []


config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "csrf_access_token"


origins = [
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000",
    "null",  # Для локальных HTML файлов
    "file://"  # Для файлов открытых напрямую в браузере
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth = AuthX(config=config)


@app.get("/main", response_class=HTMLResponse)
async def main_page(request: Request, responce: Response):
    return templates.TemplateResponse("main.html", {"request": request, "page": "Главная"})

@app.get("/log", response_class=HTMLResponse)
async def log_page(request: Request, responce: Response):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)

    if not token:
        # Проверяем статус регистрации
        registration_status = request.cookies.get("registration_status")
        context = {"request": request, "page": "Вход"}
        if registration_status == "user_added":
            context["success_message"] = "Регистрация прошла успешно! Теперь вы можете войти."
        return templates.TemplateResponse("log.html", context)

    try:
        auth._decode_token(token)
        return RedirectResponse("/main")
    except Exception as e:
        return templates.TemplateResponse("log.html", {"request": request, "page": "Вход"})

@app.get("/reg", response_class=HTMLResponse)
async def reg_page(request: Request):
    return templates.TemplateResponse("reg.html", {"request": request, "page": "Регистрация"})

@app.get("/get_jwt")
def get_jwt(username: str, response: Response):
    blocked = False

    for us in users:
        if us["username"] == username:
            blocked = True
    if blocked:
        return{
            "status": "username already taken"
        }
    token = auth.create_access_token(uid=username)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")
    return {
        "access_token": token,
        "status": "written in cookies"
    }

@app.get("/check")
def check_jwt(request: Request):
    # Извлекаем токен из cookie
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        print({"error": "Token missing in cookies"})
        return {"error": "Token missing in cookies"}

    # Вручную проверяем токен
    try:
        auth._decode_token(token)  # Декодируем и проверяем токен
        print({"status": "ok, jwt true"})
        return {"status": "ok, jwt true"}
    except Exception as e:
        print({"error": str(e)})
        return {"error": str(e)}

@app.get("/allusers")
async def get_users():
    return users


@app.get("/adduser")
async def add_user(username: str, password: str, response: Response):
    users.append({
        "id": len(users),
        "un": username,
        "pswrd": password
    })
    token = auth.create_access_token(uid=username)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")

    return RedirectResponse("/main")

    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)