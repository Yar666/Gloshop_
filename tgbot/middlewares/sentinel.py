import logging

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware

from tgbot.services.dp_api.Sqlite3 import SQLighter


class Sentinel(BaseMiddleware):
    allowed_updates = ["callback_query", "message"]

    async def trigger(self, action, args):
        obj, *args, data = args

        if not any(
                update in action for update in self.allowed_updates
        ):
            return
        if not action.startswith("process_"):
            return
        handler = current_handler.get()
        if not handler:
            return

        allow = getattr(handler, "allow", False)
        if allow:
            return

        user = data.get("user_id")
        db = SQLighter()
        status = db.user_ban_status(user)
        # logging.getLogger("SENTINEL").warning(f"Status: {status}, Allow: {allow}")
        if status:
            message = obj.message if isinstance(obj, types.CallbackQuery) else obj
            await message.reply("Доступ к боту запрещен")
            raise CancelHandler()
