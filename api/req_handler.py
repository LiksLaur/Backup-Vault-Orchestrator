from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from authx import AuthX, AuthXConfig
import psycopg2
from psycopg2 import OperationalError
# Request для взаимодействия с данными запроса в моем случаи только с куки для получения
# Responseдля взаимодействия с данными запроса в моем случаи только с куки для записи
# HTMLResponse модель ответа для возврата страниц
# RedirectResponse для переадрусации
# JSONResponse для ответа в виде джейсона
# Jinja2Templates для понимание где директория с темлейтами
# CORSMiddleware исользовал для cors политики что бы записывать куки (пс бех этого не работало)
# OperationalError для обработки ошибок в psql
# AuthX основный обьект для jwt токенов 
# AuthXConfig конфиг для этих токенов
 



app = FastAPI(title="Multi-Page Application")       
templates = Jinja2Templates(directory="templates")  # директория с темлейтами
config = AuthXConfig()                              # конфиг для authx
config.JWT_ALGORITHM = "HS256"                      # тип алгоритма - симетричный алгоритм подписания и проверки jwt
config.JWT_SECRET_KEY = "SECRET_KEY"                # для обеспечения целостности и подлинности токенов
config.JWT_ACCESS_COOKIE_NAME = "csrf_access_token" # ключ в котором храняться куки 
origins = [
    "http://127.0.0.1:5500",                        # для фронтенда на этом порту запускаелся лайфсервер
    "http://127.0.0.1:8000",                        # порт фастапи    
    "null",                                         # локальные файлы
    "file://"                                       # статичные файлы
]
app.add_middleware(
    CORSMiddleware,                                 # явное внедрение для того что бы его потом поменять
    allow_origins=origins,                          # Разрешает запросы только с этих доменов
    allow_credentials=True,                         # Разрешает отправку cookies и авторизационных заголовков
    allow_methods=["*"],                            # Разрешает все методы
    allow_headers=["*"],                            # Разрешает все хттп заголовки
)
auth = AuthX(config=config)                         # конфиг authx 
conn = psycopg2.connect(
    host="localhost",
    database="bvo",
    user="postgres",
    password="Pgadmin"
)
cur = conn.cursor()                                 # создание обьекта курсора для выполнения запросов




def _run_exists_query(sql: str, params: tuple) -> bool: # для того что бы не повторять проверку ошибок и парамсов для подключения к бд
    connection = None                                   # сброс прошлого подключения
    try:
        connection = psycopg2.connect(
            dbname="bvo",
            user="postgres",
            password="Pgadmin",
            host="localhost",
            port="5432",
        )
        cursor = connection.cursor()
        cursor.execute(sql, params)                     # сделать запрос с атрибутми
        exists = cursor.fetchone()[0]                   # словить то что ответила субд
        return bool(exists)
    except OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False
    finally:
        if connection:
            cursor.close()                              # закрыть кирсор для исполнения sql 
            connection.close()                          # закрыть подключение
def check_user_exists(username: str) -> bool:           # для того что бы проверить существует ли пользователь
    sql = (                                             # запрос на проверку пользователя
        """                                             
        SELECT EXISTS (
            SELECT 1 FROM users WHERE username = %s     
        );
        """
    )
    return _run_exists_query(sql, (username,))          # исполнение запроса, подключение, экскепт ошидок
def check_userpassword_exists(username: str, password: str) -> bool:    # проверить совпадают ли пароль + логин в бд
    sql = (                                                             # ззапрос на проверку
        """
        SELECT EXISTS (
            SELECT 1 FROM users WHERE username = %s AND password = %s
        );
        """
    )
    return _run_exists_query(sql, (username, password))                 # исполнение запроса, подключение, экскепт ошидок




@app.get("/main", response_class=HTMLResponse)                                  # обработчик get на /main с шаблоном ответа как страница 
async def main_page(request: Request):                                          # асинхронныая функция при обработке /main с передачей Request для получения куков
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)                  # получение токена jwt с ключом как в конфиге
    if not token:
        return RedirectResponse("/log")                                         # переадресация на страницу со входом 
    try:
        payload = auth._decode_token(token)                                     # пробуется декодирование токена
        username = payload.get("uid") if isinstance(payload, dict) else None    # если payload это экземпляр словаря то из него достается юз, если нет то none
    except Exception:
        return RedirectResponse("/reg")                                         # переадресация на reg
    else:
        context = {"request": request, "page": "Главная", "username": username}
        return templates.TemplateResponse("main.html", context)                 # возврат страницы с вставкой пеерменных в html 


@app.get("/log", response_class=HTMLResponse)                                   # обработчик get на /log с шаблоном ответа как страница 
async def log_page(request: Request):                                           # асинхронныая функция при обработке /log с передачей Request для получения куков
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)                  # получение токена jwt с ключом как в конфиге
    if not token:
        registration_status = request.cookies.get("registration_status")        # Ищет в куки  с ключом registration_status  
        context = {"request": request, "page": "Вход"}
        if registration_status == "user_added":         
            context["success_message"] = "Регистрация прошла успешно! Теперь вы можете войти." # если пользователь добавлен то в контекст добавляется строка
        return templates.TemplateResponse("log.html", context)                  # возврат страницы

    try:    
        auth._decode_token(token)                                               # пробуется декодирование токена
        return RedirectResponse("/main")                                        # переадресация на маин
    except Exception:
        return templates.TemplateResponse("log.html", {"request": request, "page": "Вход"}) # если ошибка то переадресация на логин


@app.get("/reg", response_class=HTMLResponse)                                   # обработчик get на /reg с шаблоном ответа как страница
async def reg_page(request: Request):                                           # асинхронныая функция при обработке /reg с передачей Request 
    context = {"request": request, "page": "Registration"}                      
    return templates.TemplateResponse("reg.html", context)                      # возврат страниц с контекстом




@app.get("/get_jwt")
def get_jwt(username: str, response: Response):
    token = auth.create_access_token(uid=username)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")
    return JSONResponse({"status": "ok"})


@app.get("/check")
def check_jwt(request: Request):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        return JSONResponse({"error": "Token missing in cookies"}, status_code=401)
    try:
        auth._decode_token(token)
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=401)


@app.get("/allusers")
async def get_users():
    cur.execute("SELECT id, username FROM users")
    rows = cur.fetchall()
    return [{"id": r[0], "username": r[1]} for r in rows]


@app.get("/checkuser")
async def user_check(username: str, password: str, response: Response):
    if not username or not password:
        return JSONResponse({"ok": False, "error": "Missing username or password"}, status_code=400)

    # True means user exists with matching password
    if not check_userpassword_exists(username, password):
        return JSONResponse({"ok": False, "error": "Invalid credentials"}, status_code=401)

    token = auth.create_access_token(uid=username)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")
    return {"ok": True, "redirect": "/main"}
    

@app.get("/adduser")
async def add_user(username: str, password: str, response: Response):
    if not username or not password:
        return JSONResponse({"ok": False, "error": "Missing username or password"}, status_code=400)

    if check_user_exists(username):
        return JSONResponse({"ok": False, "error": "Username already taken"}, status_code=409)

    try:
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
    except Exception as err:
        return JSONResponse({"ok": False, "error": str(err)}, status_code=500)
    else:
        token = auth.create_access_token(uid=username)
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")
        return {"ok": True, "redirect": "/main"}

