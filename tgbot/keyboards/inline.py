import base64
import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.misc.callback_datas import buy_callback, purchase_callback, remove_callback


async def buy_or_pay_inline(message, shop_data, mode='Купить'):
    for i in shop_data:
        choice = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=mode,
                                         callback_data=(buy_callback if mode == 'Купить' else purchase_callback).new(
                                             item_name=i[1], quantity=1, cost=i[2]
                                         )),
                    [
                        InlineKeyboardButton(text="Удалить",
                                             callback_data=remove_callback.new(
                                                 item_name=i[1]
                                             ))
                    ][0] if mode == "Оплатить" else InlineKeyboardButton(text="",
                                                                         callback_data=remove_callback.new(
                                                                             item_name=i[1]
                                                                         ))
                ],

            ]
        )
        if i[3]:
            await message.answer_photo(photo=base64.decodebytes(bytes(i[3])),
                                       caption=i[1] + "\n" + "Цена " + str(i[2]), reply_markup=choice)
        else:
            await message.answer(i[1] + "\n" + "Цена " + str(i[2]), reply_markup=choice)
