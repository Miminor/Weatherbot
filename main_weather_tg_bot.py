import asyncio
import json

from config import tg_bot_token
from config import open_weather_token

import requests
import logging
from datetime import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
logs = logging.getLogger('broadcast')

with open("user_database.json", encoding='utf-8') as file:
    users_dict = json.load(file)


def log(message):
    print("<!------!>")
    print(datetime.now())
    print("Сообщение от {0} {1} id = {2} \n {3}".format(message.from_user.first_name, message.from_user.last_name,
                                                        str(message.from_user.id), message.text))
    user_id = message.from_user.id

    users_dict[user_id] = {
        "user": message.from_user.as_json()
    }

    with open("user_database.json", "w", encoding='utf-8') as users:
        json.dump(users_dict, users, ensure_ascii=False)


@dp.message_handler(commands=["id"])
async def usr_id(message):
    await message.reply(f"{message.from_user.id}")
    log(message)


@dp.message_handler(commands=["help"])
async def usr_help(message):
    await message.reply(
        "Просто введите название города на любом языке и бот выдаст сводку погоды на текущий момент \U0001F31D\n"
        "Также с помощью команды /id вы можете узнать свой id в телеграмме")


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Привет! Напиши мне название города и я пришлю тебе сводку погоды!")


foo_counter = 0


async def insult(message: types.Message):
    r = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json")
    data = r.json()
    insult_for_you = data["insult"]
    await message.answer(insult_for_you)


@dp.message_handler(commands=["once"])
async def once_a_day(message: types.Message):
    arguments = message.get_args()
    global foo_counter
    if not arguments:
        if foo_counter % 2 == 0:
            await message.answer("Для получения ежедневной сводки в это же время дня отправьте команду в формату "
                                 "/once Киев")
        elif foo_counter % 2 != 0:
            foo_counter += 1
            await message.answer("Ежедневная сводка остановлена")
    elif foo_counter % 2 == 0:
        foo_counter += 1
        await message.answer("Для отмены введите команду /once еще раз")
        while foo_counter % 2 != 0:
            await asyncio.sleep(3600)
            await get_weather(message)


@dp.message_handler()
async def get_weather(message: types.Message):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Thunderstorm": "Гроза \U000026A1",
        "Drizzle": "Дождь \U00002614",
        "Rain": "Дождь \U00002614",
        "Snow": "Снег \U0001F328",
        "Mist": "ТУман \U0001F32b"
    }

    air_pollution = {
        1: "Хороший \U0001F7E2",
        2: "Умеренный \U0001F7E1",
        3: "Средний \U0001F7E0",
        4: "Высокий \U0001F534",
        5: "Очень высокий \U00002620"
    }

    arg = message.get_args()

    if arg is None:
        city_name = message.text
    else:
        city_name = arg

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={open_weather_token}&units=metric"
            f"&lang=ua, uk "
        )
        data = r.json()

        location_lat = data["coord"]["lat"]
        location_lon = data["coord"]["lon"]

        r2 = requests.get(
            f"http://api.openweathermap.org/data/2.5/air_pollution?lat={location_lat}&lon={location_lon}"
            f"&appid={open_weather_token} "
        )

        air = r2.json()

        pollution_level = air["list"][0]["main"]["aqi"]

        city = data["name"]
        cur_humidity = data["main"]["humidity"]
        cur_temp = data["main"]["temp"]
        # max_temp = data["main"]["temp_max"]
        # min_temp = data["main"]["temp_min"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.fromtimestamp(
            data["sys"]["sunrise"])
        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Посмотри в окно"

        await message.reply(f"***{datetime.now().strftime('%Y-%m-%d')}***\n"
                            f"Погода в городе: {city}\nТемпература сейчас: {cur_temp} C° {wd}\n"
                            f"Скорость ветра: {wind} м/с \U0001F4A8\n"
                            f"Влажность: {cur_humidity}%\n"
                            f"Восход солнца: {sunrise_timestamp}\n"
                            f"Заход солнца: {sunset_timestamp}\n"
                            f"Продолжительность светового дня: {length_of_the_day} \U0001F55B\n"
                            f"Уровень загрязнённости воздуха: {air_pollution[pollution_level]}\n"
                            f"***Хорошего дня!***"
                            )

    except:
        await message.reply('\U00002620 Проверьте название города')

    log(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
