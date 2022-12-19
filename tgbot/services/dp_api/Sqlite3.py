import base64
import sqlite3
import logging

from tgbot.models.singleton import Singleton


class SQLighter(metaclass=Singleton):

    def __init__(self, database="db.db"):
        self.__connection = sqlite3.connect(database, check_same_thread=False)
        self.__cursor = self.__connection.cursor()
        self.__DataBaseLogger = logging.getLogger("DATABASE")
        with self.__connection:
            self.__cursor.execute(
                """CREATE TABLE IF NOT EXISTS users(
                userid INTEGER PRIMARY KEY,
                status STRING,
                banned BOOLEAN);""")
            self.__cursor.execute(
                """CREATE TABLE IF NOT EXISTS user_basket (
                    userid,
                    item,
                    count
                );""")
            self.__cursor.execute(
                """CREATE TABLE IF NOT EXISTS shop_item (
                    id,
                    name STRING,
                    cost,
                    img,
                    description
                );""")
            self.__cursor.execute(
                """CREATE TABLE IF NOT EXISTS orders (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id,
                    item_id,
                    count,
                    datatime,
                    paid      BOOLEAN DEFAULT (0) 
                );""")
            self.__cursor.execute(
                """CREATE TABLE IF NOT EXISTS completed_orders (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id,
                    item_id,
                    count,
                    amount_payable,
                    order_time,
                    when_completed
                );""")

    def set_admin(self, userid, status='admin'):
        with self.__connection:
            return self.__cursor.execute("UPDATE `users` SET status=? WHERE `userid`=? ", (status, userid))

    def user_exists(self, userid) -> bool:
        with self.__connection:
            result = self.__cursor.execute('SELECT * FROM `users` WHERE `userid` = ?', (userid,)).fetchall()
            return bool(len(result))

    def user_ban_status(self, userid) -> bool:
        with self.__connection:
            result = self.__cursor.execute('SELECT `banned` FROM `users` WHERE `userid` = ?', (userid,)).fetchall()
            return not not result[0][0]

    def user_permission_status(self, userid) -> str:
        with self.__connection:
            result = self.__cursor.execute('SELECT `status` FROM `users` WHERE `userid` = ?', (userid,)).fetchall()
            return result[0][0]

    def BAN(self, userid):
        with self.__connection:
            self.__DataBaseLogger.warning(f"The user: {userid} was banned")
            return self.__cursor.execute("UPDATE `users` SET banned=? WHERE `userid`=? ", (True, userid))

    def UNBAN(self, userid):
        with self.__connection:
            self.__DataBaseLogger.warning(f"The user: {userid} was unbanned")
            return self.__cursor.execute("UPDATE `users` SET banned=? WHERE `userid`=? ", (False, userid))

    def add_user(self, userid: int):
        with self.__connection:
            return self.__cursor.execute("INSERT INTO `users` (`userid`,`status`,`banned`) VALUES(?,?,?)",
                                         (userid, "user", False,))

    def add_product(self, name, cost, img, description):
        with self.__connection:
            with open(img, "rb") as image_file:
                data = base64.b64encode(image_file.read())
                return self.__cursor.execute(
                    "INSERT INTO `shop_item` (`name`,`cost`,`img`,`description`) VALUES(?,?,?,?)",
                    (name, cost, data, description,))

    def add_to_basket(self, userid: int, item: str):
        with self.__connection:
            return self.__cursor.execute("INSERT INTO `user_basket` (`userid`,`item`,`count`) VALUES(?,?,?)",
                                         (userid, item, 1,))

    def get_shop_items(self):
        with self.__connection:
            return self.__cursor.execute("SELECT * FROM `shop_item`").fetchmany(4)

    def get_user_basket(self, userid: int):
        with self.__connection:
            return self.__cursor.execute("SELECT * FROM `user_basket` WHERE `userid`=?", (userid,)).fetchmany(5)

    def get_about_item(self, name: str):
        with self.__connection:
            return self.__cursor.execute("SELECT * FROM `shop_item` WHERE `name`=?", (name,)).fetchmany(1)

    def delete_basket(self, userid, item):
        with self.__connection:
            self.__DataBaseLogger.warning(f"DELETED COLUMN WITH DATA: USER:{userid}, ITEM: {item}")
            return self.__cursor.execute(
                "DELETE FROM `user_basket` WHERE userid=? and `rowid` IN (SELECT `rowid` FROM `user_basket` WHERE `item`=? LIMIT 1)",
                (userid, item,)).fetchmany(1)

    def close(self):
        """Закрываем соединение с БД"""
        self.__connection.close()
