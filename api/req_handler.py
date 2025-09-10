from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="./template")

@app.get("/") # <- декоратор, который обрабатывает get - запросы где маршрут
def index(request: Request):
    return templates.TemplateResponse(request=request, name='main.html')

@app.get("/login/") # <- декоратор, который обрабатывает get - запросы где маршрут
def login(request:Request):
    return templates.TemplateResponse(request=request, name="log.html")

@app.get("/reg/") # <- декоратор, который обрабатывает get - запросы где маршрут
def login(request:Request):
    return templates.TemplateResponse(request=request, name="reg.html")