# services/auth/main.py
from fastapi import FastAPI, APIRouter
from services.auth.app.api.routes import api_router

router = APIRouter()
router.include_router(api_router)

app = FastAPI()
app.include_router(router)