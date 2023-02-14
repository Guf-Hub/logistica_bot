#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from aiogram import types
from database.db import db
from services.config import Settings
from services.keybords import *
from services.helper import help_msg

tg = Settings().tg


async def start(message: types.Message):
    if not message.chat.type == 'private':
        return

    user_id = message.from_user.id
    if message.text == '/myid':
        await message.answer(f'Твой Telegram id: {user_id}')

    if message.text == '/start':
        if user_id in tg.ADMINS or (
                await db.is_user_exist(user_id) and user_id in set(x[0] for x in await db.get_active())):
            if user_id in tg.ADMINS:
                await message.answer('Менюшечка 👇', reply_markup=admin_menu)
            elif await db.is_logist(user_id):
                await message.answer('Менюшечка 👇', reply_markup=logist_menu)
            else:
                if user_id not in set(x[0] for x in await db.open_shift()):
                    await message.answer('Менюшечка 👇', reply_markup=start_menu)
                else:
                    await message.reply('Менюшечка 👇', reply_markup=queue_menu)
        else:
            """Добавление новго сотрудника"""
            username = message.from_user.username
            name = message.from_user.full_name
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name

            if not name:
                await message.answer("❌ Установите Имя и Фамилию в настройках профиля!!!")
                return

            if not first_name:
                await message.answer("❌ Установите Имя в настройках профиля!!!")
                return

            if not last_name:
                await message.answer("❌ Установите Фамилию в настройках профиля!!!")
                return

            if not username:
                await message.answer("❌ Установите Username (5-32 символов) в настройках профиля!!!")
                return

            await db.insert('users', [{
                'user_id': user_id,
                'username': username,
                'first_name': first_name.strip(),
                'last_name': last_name.strip(),
                'position': 'Курьер',
                'status': 1
            }])

            welcome_msg = f'Привет, {first_name.strip()} 👋\n' \
                          f'Добро пожаловать в команду.\n' \
                          f'Я бот помощник, запишу рабочую инфу.\n' \
                          f'Нажмите октрыть смену, чтобы вставь в очередь 👇'

            await message.answer(welcome_msg, reply_markup=start_menu)

    if user_id in tg.ADMINS or user_id in set(x[0] for x in await db.get_active()):
        """Подсказка"""
        if message.text == '/help':
            if user_id in tg.ADMINS:
                await message.answer(help_msg['admin'], disable_web_page_preview=True)
            elif await db.is_logist(user_id):
                await message.answer(help_msg['logist'], disable_web_page_preview=True)
            else:
                await message.answer(help_msg['staff'], disable_web_page_preview=True)
        """Получить файл лога ошибок"""
        if message.text == '/log' and user_id in tg.ADMINS:
            await message.answer_document(open(f'app.log', 'rb'))


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start', 'myid', 'log', 'help'])
