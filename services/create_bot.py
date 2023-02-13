#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from services.config import Settings, DEV
from aiogram.contrib.fsm_storage.memory import MemoryStorage

settings = Settings()
storage = MemoryStorage()
TOKEN = settings.tg.TELEGRAM_DEV_TOKEN if DEV else settings.tg.TELEGRAM_TOKEN

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
