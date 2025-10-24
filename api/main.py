"""
Простой API для классификации токсичного контента
"""
from fastapi import FastAPI
from agent.agent import classify_text
from .schemas import ClassificationRequest, ClassificationResponse

app = FastAPI(title="Toxic Classification API")

@app.post("/classify", response_model=ClassificationResponse)
async def classify_text_endpoint(request: ClassificationRequest):
    """Классификация текста на предмет токсичности"""
    response = await classify_text(request.text)
    return ClassificationResponse(class_id=response.class_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)