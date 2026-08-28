from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="NetScope",
    description="Lightweight network diagnostics and monitoring application",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )