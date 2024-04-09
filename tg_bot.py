from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import asyncio
import aio_pika

from models.db_models import User
from typing import List
from models.user_model import UserAction
from rabbitmq_scripts.rabbitmq_publisher import send_message

from credentials_local import creds

bot = Bot(token=creds["bot_key"])
dp = Dispatcher(bot)

engine = create_engine(creds["db_url"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Проверяем, существует ли пользователь с таким ID
    db = SessionLocal()
    user, created = User.get_or_create(db, user_id=message.from_user.id)
    
    if created:
        await message.answer("Добро пожаловать! Вы успешно зарегистрированы.")
    else:
        await message.answer(f"Ваш баланс: {user.balance}")

@dp.message_handler(commands=['predict'])
async def make_prediction(message: types.Message):
    input_text = message.text.split(' ', 1)[1]

    db = SessionLocal()
    user, _ = User.get_or_create(db, user_id=message.from_user.id)
    
    if (len(input_text) > user.balance):
        await message.answer(f"У вас не достаточно средств ({user.balance}) для выполнения данного действия. Необходимо {len(input_text)}")
    else:
        send_message(input_text, message.from_user.id)
        await message.answer("Запрос отправлен.")

@dp.message_handler(commands=['balance'])
async def get_balance(message: types.Message):
    db = SessionLocal()
    user, created = User.get_or_create(db, user_id=message.from_user.id)
    if created:
        await message.answer("Вы не зарегистрированы! Вызовите команду /start")
    else:
        await message.answer(f"Ваш баланс: {user.balance}")

@dp.message_handler(commands=['increase_balance'])
async def increase_balance(message: types.Message):
    amount = int(message.text.split(' ', 1)[1])

    db = SessionLocal()
    user, created = User.get_or_create(db, user_id=message.from_user.id)

    if created:
        await message.answer("Вы не зарегистрированы! Вызовите команду /start")
    else:
        user.increase_balance(db, amount)
        await message.answer(f"Ваш баланс успешно пополнен на {amount}")

@dp.message_handler(commands=['history'])
async def get_history(message: types.Message):
    db = SessionLocal()
    user, _ = User.get_or_create(db, user_id=message.from_user.id)

    history: List[UserAction] = user.get_history(db)

    res: str = ""
    for i in range(len(history)):
        res += f"*{i + 1}: {history[i].date}* | {history[i].input_text} | {history[i].output_text} | {history[i].cost}\n"

    await message.answer(res, parse_mode=types.ParseMode.MARKDOWN)


async def consume_results():
    connection = await aio_pika.connect_robust(
        "amqp://user:123@localhost/",
        heartbeat=30
    )

    async with connection:
        channel = await connection.channel()

        result_queue = await channel.declare_queue('result_queue')

        async for message in result_queue:
            async with message.process():
                result = json.loads(message.body)

                predict_text = result["result"]
                user_id = result["user_id"]

                db = SessionLocal()
                user, _ = User.get_or_create(db, user_id=user_id)

                await bot.send_message(user_id, predict_text)
                await bot.send_message(user_id, f"Ваш баланс был уменьшен на {len(predict_text)}")
                user.make_action(db, result["input_text"], predict_text)

async def main():
    pooling_task = asyncio.create_task(dp.start_polling())
    consume_task = asyncio.create_task(consume_results())

    await asyncio.gather(pooling_task, consume_task)

if __name__ == '__main__':
    asyncio.run(main())