from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controller.chatbot_routes import router as chatbot_router
from app.controller.auth_routes import router as auth_router
from app.services.db_connection import init_db


app = FastAPI(title="Smart Librarian")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthy")
def healthy():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(chatbot_router)


@app.on_event("startup")
def on_startup():
    init_db()
