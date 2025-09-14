from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from authx import AuthX, AuthXConfig
import psycopg2
from psycopg2 import OperationalError


app = FastAPI(title="Multi-Page Application")
templates = Jinja2Templates(directory="templates")
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
conn = psycopg2.connect(
    host="localhost",
    database="bvo",
    user="postgres",
    password="Pgadmin"
)
cur = conn.cursor()
def check_user_exists(username):
    connection = None  # Инициализируем переменную connection
    try:
        # Подключение к базе данных (замените параметры на свои)
        connection = psycopg2.connect(
            dbname="bvo",
            user="postgres",
            password="Pgadmin",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()

        # SQL-запрос для проверки существования пользователя
        query = """
        SELECT EXISTS (
            SELECT 1 
            FROM users 
            WHERE username = %s
        );
        """
        cursor.execute(query, (username,))
        
        # Извлечение результата
        exists = cursor.fetchone()[0]
        return exists  # Вернёт True или False

    except OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False
    finally:
        # Закрываем курсор и соединение, если они были открыты
        if connection:
            cursor.close()
            connection.close()
def check_userpassword_exists(username, password):
    connection = None
    try:
        # Подключение к базе данных (замените параметры на свои)
        connection = psycopg2.connect(
            dbname="bvo",
            user="postgres",
            password="Pgadmin",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()

        # SQL-запрос для проверки существования пользователя с указанными username и password
        query = """
        SELECT EXISTS (
            SELECT 1 
            FROM users 
            WHERE username = %s AND password = %s
        );
        """
        cursor.execute(query, (username, password))
        
        # Извлечение результата
        exists = cursor.fetchone()[0]
        return exists  # Вернёт True или False

    except OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()




@app.get("/main", response_class=HTMLResponse)
async def main_page(request: Request, responce: Response):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        return RedirectResponse("/log")
    try:
        auth._decode_token(token)  
    except Exception as e:
        return RedirectResponse("/log")
    else:
        return templates.TemplateResponse("main.html", {"request": request, "page": "Главная"})


@app.get("/log", response_class=HTMLResponse)
async def log_page(request: Request):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
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
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        registration_status = request.cookies.get("registration_status")
        context = {"request": request, "page": "Вход"}
        if registration_status == "user_added":
            context["success_message"] = "Регистрация прошла успешно! Теперь вы можете войти."
        return templates.TemplateResponse("reg.html", context)

    try:
        auth._decode_token(token)
        return RedirectResponse("/main")
    except Exception as e:
        return templates.TemplateResponse("reg.html", {"request": request, "page": "Вход"})





@app.get("/get_jwt")
def get_jwt(username: str, response: Response):
    token = auth.create_access_token(uid=username)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")



@app.get("/check")
def check_jwt(request: Request):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        print({"error": "Token missing in cookies"})
        return {"error": "Token missing in cookies"}
    try:
        auth._decode_token(token)  
        print({"status": "ok, jwt true"})
        return {"status": "ok, jwt true"}
    except Exception as e:
        print({"error": str(e)})
        return {"error": str(e)}


@app.get("/allusers")
async def get_users():
    cur.execute("Select * from users")
    rows = cur.fetchall() 
    return rows

@app.get("/checkuser")
async def user_check(username: str, password: str, response: Response):
    if check_userpassword_exists(username, password):
        return{
            "reject"
        }
    token = auth.create_access_token(uid=username)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")
    redirect_response = RedirectResponse("/main")
    redirect_response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")
    return redirect_response
    

@app.get("/adduser")
async def add_user(username: str, password: str, response: Response):
    if check_user_exists(username):
        print("already taken")
        return("already taken")
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
    except Exception as err:
        return{
            "status": err
        }
    else:
        token = auth.create_access_token(uid=username)
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")
        redirect_response = RedirectResponse("/main")
        redirect_response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")
        return redirect_response

