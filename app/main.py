from fastapi import FastAPI
from app.routers import images
from app.config.config import config
import traceback

app = FastAPI(docs_url="/")
app.include_router(images.router)

@app.on_event("startup")
async def startup_event():
    try:
        from app.database.database import init_db
        init_db()
        print("AplicaciÃ³n iniciada correctamente.")
    except Exception as e:
        print(f"Error durante el inicio de la aplicaciÃ³n: {str(e)}")
        traceback.print_exc()
        raise
