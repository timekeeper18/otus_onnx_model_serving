import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBasicCredentials
from app.models import DiabetesInput, PredictionResponse
from app.auth import security, verify_credentials
from app.inference import model
from app.config import settings

# Настройка логирования
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Diabetes Prediction API", description="Инференс ONNX модели диабета")

@app.get("/")
def root():
    logger.info("Корневой эндпоинт вызван")
    return {"message": "Сервис предсказания диабета. Используйте POST /predict с Basic Auth."}

@app.post("/predict", response_model=PredictionResponse)
def predict(
    request: Request,
    input_data: DiabetesInput,
    credentials: HTTPBasicCredentials = Depends(security)
):
    # Аутентификация
    verify_credentials(credentials)

    # Логирование запроса
    logger.info(f"Запрос от {credentials.username}: {input_data.model_dump()}")

    try:
        prediction = model.predict(input_data.model_dump())
        response = {"prediction": prediction}
        logger.info(f"Ответ: {response}")
        return response
    except Exception as e:
        logger.error(f"Ошибка при предсказании: {e}")
        raise HTTPException(status_code=500, detail="Ошибка выполнения модели")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)