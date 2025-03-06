import multiprocessing
import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from rb.api import routes

app = FastAPI(
    title="RescueBoxAPI",
    summary="RescueBox is a set of tools for file system investigations.",
    version="0.1.0",
    debug=True,
    contact={
        "name": "Umass Amherst RescuBox Team",
    },
) 

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static",
)

app.include_router(routes.probes_router, prefix="/probes")
app.include_router(routes.cli_to_api_router)
app.include_router(routes.ui_router)




if __name__ == "__main__":
    import uvicorn

    multiprocessing.freeze_support()  # For Windows support
    # for pyinstaller exe
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
    else:
    # for cmdline dev mode
        uvicorn.run("rb.api.main:app", host="0.0.0.0", port=8000, reload=True)
