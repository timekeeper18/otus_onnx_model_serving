import numpy as np
import onnxruntime as ort
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class DiabetesModel:
    def __init__(self):
        self.session = None
        self.input_name = None
        self.load_model()

    def load_model(self):
        try:
            logger.info(f"Расположение модели: {settings.MODEL_PATH}")
            self.session = ort.InferenceSession(
                settings.MODEL_PATH,
                providers=["CPUExecutionProvider"]
            )
            self.input_name = self.session.get_inputs()[0].name
            logger.info(f"Модель загружена из {settings.MODEL_PATH}")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            raise RuntimeError("Не удалось загрузить модель")

    def predict(self, data: dict) -> int:
        # Порядок признаков должен совпадать с обучением: [Pregnancies, Glucose, BMI, Age]
        features = np.array([[
            data["Pregnancies"],
            data["Glucose"],
            data["BMI"],
            data["Age"]
        ]], dtype=np.float32)

        output = self.session.run(None, {self.input_name: features})
        probability = output[0][0]
        prediction = 1 if probability > 0.5 else 0
        logger.debug(f"Вход: {features}, вероятность: {probability}, предсказание: {prediction}")
        return prediction

# Глобальный экземпляр модели (загружается при старте)
model = DiabetesModel()