from datetime import timedelta
import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager

from app.models import DiabetesInput, PredictionResponse, UserRegister, UserLogin, Token, UserOut
from app.auth import get_current_active_user, create_access_token
from app.users import create_user, authenticate_user, seed_admin
from app.admin import router as admin_router, increment_counter
from app.config import settings
from app.logger import setup_logger


logger = setup_logger()

# Глобальная сессия ONNX
ort_session = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ort_session
    logger.info("Loading ONNX model...")
    try:
        ort_session = ort.InferenceSession(settings.MODEL_PATH)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Model load error: {e}")
        raise
    # Сидирование админа
    seed_admin()
    yield
    logger.info("Shutting down")

app = FastAPI(
    title="Diabetes Prediction API with JWT & RBAC",
    description="JWT auth, role-based access (user/admin), inference endpoint",
    version="2.0.0",
    lifespan=lifespan
)

# Подключаем роутеры
app.include_router(admin_router)

# --- Auth endpoints ---
@app.post("/auth/register", response_model=UserOut, status_code=201)
async def register(user_data: UserRegister):
    try:
        user = create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # Создаём токен
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": user.username, "role": user.role}
    access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
    return Token(
        access_token=access_token,
        expires_in=int(access_token_expires.total_seconds())
    )

@app.get("/me", response_model=UserOut)
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    # В реальном проекте можно достать из БД дополнительные данные
    return UserOut(id=0, username=current_user.username, role=current_user.role)  # id можно не показывать


@app.post("/predict", response_model=PredictionResponse)
async def predict(
    input_data: DiabetesInput,
    current_user = Depends(get_current_active_user)  # любой авторизованный
):
    logger.info(f"Prediction request from user {current_user.username} with role {current_user.role}")
    increment_counter()  # для админских метрик
    try:
        features = np.array([[
            input_data.Pregnancies,
            input_data.Glucose,
            input_data.BMI,
            input_data.Age
        ]], dtype=np.float32)
        input_name = ort_session.get_inputs()[0].name
        output_name = ort_session.get_outputs()[0].name
        prob = ort_session.run([output_name], {input_name: features})[0]#[0][0]
        # Преобразуем в скаляр (поддерживает любую размерность)
        if np.isscalar(prob):
            prob = float(prob)
        else:
            prob = float(prob.flat[0])  # берём первый элемент
        prediction = 1 if prob > 0.5 else 0
        return PredictionResponse(prediction=prediction)
    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(status_code=500, detail="Inference failed")

# --- Корневой эндпоинт ---
@app.get("/")
async def root():
    return {
        "message": "Diabetes prediction API with JWT & RBAC",
        "endpoints": {
            "/auth/register": "Register new user",
            "/auth/login": "Login get JWT",
            "/me": "Get current user info",
            "/predict": "Make prediction (Bearer token required)",
            "/admin/metrics": "Admin only metrics"
        }
    }