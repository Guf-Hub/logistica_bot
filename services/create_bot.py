#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from services.config import Settings
from aiogram.contrib.fsm_storage.memory import MemoryStorage

settings = Settings()
storage = MemoryStorage()

bot = Bot(token=settings.tg.TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
