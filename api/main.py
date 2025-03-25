from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from .routes.chats import router as chats_router
from .routes.auth import router as auth_router
app = FastAPI()

origins = [
        'http://127.0.0.1:3000'
        'http://localhost:3000'
        ]
app.add_middleware(
        CORSMiddleware,
        allow_origins = origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )

app.include_router(chats_router, prefix="/chats")
app.include_router(auth_router, prefix="/auth")

@app.get("/")
async def index() -> RedirectResponse:
    return RedirectResponse("/docs")

@app.get("/healthcheck", status_code=200)
async def healthcheck() -> None:
    return
