from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.wisdom import router as wisdom_router

app = FastAPI(title="Wisdom Library - Forgotten Knowledge Preservation")

app.include_router(auth_router)
app.include_router(wisdom_router)

@app.get("/")
def root():
    return {"message": "Welcome to Wisdom Library API"}