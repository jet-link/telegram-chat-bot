import requests
from aiogram import Bot, Dispatcher, types, F
import asyncio
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
#HF_API_KEY=os.getenv("HF_API_KEY")
#API_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
#HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


def ask_groq(message: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": message}]
    }
    resp = requests.post(url, headers=headers, json=payload).json()
    return resp["choices"][0]["message"]["content"]

# headers = {
#     "Authorization": f"Bearer {HF_API_KEY}",
#     "Content-Type": "application/octet-stream"
# }

# def describe_image_bytes(image_bytes: bytes) -> str:
#     # Отправляем как "application/octet-stream"
#     resp = requests.post(API_URL, headers={**HEADERS, "Content-Type": "application/octet-stream"}, data=image_bytes)

#     try:
#         result = resp.json()
#     except Exception:
#         return f"⚠️ Ошибка: {resp.status_code}, {resp.text[:200]}"

#     if isinstance(result, list) and "generated_text" in result[0]:
#         return result[0]["generated_text"]

#     if "error" in result:
#         return f"⚠️ HuggingFace take a error: {result['error']}"

#     return f"⚠️ Unable to describe a pic. Answer: {result}"

# --- /start ---
@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    await message.answer("Hi there! Send me the text and we talk...")

# --- Текст → Groq ---
@dp.message(F.text)
async def handle_text(message: types.Message):
    answer = ask_groq(message.text)
    await message.answer(answer)

# #--- Фото (как фото) ---
# @dp.message(F.photo)
# @dp.message(lambda message: message.photo)
# async def handle_photo(message: types.Message):
#     # Получаем файл от Telegram
#     photo = message.photo[-1]
#     file = await bot.get_file(photo.file_id)
#     file_path = file.file_path
#     file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"

#     # Скачиваем байты
#     img_data = requests.get(file_url).content

#     # Описание
#     description = describe_image_bytes(img_data)
#     await message.answer(f"📷 Description: {description}")

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())