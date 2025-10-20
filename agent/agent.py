import asyncio
import logging
import os
import json
from typing import Literal, Tuple
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from dotenv import load_dotenv
from pydantic import ValidationError
from .so_schemas import ClassificationResponse

load_dotenv()

# Настройки модели
MODEL_PATH = os.getenv("MODEL_PATH", "./models")
MAX_LENGTH = int(os.getenv("MAX_LENGTH", "256"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальные переменные для модели
tokenizer = None
model = None
device = None




async def load_model():
    """
    Загрузка модели DistilBERT
    """
    global tokenizer, model, device
    
    try:
        logger.info(f"Загрузка модели из {MODEL_PATH}")
        
        # Определение устройства
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Используется устройство: {device}")
        
        # Загрузка токенизатора и модели
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        model.to(device)
        model.eval()
        
        logger.info("Модель успешно загружена")
        
    except Exception as e:
        logger.error(f"Ошибка загрузки модели: {e}")
        raise RuntimeError(f"Не удалось загрузить модель: {e}")

async def classify_text(text: str) -> ClassificationResponse:
    """Классификация текста с помощью DistilBERT"""
    global tokenizer, model, device
    
    if tokenizer is None or model is None:
        await load_model()
    
    try:
        logger.info(f"[DistilBERT input] {text[:100]}...")
        
        # Токенизация
        inputs = tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=MAX_LENGTH,
            return_tensors="pt"
        ).to(device)
        
        # Предсказание
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_class_id = torch.argmax(predictions, dim=-1).item()
        
        logger.info(f"[DistilBERT output] class_id: {predicted_class_id}")
        return ClassificationResponse(class_id=predicted_class_id)
        
    except Exception as e:
        logger.error(f"Classification error: {e}")
        return ClassificationResponse(class_id=0)  # fallback к нейтральному

