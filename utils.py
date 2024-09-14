
import datetime
import os
import time
from redis import Redis
from openai import OpenAI
from aiogram.types import Message
import json
from data.db_session import create_session
from data.models.users import User
from aiogram import Bot
import asyncio

async def initializeRedis(r: Redis):
    with open('config.json', 'r') as json_file:
        config = json.load(json_file)
        for l, item in config.items():
            r.set(l, item)


async def getResOpenAi(m: Message, client: OpenAI):
    thread_id = await getThreadIdByTgId(m.from_user.id)
    asst_id = os.getenv('OPENAI_ASST_KEY')
    messageToOpenAi = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=m.text
        )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=asst_id,
    )
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        return messages.data[0].content
    else:
        return run.status



async def getThreadIdByTgId(tgId: int):
    with create_session() as s:
        user = s.query(User).filter(User.tg_id == tgId).first()
        if user:
            return user.thread_id
        return None
    

async def updateLastActivityUser(m: Message, r: Redis):
    # redis
    r.hset(f'user:{m.from_user.id}', 'last_activity', time.time())
    # postgresql
    with create_session() as s:
        user = s.query(User).filter(User.tg_id == m.from_user.id).first()
        if user:
            user.last_activity = datetime.datetime.now()
            s.commit()
    

async def createUser(m: Message, r: Redis, client: OpenAI):
    # threadId = await createThreadId(client)
    threadId = '12341234'
    now = datetime.datetime.now()
    with create_session() as s:
        user = User(tg_id=m.from_user.id, full_name=m.from_user.full_name, thread_id=threadId, created_date=now, last_activity=now)
        s.add(user)
        s.commit()
        s.refresh(user)
    r.hset(f'user:{m.from_user.id}', 'last_activity', time.time())
    r.hset(f'user:{m.from_user.id}', 'wait_end_message', 0)    

async def createThreadId(client: OpenAI):
    thread = client.beta.threads.create()
    return thread.id



async def backgroundWaitEndMessage(r: Redis, bot: Bot, id: int):
    n = int(r.get('messageEndTime')) * 60
    m: str = r.get('messageEnd')
    while True:
        await asyncio.sleep(5)
        if time.time() - float(r.hget(f'user:{id}', 'last_activity')) > n:
            await bot.send_message(id, m)
            r.hset(f'user:{id}', 'wait_end_message', 0)
            break



async def getUserByTgId(id: int):
    with create_session() as s:
        user = s.query(User).filter(User.tg_id == id).first()
        return user
    return None


async def clearWaitEndMessage(r: Redis):
    with create_session() as s:
        users = s.query(User).all()
        for user in users:
            r.hset(f'user:{user.tg_id}', 'wait_end_message', 0)


async def checkWaitEndMessage(r: Redis, bot: Bot):
    with create_session() as s:
        users = s.query(User).all()
        for user in users:
            m = r.hget(f'user:{user.tg_id}', 'wait_end_message')
            if int(m) == 1:
                lastTime = r.hget(f'user:{user.tg_id}', 'last_activity')
                if time.time() - float(lastTime) < 3600:
                    asyncio.create_task(backgroundWaitEndMessage(r, bot, user.tg_id))