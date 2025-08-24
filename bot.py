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


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

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
    await message.answer("Hi there! Send me the text and we can talk...")

# --- Текст → Groq ---
@dp.message(F.text)
async def handle_text(message: types.Message):
    answer = ask_groq(message.text)
    await message.answer(answer)


# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())