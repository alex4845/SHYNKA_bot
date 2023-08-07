from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from battons import get_day, admin_panel, will

engine = create_engine('sqlite:///my_bd.db', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    user_name = Column(String)
    vichicle = Column(String)
    day = Column(String)
    time = Column(String)

Base.metadata.create_all(engine)

bot_token = '5917858144:AAHRyeAdLmAfuDsuZAAv5jUXs4U9cG3sa34'
bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton("🛞 Записаться на шиномонтаж 🛞")
    item2 = types.KeyboardButton("Посмотреть цены")
    item3 = types.KeyboardButton("Реферальная система")
    item4 = types.KeyboardButton("Для админа")
    markup.add(item1)
    markup.row(item2, item3)
    markup.add(item4)
    user_name = message.from_user.first_name

    user_id = message.from_user.id
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        await bot.send_message(message.from_user.id, f'Привет, {user_name}. Рады видеть вас снова! Выберите действие',
                               reply_markup=markup)
    else:
        await bot.send_message(message.from_user.id, f'Привет, {user_name}. Это шиномонтаж. Выберите действие',
                               reply_markup=markup)

class FSMclient(StatesGroup):
    vichicle = State()
    day = State()
    time = State()

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=None)
async def get_start(message: types.Message):
    if message.text == '🛞 Записаться на шиномонтаж 🛞':
        await FSMclient.vichicle.set()
        await message.answer('Марка, цвет и желательно номер вашей машины')

    if message.text == 'Для админа':
        if message.chat.id == 469632258:
            global days
            days = ['tod_wr', 'tum_wr', 'aft_tum_wr']
            await admin_panel(message)
        else:
            await message.answer('Извините, вы не админ')

    if message.text == 'Посмотреть цены':
        global wills
        wills = ['R13', 'R14', 'R15', 'R16', 'R17', 'R18', 'R19', 'R20', 'R21']
        await will(message)

@dp.message_handler(content_types=['text'], state=FSMclient.vichicle)
async def get_vichicle(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['vichicle'] = message.text
    await FSMclient.next()
    await get_day(message)

@dp.callback_query_handler(lambda c: c.data in ['tod', 'tum', 'aft_tum'], state=FSMclient.day)
async def get_days(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    async with state.proxy() as data:
        a = callback_query.data
        t_n = datetime.now().strftime("%Y-%m-%d")
        t_n1 = datetime.now() + timedelta(days=1)
        t_n2 = datetime.now() + timedelta(days=2)
        s_t = str(datetime.now())[11:13]
        global times
        times = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
        if a == "tod":
            data['day'] = t_n
            times = [x for x in times if int(s_t) < int(x[:2])]
            times_all = session.query(User.time).filter_by(day=t_n).all()
        elif a == "tum":
            data['day'] = t_n1.strftime("%Y-%m-%d")
            times_all = session.query(User.time).filter_by(day=data["day"]).all()
        elif a == "aft_tum":
            data['day'] = t_n2.strftime("%Y-%m-%d")
            times_all = session.query(User.time).filter_by(day=data["day"]).all()

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for t in times_all:
        if str(t[0]) in times:
            times.remove(str(t[0]))
    if len(times) > 0:
        for i in range(0, len(times), 4):
            row_buttons = []
            for j in range(4):
                if i + j < len(times):
                    key_time = types.InlineKeyboardButton(text=f"{times[i + j]}", callback_data=f"{times[i + j]}")
                    row_buttons.append(key_time)
            keyboard.row(*row_buttons)
        await bot.send_message(callback_query.from_user.id, text="Выберите время", reply_markup=keyboard)
        await FSMclient.next()
    else:
        await bot.send_message(callback_query.from_user.id, "Времени на запись нет")
        await state.finish()

@dp.callback_query_handler(lambda c: c.data in times, state=FSMclient.time)
async def get_time(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = callback_query.data

    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.full_name
    new_user = User(user_id=user_id, user_name=user_name, vichicle=data["vichicle"], day=data["day"],
                    time=data["time"])
    session.add(new_user)
    session.commit()

    await bot.send_message(callback_query.from_user.id, f'Вы записаны на {data["time"]} на {data["day"]}. Ждем вас!')
    await state.finish()

@dp.callback_query_handler(lambda c: c.data in days)
async def writes(callback_query: types.CallbackQuery):
    day = callback_query.data
    t_n = ""
    if day == 'tod_wr':
        await bot.send_message(callback_query.from_user.id, "На сегодня:")
        t_n = datetime.now()
    elif day == 'tum_wr':
        await bot.send_message(callback_query.from_user.id, "На завтра:")
        t_n = datetime.now() + timedelta(days=1)
    elif day == 'aft_tum_wr':
        await bot.send_message(callback_query.from_user.id, "На послезавтра:")
        t_n = datetime.now() + timedelta(days=2)

    res = session.query(User.time, User.vichicle).filter_by(day=t_n.strftime("%Y-%m-%d")).all()
    if res:
        res.sort(key=lambda x: int(x[-2][0:2]))
        count = 0
        for i in res:
            count += 1
            await bot.send_message(callback_query.from_user.id, f"{count}. {str(i)[1:-1]}")
    else:
        await bot.send_message(callback_query.from_user.id, "Нет записей")

@dp.callback_query_handler(lambda c: c.data == 'all')
async def get_all(callback_query: types.CallbackQuery):
    count_records = session.query(func.count(User.id)).scalar()
    await bot.send_message(callback_query.from_user.id, f"Всего {count_records} клиентов в базе.")


@dp.callback_query_handler(lambda c: c.data in wills)
async def get_price(callback_query: types.CallbackQuery):
    choise = callback_query.data
    price = []
    if choise == 'R13': price = [4, 4, 2.5]
    elif choise == 'R14': price = [4.5, 4.5, 2.5]
    elif choise == 'R15': price = [5, 5, 3]
    elif choise == 'R16': price = [5.5, 5.5, 3]
    elif choise == 'R17': price = [5.5, 5.5, 3.5]
    elif choise == 'R18': price = [6, 6, 3.5]
    elif choise == 'R19': price = [6.5, 6.5, 4]
    elif choise == 'R20': price = [6.5, 6.5, 5]
    elif choise == 'R21': price = [7, 7, 5]
    await bot.send_message(callback_query.from_user.id, f"{choise}: снять/поставить - {price[0]} руб., "
                                                            f"монтаж/демонтаж - {price[1]} руб., балансировка - "
                                                            f"{price[2]} руб. Итого за одно колесо: {sum(price)} руб.")


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)

