from fastapi import FastAPI
from app.routers import images, auth
from app.config.config import config

app = FastAPI(docs_url="/")
app.include_router(images.router)
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    from app.database.database import init_db
    init_db()
