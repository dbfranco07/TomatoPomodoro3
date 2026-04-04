from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from services.persistence import ASSETS_DIR, STATIC_DIR
from services.database import init_db, close_db
from routers import tasks, notes, ai, auth
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="TomatoPomodoro", lifespan=lifespan)
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(notes.router)
app.include_router(ai.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, reload_dirs=["src"])
