import logging

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from tgbot.services.dp_api.Sqlite3 import SQLighter


class ACLMiddleware(BaseMiddleware):

    async def setup_chat(self, data: dict, user: types.User):
        user_id = user.id
        db = SQLighter()
        if not db.user_exists(user_id):
            db.add_user(user_id)
            logging.getLogger("ACL Middleware").info(f"ADDED NEW USER: {user_id}")
        data["cntr"] = db
        data["user_id"] = user_id

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.setup_chat(data, message.from_user)

    async def on_pre_process_callback_query(self, call: types.CallbackQuery, data: dict):
        await self.setup_chat(data, call.from_user)
