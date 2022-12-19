import logging
from aiogram import Dispatcher
from aiogram.utils.exceptions import TelegramAPIError
from aiogram.types import Update

async def errors_handler(update: Update, exception):
    logger = logging.getLogger("ERROR HANDLER")
    logger.error(f"{exception}")
    await  update.get_current().message.answer("ОШИБоЧКА")
    return True


def register_error_handler(dp: Dispatcher):
    dp.register_errors_handler(errors_handler, exception=TelegramAPIError)
