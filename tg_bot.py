from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_models import User
from nn_model import Model as SummarizeModel
from typing import List
from user_model import UserAction

from credentials_local import creds

bot = Bot(token=creds["bot_key"])
dp = Dispatcher(bot)

engine = create_engine(creds["db_url"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

PREDICTION_MODEL: SummarizeModel = SummarizeModel()


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
    user, created = User.get_or_create(db, user_id=message.from_user.id)
    
    if (len(input_text) > user.balance):
        await message.answer(f"У вас не достаточно средств ({user.balance}) для выполнения данного действия. Необходимо {len(input_text)}")
    else:
        global PREDICTION_MODEL
        predict = PREDICTION_MODEL.make_prediction(input_text, min_len=10, max_len=1000)[0]["summary_text"]
        user.make_action(db, input_text, predict)
        await message.answer(predict)
        await message.answer(f"Ваш баланс был уменьшен на {len(input_text)}")

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
    user, created = User.get_or_create(db, user_id=message.from_user.id)

    history: List[UserAction] = user.get_history(db)

    res: str = ""
    for i in range(len(history)):
        res += f"*{i + 1}: {history[i].date}* | {history[i].input_text} | {history[i].output_text} | {history[i].cost}\n"

    await message.answer(res, parse_mode=types.ParseMode.MARKDOWN)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
