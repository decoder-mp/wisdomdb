from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers.wisdom import router as wisdom_router

app = FastAPI(title="Wisdom Library - Forgotten Knowledge Preservation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://wisdom-ui-production.up.railway.app",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(wisdom_router)

@app.get("/")
def root():
    return {"message": "Welcome to Wisdom Library API"}