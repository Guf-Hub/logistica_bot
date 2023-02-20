#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from typing import List

from aiogram import Dispatcher
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup, \
    BotCommandScopeChat, BotCommand
from aiogram.utils.exceptions import ChatNotFound

# Описание и кнопки
start_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False) \
    .add(KeyboardButton('✅ Открыть смену'))

staff_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2) \
    .add(KeyboardButton('🏠 На базе'),
         KeyboardButton('⚡ После ЭКС/МОЛ'),
         KeyboardButton('⏳ Позиция в очереди'),
         KeyboardButton('🚗 Отъехать'),
         KeyboardButton('❌ Закрыть смену'))

exp_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2) \
    .add(KeyboardButton('⚡ После ЭКС/МОЛ'),
         KeyboardButton('🚗 Отъехать'),
         KeyboardButton('❌ Закрыть смену'))

long_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2) \
    .add(KeyboardButton('🏠 На базе'),
         KeyboardButton('🚗 Отъехать'),
         KeyboardButton('❌ Закрыть смену'))

remove = ReplyKeyboardRemove()

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False) \
    .row(KeyboardButton('Очередь')) \
    .row(KeyboardButton('🗂 Отчет .csv'), KeyboardButton('📊 По сотруднику')) \
    .row(KeyboardButton('Удалить'), KeyboardButton('Обновить')) \
    .row(KeyboardButton('❌ Закрыть'))

logist_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1) \
    .add(KeyboardButton('Очередь'), KeyboardButton('📊 По сотруднику'), KeyboardButton('❌ Закрыть'))

back_menu_inline = InlineKeyboardMarkup(row_width=1) \
    .add(InlineKeyboardButton(text='🏠 На базе', callback_data='1'),
         InlineKeyboardButton(text='❌ Закрыть смену', callback_data='6'))

queue_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2) \
    .add(KeyboardButton('🚗 Отъехать'), KeyboardButton('⏳ Позиция в очереди'), KeyboardButton('❌ Закрыть смену'))

yes_no = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2) \
    .add(KeyboardButton('Да'), KeyboardButton('Нет'))

commands_staff = [
    BotCommand(command='/start', description='запуск бота (если меню потеряется)'),
    BotCommand(command='/myid', description='мой id'),
    BotCommand(command='/help', description='справка')]

commands_admin = [
    BotCommand(command='/start', description='запуск бота (если меню потеряется)'),
    BotCommand(command='/myid', description='мой id'),
    BotCommand(command='/help', description='справка'),
    BotCommand(command='/log', description='лог программы'),
    BotCommand(command='/cancel', description='отменить действие')]


async def set_commands(dp: Dispatcher,
                       staff_commands: List[BotCommand] = None,
                       admin_ids: List[int] = None,
                       admin_commands: List[BotCommand] = None):
    """Установка меню команд для бота"""
    from database.db import db
    for user_id in set(x[0] for x in await db.get_active()):
        try:
            await dp.bot.delete_my_commands(scope=BotCommandScopeChat(user_id))
        except ChatNotFound as e:
            logging.error(f"Удаление меню {user_id}: {e}")

    if staff_commands:
        await dp.bot.set_my_commands(commands=staff_commands)

    if admin_ids:
        for admin_id in admin_ids:
            try:
                await dp.bot.set_my_commands(
                    commands=admin_commands,
                    scope=BotCommandScopeChat(admin_id)
                )
            except ChatNotFound as e:
                logging.error(f"Установка команд для администратора {admin_id}: {e}")



async def set_commands(dp: Dispatcher,
                       staff_commands: List[BotCommand] = None,
                       admin_ids: List[int] = None,
                       admin_commands: List[BotCommand] = None):
    """Установка меню команд для бота"""
    if staff_commands:
        await dp.bot.set_my_commands(commands=staff_commands)

    if admin_ids and admin_commands:
        for admin_id in admin_ids:
            try:
                await dp.bot.set_my_commands(
                    commands=admin_commands,
                    scope=BotCommandScopeChat(admin_id)
                )
            except ChatNotFound as e:
                logging.error(f"Установка команд для администратора {admin_id}: {e}")
