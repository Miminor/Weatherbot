from config import tg_bot_token
from aiogram import Bot, Dispatcher, executor

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)

async def send():
    usr_id = int(input("Введите id получателя: "))
    test = input("Введите ваше сообщение: ")
    await bot.send_message(usr_id, test)


if __name__ == '__main__':
    executor.start(dp, send())