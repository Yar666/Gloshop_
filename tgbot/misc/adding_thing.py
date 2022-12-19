import base64
import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from tgbot.keyboards.reply import admin_panel, cancel, done_add, confirm
from tgbot.misc.states import Product
import os

from tgbot.services.dp_api.Sqlite3 import SQLighter


async def cancel_add(message, state):
    await state.finish()
    await message.answer('Панель Андминистратора.\nДля выхода /user', reply_markup=admin_panel)


async def chech_answer(data, message):
    await message.answer("Убедитесь, что данные введены верно", reply_markup=confirm)
    if data.get('image_path'):
        await message.answer_photo(photo=open('tmp.jpg', "rb"),
                                   caption=data.get('name') + "\n" + data.get('describe') + "\n" + data.get('cost'))
        return
    await message.answer(
        data.get('name') + "\n" + data.get('describe') + "\n" + data.get('cost'))


async def name_product(message: Message, state: FSMContext):
    answer = message.text
    logging.getLogger("PRODUCT").info(f"Name successful")
    if message.text == 'Отмена':
        await cancel_add(message, state)
        return
    async with state.proxy() as data:
        data['name'] = answer
    await message.answer("Опишите товар", reply_markup=cancel)
    await Product.Describe.set()


async def describe_product(message: Message, state: FSMContext):
    answer = message.text
    if message.text == 'Отмена':
        await cancel_add(message, state)
        return
    async with state.proxy() as data:
        data['describe'] = answer
    await message.answer("Укажите цену", reply_markup=cancel)
    await Product.Cost.set()


async def cost_product(message: Message, state: FSMContext):
    answer = message.text
    if message.text == 'Отмена':
        await cancel_add(message, state)
        return
    elif not answer.isdigit():
        await message.answer("Допустимы только числовые значения", reply_markup=cancel)
        await Product.Cost.set()
        return
    async with state.proxy() as data:
        data['cost'] = answer
    await message.answer("Добавьте картинку(не обязательно)", reply_markup=done_add)
    await Product.Image.set()


async def product_image(message: Message, state: FSMContext):
    logging.getLogger("PRODUCT").info(f"ANSWER: {message}")
    if message.text == 'Отмена':
        await cancel_add(message, state)
        return

    if message.text == 'Готово':
        async with state.proxy() as data:
            data['image_path'] = ""
        data = await state.get_data()
        await chech_answer(data, message)
        await Product.Confirm.set()

    elif message.photo:
        document = message.photo[-1]
        await document.download(destination_file='tmp.jpg')
        logging.getLogger("PRODUCT").info(f"PHOTO INFO: {document}")
        async with state.proxy() as data:
            data['image_path'] = 'tmp.jpg'
        data = await state.get_data()
        await chech_answer(data, message)
        await Product.Confirm.set()
        return

    await message.answer("Нажмите готово или добавьте картинку", reply_markup=done_add)
    await Product.Image.set()


async def confirm_product(message: Message, state: FSMContext):
    answer = message.text
    if answer == 'Отмена':
        await cancel_add(message, state)
        return
    elif answer == 'Завершить':
        db = SQLighter()
        data = await state.get_data()
        db.add_product(data.get('name'), data.get('cost'), data.get('image_path'), data.get('describe'))
        await message.answer("Товар успешно добавлен", reply_markup=admin_panel)
        await state.finish()


def register_states(dp):
    dp.register_message_handler(name_product, state=Product.Name)
    dp.register_message_handler(describe_product, state=Product.Describe)
    dp.register_message_handler(cost_product, state=Product.Cost)
    dp.register_message_handler(product_image, content_types=['photo', 'text'], state=Product.Image)
    dp.register_message_handler(confirm_product, state=Product.Confirm)
