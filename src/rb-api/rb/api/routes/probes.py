from fastapi import APIRouter

probes_router = APIRouter()


@probes_router.get("/liveness/")
def liveness():
    return {"message": "RescueBox API"}
