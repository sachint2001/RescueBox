import os
from functools import wraps
from typing import Callable

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rb.api.models import CommandResult
from rb.lib.stdout import Capturing  # type: ignore

from rescuebox.main import app as rescuebox_app

app = FastAPI(
    title="RescueBoxAPI",
    summary="RescueBox is a set of tools for file system investigations.",
    version="0.1.0",
    contact={
        "name": "Jagath Jai Kumar",
    },
)

app.mount(
    "/static", StaticFiles(directory=os.path.join("rb", "api", "static")), name="static"
)
templates = Jinja2Templates(directory=os.path.join("rb", "api", "templates"))


def safe_endpoint(callback: Callable, *args, **kwargs) -> CommandResult:
    with Capturing() as stdout:
        try:
            result = callback(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = f"Typer CLI aborted {e}"
    return CommandResult(result=result, stdout=stdout, success=success, error=error)


def command_callback(callback: Callable):
    @wraps(callback)
    def wrapper(*args, **kwargs):
        result = safe_endpoint(callback, *args, **kwargs)
        if not result.success:
            # Return the last 10 lines of stdout
            raise HTTPException(
                status_code=400,
                detail={"error": result.error, "stdout": result.stdout[-10:]},
            )
        return result

    return wrapper


for plugin in rescuebox_app.registered_groups:
    router = APIRouter()
    for command in plugin.typer_instance.registered_commands:
        router.add_api_route(
            f"/{command.callback.__name__}/",
            endpoint=command_callback(command.callback),
            methods=["POST"],
            name=command.callback.__name__,
            response_model=CommandResult,
        )
    app.include_router(router, prefix=f"/{plugin.name}", tags=[plugin.name])


@app.get("/", response_class=HTMLResponse)
def ui(request: Request):
    # TODO: add the UI implementation here
    return templates.TemplateResponse(request=request, name="index.html.j2")


@app.get("/api/")
def api():
    return {"message": "RescueBox API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("rb.api.main:app", host="0.0.0.0", port=8000, reload=True)
