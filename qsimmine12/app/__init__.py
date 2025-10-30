import os
from contextlib import asynccontextmanager
from pathlib import Path

import redis
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.sim_engine.infra.logger.logger import Logger

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR.parent / "upload"

Logger.init()


DATABASE_URL = (
    f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}@"
    f"{os.getenv('DB_HOST')}:5432/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

redis_client = redis.Redis.from_url(
    os.getenv('REDIS_URL', 'redis://not_found_in_env'),
    decode_responses=True
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    return redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    yield
    print("Application shutdown")

def create_app(test_config=None):
    app = FastAPI(
        title="QSIMMINE12",
        lifespan=lifespan,
        debug=os.getenv('APP_MODE') == 'dev'
    )

    app.state.config = {
        'UPLOAD_FOLDER': 'uploads'
    }
    upload_folder = Path(app.state.config['UPLOAD_FOLDER'])
    upload_folder.mkdir(exist_ok=True)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[f"https://{os.getenv('BASE_DOMAIN')}"] if os.getenv('BASE_DOMAIN') else ["*"],
        allow_credentials=True,
        allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    )

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/upload", StaticFiles(directory=UPLOAD_DIR), name="upload")

    from app.routes import router
    app.include_router(router)

    return app

app = create_app()
