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
    .add(InlineKeyboardButton(text='🏠 На базе', callback_data=1),
         InlineKeyboardButton(text='❌ Закрыть смену', callback_data=6))

queue_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2) \
    .add(KeyboardButton('🚗 Отъехать'), KeyboardButton('⏳ Позиция в очереди'), KeyboardButton('❌ Закрыть смену'))

yes_no = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2) \
    .add(KeyboardButton('Да'), KeyboardButton('Нет'))

commands = [
    BotCommand(command='/start', description='запуск бота (если меню потеряется)'),
    BotCommand(command='/myid', description='мой id'),
    BotCommand(command='/help', description='справка')]


async def set_commands(dp: Dispatcher, bot_commands: List[BotCommand], admin_ids: List[int] = None):
    """Установка меню команд для бота"""
    await dp.bot.set_my_commands(commands=bot_commands)

    if admin_ids:
        commands_for_admin = [
            BotCommand(command='/start', description='запуск бота (если меню потеряется)'),
            BotCommand(command='/myid', description='мой id'),
            BotCommand(command='/help', description='справка'),
            BotCommand(command='/log', description='лог программы'),
            BotCommand(command='/cancel', description='отменить действие')]
        for admin_id in admin_ids:
            try:
                await dp.bot.set_my_commands(
                    commands=commands_for_admin,
                    scope=BotCommandScopeChat(admin_id)
                )
            except ChatNotFound as e:
                logging.error(f"Установка команд для администратора {admin_id}: {e}")
