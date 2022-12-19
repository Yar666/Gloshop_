import logging

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ..keyboards.inline import buy_or_pay_inline
from ..keyboards.reply import menu_user
from ..services.dp_api.Sqlite3 import SQLighter


async def start(message: Message):
    await message.answer("Вас приветствует магазин GloShop", reply_markup=menu_user)


async def shop(message: Message):
    db = SQLighter()
    shop_data = db.get_shop_items()
    if not shop_data:
        await message.answer('Магазин пуст', reply_markup=menu_user)
        return

    await buy_or_pay_inline(message, shop_data)


async def basket(message: Message):
    db = SQLighter()
    user_basket = db.get_user_basket(message.from_user.id)
    shop_data = [db.get_about_item(i[1])[0] for i in user_basket]
    if not user_basket:
        await message.answer('Корзина пуста', reply_markup=menu_user)
        return
    await message.answer('Будут выведены только первые 5 позиций!', reply_markup=menu_user)
    await buy_or_pay_inline(message, shop_data, mode='Оплатить')


def register_user(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start","user"], state="*")
    dp.register_message_handler(shop, Text("Магазин"))
    dp.register_message_handler(basket, Text("Корзина"))
