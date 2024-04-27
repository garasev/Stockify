import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InputMediaPhoto, FSInputFile
from aiogram.utils.markdown import hbold

import utils

TOKEN = getenv("BOT_TOKEN")
TOKEN = "token"
dp = Dispatcher()

CACHE = {
}

NEW_SET_MSG = "Таргет установлен на банк: "
ERROR_MSG = "ERROR"


WHITELIST = ["JPM", "WFC", "Citi", "BAC"]

TARGET = WHITELIST[0]

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(utils.START_MSG)


@dp.message(Command(commands="getCache"))
async def get_cache_handler(message: types.Message) -> None:
    try:
        await message.answer(str(CACHE))
    except TypeError:
        await message.answer(ERROR_MSG)


@dp.message(Command(commands="graph"))
async def get_cache_handler(message: types.Message) -> None:
    try:
        name = utils.picture_from_graph(TARGET)
        photo = FSInputFile(name)
        await message.answer_photo(photo, caption=TARGET)
    except TypeError:
        await message.answer(ERROR_MSG)


@dp.message(Command(commands="JPM"))
async def set_jpm_handler(message: types.Message):
    TARGET = WHITELIST[0]
    await message.answer(NEW_SET_MSG + TARGET)

@dp.message(Command(commands="WFC"))
async def set_wfc_handler(message: types.Message):
    TARGET = WHITELIST[1]
    await message.answer(NEW_SET_MSG + TARGET)

@dp.message(Command(commands="Citi"))
async def set_citi_handler(message: types.Message):
    TARGET = WHITELIST[2]
    await message.answer(NEW_SET_MSG + TARGET)

@dp.message(Command(commands="BAC"))
async def set_bac_handler(message: types.Message):
    TARGET = WHITELIST[3]
    await message.answer(NEW_SET_MSG + TARGET)

@dp.message(Command(commands="forecast"))
async def get_handler(message: types.Message):
    if not TARGET in CACHE:
        CACHE[TARGET] = TARGET + "\n" + utils.dict_to_str(utils.get_all_forecast(TARGET))
    
    await message.answer(CACHE[TARGET])

@dp.message(Command(commands="clearCache"))
async def get_cache_handler(message: types.Message) -> None:
    CACHE = {}
    try:
        await message.answer(str(CACHE))
    except TypeError:
        await message.answer(ERROR_MSG)

async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())