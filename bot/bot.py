import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
import io
import google.generativeai as genai

from agent.agent import classify_text
from schemas import Query

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")



async def transcribe_audio_gemini_bytes(
    audio_bytes: bytes,
    mime_type: str = "audio/ogg",
    prompt: str | None = None
) -> str:
    """Распознаёт речь с помощью Gemini 2.5 Pro, принимая байты аудио.
    """
    if genai is None:
        return "[STT] Требуется пакет google-generativeai"
    if not GOOGLE_API_KEY:
        return "[STT] Не задан GOOGLE_API_KEY"

    model = genai.GenerativeModel("gemini-2.5-pro")
    try:
        system_hint = (
            prompt
            or f"Преобразуй аудио в текст. Верни только транскрипт без пояснений."
        )
        response = await asyncio.to_thread(
            model.generate_content,
            [
                system_hint,
                {"inline_data": {"data": audio_bytes, "mime_type": mime_type}},
            ],
        )
        text = getattr(response, "text", None) or (response.candidates[0].content.parts[0].text if response.candidates else "")
        return text or ""
    except Exception as e:
        return f"[STT] Ошибка Gemini: {e}"

def map_class_id_to_text(class_id: int) -> str:
    """Маппинг ID класса в читаемый текст"""
    class_mapping = {
        0: "нейтральный",
        1: "токсичный", 
        2: "оскорбительный"
    }
    return class_mapping.get(class_id, "нейтральный")

async def agent_query(user_query: str) -> str:
    """Классификация текста через импортированный агент"""
    try:
        response = await classify_text(user_query)
        result = map_class_id_to_text(response.class_id)
        logging.info(f"[Agent result] class_id: {response.class_id}, class_name: {result}")
        return result
        
    except Exception as e:
        logging.exception(f"Ошибка классификации: {e}")
        return "ERROR"  # Специальный маркер для ошибки


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: types.Message):
        await message.answer(
            """Здравствуйте! Наша интеллектуальная система позволит Вам классифицировать голосовой контент на 3 группы: 1. токсичный, 2. оскорбительный, 3. нейтральный. Оставьте свое голосовое сообщение и дождитесь решения"""
        )

    @dp.message(F.voice)
    async def voice_handler(message: types.Message):
        await asyncio.sleep(1)
        await message.answer("Получили сообщение, ожидайте")
        file_id = message.voice.file_id
        tg_file = await message.bot.get_file(file_id)
        buffer = io.BytesIO()
        await message.bot.download(tg_file, destination=buffer)
        buffer.seek(0)
        transcript = await transcribe_audio_gemini_bytes(buffer.getvalue(), mime_type="audio/ogg")
        if transcript.startswith("[STT]"):
            logging.error("[BOT STT error] %s", transcript)
            await message.answer("Произошла ошибка. Попробуйте отправить аудио еще раз")
            return
        logging.info("[BOT STT transcript] %s", transcript)
        
        # Валидация транскрибированного текста
        try:
            validated_text = Query(text=transcript)
            text_to_classify = validated_text.text
        except Exception as e:
            logging.error(f"[BOT validation error] {e}")
            await message.answer("Произошла ошибка. Попробуйте отправить аудио еще раз")
            return
        
        answer = (await agent_query(text_to_classify)) or ""
        if answer == "ERROR":
            await message.answer("Произошла ошибка. Попробуйте отправить аудио еще раз")
        elif answer in {"токсичный", "оскорбительный", "нейтральный"}:
            await message.answer(f"Мы присвоили Вашему голосовому сообщению класс '{answer}'. Всегда к вашим услугам")
        else:
            logging.error("[BOT agent unexpected answer] %s", answer)
            await message.answer("Произошла ошибка. Попробуйте отправить аудио еще раз")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())