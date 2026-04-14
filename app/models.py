from pydantic import BaseModel, Field, field_validator
from typing import Optional

class DiabetesInput(BaseModel):
    Pregnancies: int = Field(..., ge=0, le=20, description="Количество беременностей")
    Glucose: int = Field(..., ge=0, le=300, description="Уровень глюкозы")
    BMI: float = Field(..., ge=0.0, le=60.0, description="Индекс массы тела")
    Age: int = Field(..., ge=0, le=120, description="Возраст")

    @field_validator('Glucose')
    def glucose_positive(cls, v):
        if v <= 0:
            raise ValueError('Glucose must be positive')
        return v

    @field_validator('BMI')
    def bmi_positive(cls, v):
        if v <= 0:
            raise ValueError('BMI must be positive')
        return v

class PredictionResponse(BaseModel):
    prediction: int  # 0 или 1

# --- Модели для аутентификации ---
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: Optional[str] = "user"  # можно указать только при регистрации, но по умолчанию user

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # секунд

class TokenData(BaseModel):
    username: str
    role: str