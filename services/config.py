from typing import List, Optional, Union

from pydantic import BaseSettings


class DefaultConfig(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class TgBot(DefaultConfig):
    TELEGRAM_TOKEN: str
    ADMINS: Optional[List[int]] = None
    BOSS: Optional[List[int]] = None
    MASTER: Optional[int] = None
    GROUP_ID: Optional[Union[str, int]] = None


class Google(DefaultConfig):
    PASSWORD: str
    SERVICE_ACCOUNT_FILE: str
    BOOK_MAIN: str
    SHEET_DELIVERY: str


class Settings(BaseSettings):
    tg: TgBot = TgBot()
    gl: Google = Google()


class Restrictions:
    """Ограничения TG https://limits.tginfo.me/ru-RU"""
    MESSAGE_LENGTH: int = 4096
    CAPTION_LENGTH: int = 1024
    FILE_SIZE: int = 20000000
