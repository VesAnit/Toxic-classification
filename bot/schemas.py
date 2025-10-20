from pydantic import BaseModel, Field, field_validator


class Query(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Текст не может быть пустым')
        return v.strip()