import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MODEL_PATH = os.getenv("MODEL_PATH", "diabetes_model.onnx")
    AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
    AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "secret")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()