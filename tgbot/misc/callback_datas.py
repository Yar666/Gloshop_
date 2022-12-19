from aiogram.utils.callback_data import CallbackData

buy_callback = CallbackData("buy", "item_name", "quantity", "cost")
purchase_callback = CallbackData("purchase", "item_name", "quantity", "cost")
remove_callback = CallbackData("remove","item_name")