import logging
import typing

from aiogram.dispatcher.filters import BoundFilter

from tgbot.config import Config
from tgbot.services.dp_api.Sqlite3 import SQLighter


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, obj):
        if self.is_admin is None:
            return False
        db = SQLighter()
        return db.user_permission_status(obj.from_user.id) == "admin"

