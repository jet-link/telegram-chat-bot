import requests
from aiogram import Bot, Dispatcher, types, F, Router
import asyncio
import os
from dotenv import load_dotenv
import logging
from aiogram.filters import Command

load_dotenv()
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
HF_API_KEY=os.getenv("HF_API_KEY")

HF_MODEL_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# --- Начало работы Groq! ---
def ask_groq(message: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": message}]
    }
    resp = requests.post(url, headers=headers, json=payload).json()
    return resp["choices"][0]["message"]["content"]


# --- /start ---
@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    await message.answer("Hi there! Send me the text and we talk...")

# --- Текст → Groq ---
@dp.message(F.text)
async def handle_text(message: types.Message):
    answer = ask_groq(message.text)
    await message.answer(answer)


@router.message(lambda msg: msg.photo)
async def handle_photo(message: types.Message):
    # Получаем фото
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path}"

    # Качаем картинку
    img_bytes = requests.get(file_url).content

    # Отправляем в Hugging Face
    response = requests.post(HF_MODEL_URL, headers=headers, data=img_bytes)


    try:
        caption = response.json()[0]['generated_text']
    except Exception as e:
        caption = f"Не получилось описать({e})"

    # Отправляем ответ
    await message.answer(caption)
    


# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())