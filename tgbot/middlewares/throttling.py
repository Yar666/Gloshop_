import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import current_handler, CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def throttle(self, target):
        handler = current_handler.get()
        if not handler:
            return
        limit = getattr(handler, "throttling_rate_limit", self.limit)
        key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        dp = Dispatcher.get_current()
        try:
            await dp.throttle(key, rate=limit)
        except Throttled as t:
            await self.target_throttled(target, t, dp, key)
            raise CancelHandler()

    @staticmethod
    async def target_throttled(target, throttled: Throttled,
                               dp: Dispatcher, key: str):
        msg = target.message if isinstance(target, types.CallbackQuery) else target
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count == 2:
            await msg.reply("Слишком часто. Давай медленнее")
            return
        return
        # elif throttled.exceeded_count == 3:
        #     await msg.reply(f"Вы заблокированны на {delta} секунд")
        #     return
        # await asyncio.sleep(delta)

    async def on_process_message(self, message, data):
        await self.throttle(message)

    async def on_process_callback_query(self, call, data):
        await self.throttle(call)
