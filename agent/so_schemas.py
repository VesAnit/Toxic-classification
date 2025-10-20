from pydantic import BaseModel


class ClassificationResponse(BaseModel):
    """Модель для проверки ответа модели"""
    class_id: int
