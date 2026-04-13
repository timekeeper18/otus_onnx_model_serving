from pydantic import BaseModel, Field, field_validator

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