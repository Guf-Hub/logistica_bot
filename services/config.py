from typing import List, Optional, Union

from pydantic import BaseSettings

DEV = True


class DefaultConfig(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class TgBot(DefaultConfig):
    """Telegram API settings"""
    TELEGRAM_TOKEN: Optional[str] = None
    TELEGRAM_DEV_TOKEN: Optional[str] = None
    ADMINS: Optional[List[int]] = None
    MASTER: Optional[int] = None
    GROUP_ID: Optional[List[Union[str, list]]] = None


class Settings(BaseSettings):
    """App base settings"""
    tg: TgBot = TgBot()


class Restrictions:
    """Ограничения TG https://limits.tginfo.me/ru-RU"""
    MESSAGE_LENGTH: int = 4096
    CAPTION_LENGTH: int = 1024
    FILE_SIZE: int = 20000000
