from pydantic import BaseModel, Field, field_validator

class ClassificationRequest(BaseModel):
    """Модель для запроса инпута"""
    text: str = Field(..., min_length=1, max_length=5000)
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Текст не может быть пустым')
        return v.strip()

class ClassificationResponse(BaseModel):
    """Модель для ответа модели"""
    class_id: int