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
start_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) \
    .add(KeyboardButton('✅ Открыть смену'))

staff_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2) \
    .add(KeyboardButton('🏠 На базе'),
         KeyboardButton('⚡ После ЭКС/МОЛ'),
         KeyboardButton('⏳ Позиция в очереди'),
         KeyboardButton('🚗 Отъехать'),
         KeyboardButton('❌ Закрыть смену'))

exp_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2) \
    .add(KeyboardButton('⚡ После ЭКС/МОЛ'),
         KeyboardButton('🚗 Отъехать'),
         KeyboardButton('❌ Закрыть смену'))

long_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2) \
    .add(KeyboardButton('🏠 На базе'),
         KeyboardButton('🚗 Отъехать'),
         KeyboardButton('❌ Закрыть смену'))

remove = ReplyKeyboardRemove()

boss_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) \
    .row(KeyboardButton('Очередь')) \
    .row(KeyboardButton('Удалить'), KeyboardButton('Обновить'))

back_menu = ReplyKeyboardMarkup(resize_keyboard=True) \
    .add(KeyboardButton('🏠 На базе'), KeyboardButton('❌ Закрыть смену'))

back_menu_inline = InlineKeyboardMarkup(row_width=1) \
    .add(InlineKeyboardButton(text='🏠 На базе', callback_data=1),
         InlineKeyboardButton(text='❌ Закрыть смену', callback_data=6))

drive_out_menu = InlineKeyboardMarkup(row_width=1) \
    .add(InlineKeyboardButton(text='Мойка', callback_data='Мойка'),
         InlineKeyboardButton(text='Шинка', callback_data='Шинка'),
         InlineKeyboardButton(text='Обед', callback_data='Обед'),
         InlineKeyboardButton(text='Магазин', callback_data='Магазин'),
         InlineKeyboardButton(text='Прочее', callback_data='Прочее'))

queue_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2) \
    .add(KeyboardButton('🚗 Отъехать'),
         KeyboardButton('⏳ Позиция в очереди'),
         KeyboardButton('❌ Закрыть смену'))

logist_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) \
    .add(KeyboardButton('Очередь'))

route_type = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2) \
    .add(KeyboardButton('ЭКС'),
         KeyboardButton('МОЛ'),
         KeyboardButton('Полный'),
         KeyboardButton('❌ Отмена'))

yes_no = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2) \
    .add(KeyboardButton('Да'), KeyboardButton('Нет'))

bot_commands = [
    BotCommand(command='/start', description='запуск бота (если меню потеряется)'),
    BotCommand(command='/myid', description='мой id'),
    BotCommand(command='/help', description='справка')]


async def set_commands(dp: Dispatcher, commands: List[BotCommand], admin_ids: List[int] = None):
    """Установка меню команд для бота"""
    await dp.bot.set_my_commands(commands=commands)

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
