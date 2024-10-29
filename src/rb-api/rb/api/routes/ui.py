import os

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

ui_router = APIRouter()

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "..", "templates")
)


@ui_router.get("/")
async def interface(request: Request):
    return templates.TemplateResponse("index.html.j2", {"request": request})
