import logging
from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class TgBot:
    token: str
    liqtoken: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)
    logging.getLogger("CONFIG").info(f"ADMINS: {list(map(int, env.str('ADMINS').split()))}")
    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            liqtoken = env.str("LIQPAY"),
            admin_ids=list(map(int, env.str('ADMINS').split())),
            # admin_ids=env.list("ADMINS"),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        ),
        misc=Miscellaneous()
    )
