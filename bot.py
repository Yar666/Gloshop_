import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.purchase import register_purchase
from tgbot.handlers.user import register_user
from tgbot.handlers.error_handler import register_error_handler
from tgbot.middlewares.access_control_list import ACLMiddleware
from tgbot.middlewares.sentinel import Sentinel
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.misc.adding_thing import register_states
from tgbot.services.dp_api.Sqlite3 import SQLighter

logger = logging.getLogger("MAIN")


def register_all_middlewares(dp, config):
    dp.setup_middleware(ACLMiddleware())
    dp.setup_middleware(Sentinel())
    dp.setup_middleware(ThrottlingMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)
    register_purchase(dp)
    register_states(dp)
    register_error_handler(dp)


async def main():
    SQLighter("tgbot/services/dp_api/db.db")
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
