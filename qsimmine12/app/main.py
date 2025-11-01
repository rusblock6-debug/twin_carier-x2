# qsimmine12/app/main.py
from fastapi import FastAPI
from app.routes import router  # ← импортируем твой роутер

app = FastAPI(
    title="QSimMine API",
    description="Цифровой двойник карьера — симуляция и планирование",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc"     # ReDoc
)

# Подключаем все роуты
app.include_router(router)

# Опционально: приветствие
@app.get("/")
def read_root():
    return {"message": "QSimMine API запущен! Перейди в /docs"}