from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from authx import AuthX, AuthXConfig
import psycopg2
from psycopg2 import OperationalError
from crypto.crypto_def import create_saltpassword, virify_saltpassword
# Request для взаимодействия с данными запроса в моем случаи только с куки для получения
# Responseдля взаимодействия с данными запроса в моем случаи только с куки для записи
# HTMLResponse модель ответа для возврата страниц
# RedirectResponse для переадрусации
# JSONResponse для ответа в виде джейсона
# crypto_def для работы с паролями
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
    # Получаем хэш пароля по имени пользователя и проверяем через bcrypt
    connection = None
    try:
        connection = psycopg2.connect(
            dbname="bvo",
            user="postgres",
            password="Pgadmin",
            host="localhost",
            port="5432",
        )
        cursor = connection.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE username = %s LIMIT 1",
            (username,),
        )
        row = cursor.fetchone()
        if not row or row[0] is None:
            return False
        stored_hash_text = row[0]
        # Храним как текст -> переводим обратно в bytes для проверки
        stored_hash_bytes = stored_hash_text.encode("utf-8") if isinstance(stored_hash_text, str) else stored_hash_text
        return virify_saltpassword(stored_hash_bytes, password)
    except OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()




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




@app.get("/get_jwt")                                                            # обработчик get на /get_jwt генерация токена 
def get_jwt(username: str, response: Response):                                 # функция для /get_jwt с передачей юз для генерации токена и респонса для записи токена в куки
    token = auth.create_access_token(uid=username)                              # генерация токена по юз
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax") # установкаjwt в куки jwt с ключом как name из конфига 
    return JSONResponse({"status": "ok"})                                                    


@app.get("/check")                                                              # обработчик get на /check для проверки валидности токена 
def check_jwt(request: Request):                                                # функция для /get_jwt с регуеста для проверки токена в куках
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        return JSONResponse({"error": "Token missing in cookies"}, status_code=401) # если токена нет вернуть ошибку со статус кодом 401
    try:
        auth._decode_token(token)                                                   # пробуется декодировать токен
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=401)                     # если не получается то возврат ошибки с описанием + статус код 401


@app.get("/checkuser")                                                              # обработчик get на /checkuser для проверки пользователя
async def user_check(username: str, password: str, response: Response):             # асинхронная функция принимаюяя юз пасворд и респонс для записи в куки
    if not username or not password:                                                # если не передан проль или юз то
        return JSONResponse({"ok": False, "error": "Missing username or password"}, status_code=400)    # возврат ошибки с статус кодом 400

    if not check_userpassword_exists(username, password):                                               # проверка пользователя с правильным юз и паролем
        return JSONResponse({"ok": False, "error": "Invalid credentials"}, status_code=401)             # если нет то ошибка со статус кодом 401

    token = auth.create_access_token(uid=username)                                                      # генерация токена для существующего пользователя 
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")            # запись токена в куки 
    return {"ok": True, "redirect": "/main"}
    

@app.get("/adduser")                                                                                    # обработчик get на /adduser для добавления пользователя
async def add_user(username: str, password: str, response: Response):                                   # асинхронная функция принимает юз пасворд и респонс для записи в куки jwt 
    if not username or not password:                                                                    # если не передан проль или юз то
        return JSONResponse({"ok": False, "error": "Missing username or password"}, status_code=400)    # возврат ошибки с статус кодом 400

    if check_user_exists(username):                                                                     # проверка занят ли юз
        return JSONResponse({"ok": False, "error": "Username already taken"}, status_code=409)          # возврат ошибки с статус кодом 409

    try:
        # Хэшируем пароль перед сохранением
        hashed_password_bytes = create_saltpassword(password)
        hashed_password_text = hashed_password_bytes.decode("utf-8")
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password_text))     # попытка вставить данные 
        conn.commit()       
    except Exception as err:                                        
        return JSONResponse({"ok": False, "error": str(err)}, status_code=500)                          # выозврат ошибки со статус кодом 500
    else:
        token = auth.create_access_token(uid=username)                                                  # если нет ошибок то генерируется токен на основе юза
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token, httponly=True, samesite="lax")        # записывается в куки
        return {"ok": True, "redirect": "/main"}
    

### ДЛЯ РАЗРАБОТКИ ###
### ↓ ↓ ↓ ↓ ↓ ↓ ↓  ###

@app.get("/allusers")                                                               # обработчик get на /allusers для возврата всех юзеров из бд
async def get_users():
    cur.execute("SELECT id, username FROM users")                                   # исполнение запрса
    rows = cur.fetchall()                                                           # получение того что вернла субд
    return [{"id": r[0], "username": r[1]} for r in rows]                           # возврат массива обьектов где к каждому id преписывается id из соответсвующей строки и username так же из строки


# хттп статус коды
# 400 - неправильный запрос
# 401 - неавторизованн
# 409 - конфлкт ( пользователь уже существует )
# 500 - ошибка сервера (запрос в бд не пошлучился)
