import asyncio
from aiogram import F
from aiogram import Bot, Dispatcher
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    FSInputFile)
from aiogram.filters import CommandStart
import redis
import os
from data.db_session import global_init
from utils import initializeRedis, createUser, updateLastActivityUser, backgroundWaitEndMessage, getUserByTgId, clearWaitEndMessage, getResOpenAi, checkWaitEndMessage
from openai import OpenAI
import logging

bot = Bot(token=os.getenv('TOKEN_TELEGRAM'))
dp = Dispatcher()
r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), decode_responses='utf-8')
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))


@dp.message(CommandStart())
async def start(message: Message):
    logging.info(f"New Message: {message.text};From: {message.from_user.id};")
    name = message.from_user.full_name
    user = await getUserByTgId(message.from_user.id)
    if not user:
        await createUser(message, r, client)
    else:
        await updateLastActivityUser(message, r)
    await message.answer(r.get('messageStart').format(name=name))
    if int(r.hget(f'user:{message.from_user.id}', 'wait_end_message')) == 0:
        r.hset(f'user:{message.from_user.id}', 'wait_end_message', 1)
        asyncio.create_task(backgroundWaitEndMessage(
            r, bot, message.from_user.id))


@dp.message(F.text)
async def openAi(message: Message):
    logging.info(f"[OpenAi]: New Message: {message.text};From: {message.from_user.id};")
    await updateLastActivityUser(message, r)
    res = await getResOpenAi(message, client)
    logging.info(f"[OpenAi]: New Answer: {';'.join(res)};From: OPENAI;")
    for i in res:
        await message.answer(i.text.value)
    if int(r.hget(f'user:{message.from_user.id}', 'wait_end_message')) == 0:
        r.hset(f'user:{message.from_user.id}', 'wait_end_message', 1)
        asyncio.create_task(backgroundWaitEndMessage(r, bot, message.from_user.id))


async def main():
    asyncio.create_task(checkWaitEndMessage(r, bot))
    # logging.info("Start clearWaitEndMessage")
    # await clearWaitEndMessage(r)
    # logging.info("End clearWaitEndMessage")
    logging.info('Start initializeRedis')
    await initializeRedis(r)
    logging.info('End initializeRedis')
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info('START POLLING')
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(filename='log/log.log', level="INFO")
    global_init()
    asyncio.run(main())
