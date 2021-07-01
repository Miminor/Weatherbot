from config import tg_bot_token
from config import open_weather_token

import requests
from datetime import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)


def log(message):
    print("<!------!>")
    print(datetime.now())
    print("Сообщение от {0} {1} id = {2} \n {3}".format(message.from_user.first_name, message.from_user.last_name,
                                                        str(message.from_user.id), message.text))


@dp.message_handler(commands=["id"])
async def usr_id(message):
    await message.reply(f"{message.from_user.id}")
    log(message)


@dp.message_handler(commands=["help"])
async def usr_help(message):
    await message.reply(
        "Просто введите название города на любом языке и бот выдаст сводку погоды на текущий момент \U0001F31D\n"
        "Также с помощью команды /id вы можете узнать свой id в телеграмме")
    log(message)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Привет! Напиши мне название города и я пришлю тебе сводку погоды!")
    log(message)


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

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric&lang=ua, uk"
        )
        data = r.json()

        location_lat = data["coord"]["lat"]
        location_lon = data["coord"]["lon"]

        r2 = requests.get(
            f"http://api.openweathermap.org/data/2.5/air_pollution?lat={location_lat}&lon={location_lon}&appid={open_weather_token}"
        )

        air = r2.json()

        pollution_level = air["list"][0]["main"]["aqi"]

        city = data["name"]
        cur_humidity = data["main"]["humidity"]
        cur_temp = data["main"]["temp"]
        #max_temp = data["main"]["temp_max"]
        #min_temp = data["main"]["temp_min"]
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
    executor.start_polling(dp)