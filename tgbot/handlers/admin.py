from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from tgbot.keyboards.reply import admin_panel, cancel
from tgbot.misc.access import allow_access
from tgbot.misc.states import Product
from tgbot.misc.throttling import rate_limit
from tgbot.services.dp_api.Sqlite3 import SQLighter


async def admin(message: Message):
    await message.answer("Панель Администратора", reply_markup=admin_panel)


async def add_product(message: Message):
    await message.answer("Название товара", reply_markup=cancel)
    await Product.Name.set()


@rate_limit(2)
@allow_access()
async def block_me(message: Message, cntr: SQLighter):
    cntr.BAN(message.chat.id)
    await message.answer("You have been banned")


@rate_limit(2)
@allow_access()
async def unblock_me(message: Message, cntr: SQLighter):
    cntr.UNBAN(message.chat.id)
    await message.answer("You have been unbanned")


@rate_limit(2)
async def get_admin(message: Message):
    db = SQLighter()
    db.set_admin(message.from_user.id)
    await message.answer("Вы получили статус администратора.\nПанель - /admin")


@rate_limit(2)
async def remove_admin(message: Message):
    db = SQLighter()
    db.set_admin(message.from_user.id, status='user')
    await message.answer("Теперь у вас нет прав администратора.")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin, commands=["admin"], state="*", is_admin=True)
    dp.register_message_handler(add_product, Text("Добавить товар"), is_admin=True)
    dp.register_message_handler(get_admin, commands=["get_admin"], state="*")
    dp.register_message_handler(remove_admin, commands=["remove_admin"], state="*")
    dp.register_message_handler(block_me, commands=["block_me"], state="*")
    dp.register_message_handler(unblock_me, commands=["unblock_me"], state="*")
