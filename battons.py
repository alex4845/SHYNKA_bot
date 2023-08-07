from aiogram import types

async def get_day(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    button1_0 = types.InlineKeyboardButton(text='на сегодня', callback_data='tod')
    button2_0 = types.InlineKeyboardButton(text='на завтра', callback_data='tum')
    button3_0 = types.InlineKeyboardButton(text='на послезавтра', callback_data='aft_tum')
    keyboard.add(button1_0, button2_0, button3_0)
    await message.answer("Выберите день, на который хотите записаться", reply_markup=keyboard)

async def admin_panel(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_tod = types.InlineKeyboardButton(text='Записи на сегодня', callback_data='tod_wr')
    key_tum = types.InlineKeyboardButton(text='Записи на завтра', callback_data='tum_wr')
    key_aft_tum = types.InlineKeyboardButton(text='Записи на послезавтра', callback_data='aft_tum_wr')
    key_all = types.InlineKeyboardButton(text='Сколько всего людей в базе', callback_data='all')
    keyboard.add(key_tod, key_tum, key_aft_tum, key_all)
    await message.answer("Выберите какие записи смотреть", reply_markup=keyboard)

async def will(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    key_13 = types.InlineKeyboardButton(text='R13', callback_data='R13')
    key_14 = types.InlineKeyboardButton(text='R14', callback_data='R14')
    key_15 = types.InlineKeyboardButton(text='R15', callback_data='R15')
    key_16 = types.InlineKeyboardButton(text='R16', callback_data='R16')
    key_17 = types.InlineKeyboardButton(text='R17', callback_data='R17')
    key_18 = types.InlineKeyboardButton(text='R18', callback_data='R18')
    key_19 = types.InlineKeyboardButton(text='R19', callback_data='R19')
    key_20 = types.InlineKeyboardButton(text='R20', callback_data='R20')
    key_21 = types.InlineKeyboardButton(text='R21', callback_data='R21')

    keyboard.add(key_13, key_14, key_15, key_16, key_17, key_18, key_19, key_20, key_21)
    await message.answer("Выберите диаметр вашего колеса", reply_markup=keyboard)
