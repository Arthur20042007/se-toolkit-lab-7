import sys
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command

# Bot-level imports
from config import config
from handlers.commands import handle_text

async def main():
    # TEST MODE
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        question = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if question:
            response = handle_text(question)
            print(response)
        else:
            print("Please provide a command to test.")
        sys.exit(0)

    # TELEGRAM MODE
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_handler(message: types.Message):
        response = handle_text("/start")
        await message.answer(response)

    @dp.message(Command("help"))
    async def help_handler(message: types.Message):
        response = handle_text("/help")
        await message.answer(response)
        
    @dp.message(Command("health"))
    async def health_handler(message: types.Message):
        response = handle_text("/health")
        await message.answer(response)

    @dp.message(Command("scores"))
    async def scores_handler(message: types.Message):
        response = handle_text(message.text)
        await message.answer(response)
        
    @dp.message(Command("labs"))
    async def labs_handler(message: types.Message):
        response = handle_text("/labs")
        await message.answer(response)

    @dp.message()
    async def text_handler(message: types.Message):
        response = handle_text(message.text)
        await message.answer(response)

    print("Starting bot in Telegram mode...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
