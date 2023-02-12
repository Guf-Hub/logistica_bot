#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Файл запуска бота"""
import logging

from aiogram import types
from aiogram.utils import executor, exceptions
from database.db import db
from hendlers import *
from services.config import Settings
from services.create_bot import dp
from services.keybords import set_commands, bot_commands


async def on_startup(_):
    """Запуск бота (установка команд и рассылок)"""
    admins = Settings().tg.ADMINS
    if admins:
        await set_commands(dp, bot_commands, admin_ids=admins)
    else:
        await set_commands(dp, bot_commands)


@dp.errors_handler(exception=exceptions.RetryAfter)
async def exception_handler(update: types.Update, exception: exceptions.RetryAfter):
    return True


@dp.errors_handler(exception=exceptions.MessageNotModified)
async def message_not_modified_handler(update, error):
    return True

client.register_handlers_client(dp)  # команды
delivery.register_handlers_delivery(dp)  # запись очереди доставки


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=db.close)
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
