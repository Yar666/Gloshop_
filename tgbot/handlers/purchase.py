import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, PreCheckoutQuery
from tgbot.misc import states
from tgbot.services.dp_api.Sqlite3 import SQLighter


async def purchase_item(call: CallbackQuery):
    db = SQLighter()
    await call.answer(cache_time=120)
    item_data = db.get_about_item(call.data.split(":")[1])[0]
    logging.getLogger("PURCHASE").info(f"callback data: {item_data}")
    currency = "UAH"
    need_name = True
    need_phone_number = False
    need_email = False
    need_shipping_address = True
    PRICE = types.LabeledPrice(label=item_data[1], amount=int(item_data[2]) * 100)
    await call.bot.send_message(call.from_user.id, "Тестовая карта - 4242 4242 4242 4242")
    await call.bot.send_invoice(chat_id=call.from_user.id,
                                title="Оплата",
                                description=item_data[4],
                                payload='some-invoice-payload-for-our-internal-use',
                                start_parameter='test',
                                currency=currency,
                                prices=[PRICE],
                                provider_token='632593626:TEST:sandbox_i30056585195',
                                need_name=need_name,
                                need_phone_number=need_phone_number,
                                need_email=need_email,
                                need_shipping_address=need_shipping_address
                                )
    states.Purchase.Item = item_data[1]
    await states.Purchase.Payment.set()


async def checkout(query: PreCheckoutQuery, state: FSMContext):
    await query.bot.answer_pre_checkout_query(query.id, True)
    success = await check_payment()
    if success:
        logging.getLogger("PURCHASE").info(f"SUCCESSFUL PAYMENT | DATA: {query.order_info}")
        await query.bot.send_message(query.from_user.id, "Спасибо за покупку")
        await query.bot.send_message(query.from_user.id, f"Указанные данные: {query.order_info}")
        db = SQLighter()
        db.delete_basket(query.from_user.id, states.Purchase.Item)
        await state.reset_state()


async def check_payment():
    return True


async def buy_item(call: CallbackQuery):
    logging.getLogger("BUY").info(f"callback data: {call.data.split(':')}")
    db = SQLighter()
    db.add_to_basket(call.from_user.id, call.data.split(":")[1])
    await call.answer("Товар добавлен в корзину")


async def remove_item(call: CallbackQuery):
    db = SQLighter()
    db.delete_basket(call.from_user.id, call.data.split(":")[1])
    await call.answer("Товар удален из корзины")
    await call.message.delete()

def register_purchase(dp: Dispatcher):
    dp.register_pre_checkout_query_handler(checkout, state=states.Purchase.Payment)
    dp.register_callback_query_handler(purchase_item, text_contains="purchase")
    dp.register_callback_query_handler(remove_item, text_contains="remove")
    dp.register_callback_query_handler(buy_item, text_contains="buy")
