from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/main", response_class=HTMLResponse)
def get_main(request: Request):
    return templates.TemplateResponse(
        "main.html",
    )

@app.get("/log", response_class=HTMLResponse)
def get_main(request: Request):
    return templates.TemplateResponse(
        "log.html",
    )

@app.get("/reg", response_class=HTMLResponse)
def get_main(request: Request):
    return templates.TemplateResponse(
        "reg.html",
    )
