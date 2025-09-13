from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Multi-Page Application")
templates = Jinja2Templates(directory="templates")


@app.get("/main", response_class=HTMLResponse)
async def main_page(request: Request, responce: Response):
    return templates.TemplateResponse("main.html", {"request": request, "page": "Главная"})

@app.get("/log", response_class=HTMLResponse)
async def log_page(request: Request, responce: Response):
    return templates.TemplateResponse("log.html", {"request": request, "page": "Вход"})

@app.get("/reg", response_class=HTMLResponse)
async def reg_page(request: Request, responce: Response):
    return templates.TemplateResponse("reg.html", {"request": request, "page": "Регистрация"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)