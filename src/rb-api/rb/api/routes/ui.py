import json
import os

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from rb.lib.typer import typer_app_to_tree

from rescuebox.main import app as rescuebox_app

ui_router = APIRouter()

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "..", "templates")
)


@ui_router.get("/")
async def interface(request: Request):
    tree = typer_app_to_tree(rescuebox_app)
    return templates.TemplateResponse(
        "index.html.j2", {"request": request, "tree": json.dumps(tree)}
    )
