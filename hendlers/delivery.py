#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import Throttled

from database.db import db
from services.config import Settings
from services.create_bot import bot, dp
from services.functions import *
from services.keybords import *
from services.questions import positions


tg = Settings().tg
g = Settings().gl


# Выход из состояния
async def cancel(message: types.Message, state=FSMContext):
    if not message.chat.type == 'private':
        return
    user_id = message.from_user.id
    if user_id in tg.ADMINS or user_id in set(x[0] for x in await db.get_active()):
        current_state = await state.get_state()
        if message.text.lower() in ['отмена', 'отменить', '❌ отмена', '/cancel']:
            if current_state is None:
                await message.reply('Отмена выполнена')
                if user_id in tg.ADMINS:
                    await message.answer('Еще вопросы? 👇', reply_markup=boss_menu)
                elif await db.is_logist(user_id):
                    await message.answer('Менюшечка 👇', reply_markup=queue_menu)
                else:
                    await message.answer('Еще вопросы? 👇', reply_markup=staff_menu)
            else:
                await state.finish()
                await message.reply('Отмена выполнена')
                if user_id in tg.ADMINS:
                    await message.answer('Еще вопросы? 👇', reply_markup=boss_menu)
                elif await db.is_logist(user_id):
                    await message.answer('Менюшечка 👇', reply_markup=queue_menu)
                else:
                    await message.answer('Еще вопросы? 👇', reply_markup=staff_menu)
    else:
        await message.reply('Нет доступа', reply_markup=remove)


class UpdateStaff(StatesGroup):
    """Класс для обновления данных по сотруднику в БД(users)"""
    user_id = State()
    position = State()


async def update_staff(message: types.Message):
    """Text(equals=['обновить']"""
    staff = await db.get_active()
    if staff:
        staff_menu = InlineKeyboardMarkup(row_width=1) \
            .add(*(InlineKeyboardButton(text=f'{i[3]} {i[2]}', callback_data=f'upd={i[0]}') for i in staff))
        await message.reply('Выбери сотрудника 👇', reply_markup=staff_menu)
    else:
        await message.reply('Никого нет дома 😬', reply_markup=boss_menu)


async def update_staff_end(message: types.Message, state=FSMContext):
    text = message.text
    if text in positions:
        async with state.proxy() as data:
            data['position'] = text
        await UpdateStaff.next()
        await db.update('users', {'position': data['position']}, {'user_id': data['user_id']})
        await message.answer(f'Должность обновили на {text} 😁', reply_markup=boss_menu)
        await state.finish()
    else:
        await UpdateStaff.position.set()
        positions_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1) \
            .add(*(KeyboardButton(text) for text in positions))
        await message.reply('Выбери 👇', reply_markup=positions_menu)


async def activate_staff(message: types.Message):
    """Text(equals=['активировать']"""
    staff = await db.get_no_active()
    if staff:
        staff_menu = InlineKeyboardMarkup(row_width=1) \
            .add(*(InlineKeyboardButton(text=f'{i[3]} {i[2]}', callback_data=f'act={i[0]}') for i in staff))
        await message.reply('Выбери сотрудника 👇', reply_markup=staff_menu)
    else:
        await message.reply('Нет не активированных 😬', reply_markup=boss_menu)


async def delete_staff(message: types.Message):
    """Text(equals=['удалить']"""
    staff = await db.get_active()
    if staff:
        staff_menu = InlineKeyboardMarkup(row_width=1) \
            .add(*(InlineKeyboardButton(text=f'{i[3]} {i[2]}', callback_data=f'del={i[0]}') for i in staff))
        await message.reply('Выбери сотрудника 👇', reply_markup=staff_menu)
    else:
        await message.reply('Никого нет дома 😬', reply_markup=boss_menu)


class Queue(StatesGroup):
    """Класс для сбора данных об очереди"""
    line = State()
    user_id = State()
    staff = State()
    status = State()


async def open_shift(message: types.Message):
    """Начало работы"""
    user_id = message.from_user.id
    if user_id not in set(x[0] for x in await db.get_active()):
        await message.reply('Нет доступа', reply_markup=remove)
    else:
        line = await db.last_line(dt_formatted(6))
        in_queue = await db.is_open(user_id, dt_formatted(6))
        name = await db.get_user_name(user_id)

        if not in_queue:
            await db.insert('working_mode', [{
                'user_id': user_id,
                'staff': name,
                'status': 0
            }])

            if line:
                await db.insert('delivery', [{
                    'user_id': user_id,
                    'line': line + 1,
                    'staff': name,
                    'status': 1
                }])
            else:
                await db.insert('delivery', [{
                    'user_id': user_id,
                    'line': 1,
                    'staff': name,
                    'status': 1
                }])

            await message.reply(f'<b>Смена открыта</b>\n'
                                f'Вы записаны в очередь.\n'
                                f'Хорошего рабочего дня.', reply_markup=queue_menu)
            await bot.send_message(tg.GROUP_ID, f'<b>{name}</b>\nОткрыл смену', reply_markup=remove)
        else:
            await message.answer(f'⚠ Вы уже сегодня отработали!!!\nЖдем вас завтра', reply_markup=start_menu)


async def queue_num(message: types.Message):
    """Позиция в очереди"""
    user_id = message.from_user.id
    if user_id not in set(x[0] for x in await db.get_active()):
        await message.reply('Нет доступа', reply_markup=remove)
    else:
        queue = await db.queue_num(dt_formatted(6))
        if queue:
            for i, u_id in enumerate(queue):
                if u_id[0] == user_id:
                    await message.answer(f'Ваш номер: {i + 1}', reply_markup=queue_menu)
                    break
        else:
            await message.answer(f'⚠ Вас нет в очереди!!!', reply_markup=staff_menu)


async def queue(message: types.Message):
    """Список курьеров в очереди"""
    user_id = message.from_id
    if user_id in tg.ADMINS or user_id in set(x[0] for x in await db.get_active()):
        queue = await db.queue(dt_formatted(6))
        if queue:
            queue_staff_menu = InlineKeyboardMarkup(row_width=1) \
                .add(*(InlineKeyboardButton(text=f'{text[1]}', callback_data=f'get_queue={text[0]}') for text in queue))
            await message.answer(f'✅ Текущая очередь:', reply_markup=queue_staff_menu)
        else:
            if user_id in tg.ADMINS:
                await message.answer(f'⚠ Очередь пуста!!!', reply_markup=boss_menu)
            else:
                await message.answer(f'⚠ Очередь пуста!!!', reply_markup=logist_menu)
    else:
        await message.reply('Нет доступа', reply_markup=remove)


async def drive_off(message: types.Message):
    """Отъехать"""
    if message.from_id not in set(x[0] for x in await db.get_active()):
        await message.reply('Нет доступа', reply_markup=remove)
    else:
        await message.answer('Куда отъезжаете?', reply_markup=drive_out_menu)


@dp.callback_query_handler()
async def callback_handler(call: types.CallbackQuery, state=FSMContext):
    try:
        await dp.throttle('vote', rate=1)
    except Throttled:
        return await call.answer('Слишком много запросов...')

    name = call.from_user.full_name

    if call.data in ['Мойка', 'Шинка', 'Обед', 'Магазин', 'Прочее']:
        user_id = call.from_user.id
        name = await db.get_user_name(user_id)
        await db.update('delivery', {'status': 5}, {'user_id': user_id})
        await bot.send_message(tg.GROUP_ID, f'<b>{name}</b>\nОтъехал <i>({call.data})</i>')
        await call.message.edit_text(f'✅ Статус установлен')
        await bot.send_message(user_id, 'Когда вернётесь, нажмите кнопку 👇', reply_markup=back_menu_inline)

    elif 'get_queue=' in call.data:
        user_id = call.data.split('=')[1]
        name = await db.get_user_name(user_id)
        route_type = InlineKeyboardMarkup(row_width=2) \
            .add(
            InlineKeyboardButton(text='ЭКС', callback_data=f'set_queue={user_id}=2=-1'),
            InlineKeyboardButton(text='МОЛ', callback_data=f'set_queue={user_id}=3=-1'),
            InlineKeyboardButton(text='Полный', callback_data=f'set_queue={user_id}=4=1'))
        await call.message.edit_text(f'{name}\nКуда отправляем?', reply_markup=route_type)

    elif 'set_queue=' in call.data:

        _, user_id, status, line = call.data.split('=')
        update = {
            'status': status
        }
        last_line = await db.last_line(dt_formatted(6))
        if line == 1:
            update['line'] = last_line + 1
        await db.update('delivery', update, {'user_id': user_id})
        name = await db.get_user_name(user_id)
        await call.message.edit_text("✅ Статус установлен")
        if status == 2:
            await bot.send_message(tg.GROUP_ID, f'<b>{name}</b>\nНа экспресс доставке', reply_markup=remove)
        elif status == 3:
            await bot.send_message(tg.GROUP_ID, f'<b>{name}</b>\nНа молнии', reply_markup=remove)
        else:
            await bot.send_message(tg.GROUP_ID, f'<b>{name}</b>\nНа полном маршруте', reply_markup=remove)

        msg = 'Вы отправлены на доставку.\nКогда вернётесь, нажмите кнопку 👇'
        if status in [2, 3]:
            await bot.send_message(user_id, msg, reply_markup=exp_menu)
        else:
            await bot.send_message(user_id, msg, reply_markup=long_menu)
        await asyncio.sleep(5)
        queue = await db.queue(dt_formatted(6))
        if queue:
            queue_staff_menu = InlineKeyboardMarkup(row_width=1) \
                .add(*(InlineKeyboardButton(text=f'{text[1]}', callback_data=f'get_queue={text[0]}') for text in queue))
            await call.message.edit_text(f'✅ Текущая очередь:', reply_markup=queue_staff_menu)

    elif call.data == "1":
        user_id = call.from_user.id
        name = await db.get_user_name(user_id)
        await db.update('delivery', {'status': 1}, {'user_id': user_id})
        await bot.send_message(tg.GROUP_ID, f'<b>{name}</b>\nНа базе', reply_markup=remove)
        await call.message.edit_text("✅ Статус установлен")
        await bot.send_message(call.from_user.id, f'✅ Вы записаны в очередь.', reply_markup=queue_menu)

    elif call.data == "6":
        user_id = call.from_user.id
        await CloseShift.yes.set()
        await bot.send_message(call.from_user.id, 'Уверены, что хотите закрыть смену? 👇', reply_markup=yes_no)

    elif 'upd=' in call.data:
        user_id = call.data.split('=')[1]
        async with state.proxy() as data:
            data['user_id'] = user_id
        await UpdateStaff.next()
        await UpdateStaff.position.set()

        positions_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1) \
            .add(*(KeyboardButton(text) for text in positions))

        await bot.send_message(call.from_user.id, 'Выбери должность 👇', reply_markup=positions_menu)

    elif 'del=' in call.data:
        user_id = call.data.split('=')[1]
        name = call.data.split('=')[0]
        await db.delete('users', 'user_id', str(user_id))
        await call.message.edit_text(f'Удалили сотрудника {name} 😈')
        await bot.send_message(call.from_user.id, f'Еще вопросы? 👇', reply_markup=boss_menu)


async def back(message: types.Message):
    """На базе"""
    user_id = message.from_user.id
    if user_id not in set(x[0] for x in await db.get_active()):
        await message.reply('Нет доступа', reply_markup=remove)
    else:
        line = await db.last_line(dt_formatted(6))
        name = await db.get_user_name(user_id)
        await db.update('delivery', {'line': line + 1, 'status': 1}, {'user_id': user_id})
        await bot.send_message(tg.GROUP_ID, f'<b>{name}</b>\nНа базе', reply_markup=remove)
        await message.answer(f'✅ Запись добавлена.\nВы записаны в очередь.', reply_markup=queue_menu)


async def exp(message: types.Message):
    """После ЭКС/МОЛ"""
    user_id = message.from_user.id
    if user_id not in set(x[0] for x in await db.get_active()):
        await message.reply('Нет доступа', reply_markup=remove)
    else:
        name = await db.get_user_name(user_id)
        await db.update('delivery', {'status': 1}, {'user_id': user_id})
        await bot.send_message(tg.GROUP_ID, f'<b>{name}</b>\nВернулся с ЭКС/МОЛ', reply_markup=remove)
        await message.answer(f'✅ Запись добавлена.\nВы записаны в очередь.', reply_markup=queue_menu)


class CloseShift(StatesGroup):
    """Сохранение ответа на вызов Закрыть смену"""
    yes = State()


async def close_shift_start(message: types.Message):
    """Закрыть смену"""
    await CloseShift.yes.set()
    await message.reply('Уверены, что хотите закрыть смену? 👇', reply_markup=yes_no)


async def close_shift_end(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['yes'] = message.text.strip()
    await CloseShift.next()

    user_id = message.from_user.id
    if data['yes'] == 'Да':
        name = await db.get_user_name(user_id)
        await db.delete('delivery', 'user_id', str(user_id))
        await db.insert('working_mode', [{
            'user_id': user_id,
            'staff': name,
            'status': 6
        }])

        await bot.send_message(tg.GROUP_ID, f'<b>{name}</b>\nЗакрыл смену', reply_markup=remove)
        await message.answer('✅ Смена закрыта', reply_markup=start_menu)
        await state.finish()
    else:
        await message.answer('Ошиблись, ну с кем не бывает 😁', reply_markup=staff_menu)
        await state.finish()


async def empty(message: types.Message):
    """Не понятные сообщения"""
    if not message.chat.type == 'private':
        return

    user_id = message.from_user.id
    if user_id in tg.ADMINS or user_id in set(x[0] for x in await db.get_active()):
        if user_id in tg.ADMINS:
            await message.answer('Что за ересь??? 🤣\nУчи матчасть >>> /help', disable_web_page_preview=True)
        elif await db.is_logist(user_id):
            await message.answer('Что за ересь??? 🤣\nУчи матчасть >>> /help', disable_web_page_preview=True)
        else:
            await message.answer('Что за ересь??? 🤣\nУчи матчасть >>> /help', disable_web_page_preview=True)
    else:
        await message.reply('Нет доступа', reply_markup=remove)


def register_handlers_delivery(d: Dispatcher):
    d.register_message_handler(cancel, commands='cancel', state='*')
    d.register_message_handler(cancel, Text(equals=['отмена', '❌ отмена', '⬆ Выйти'], ignore_case=True), state='*')

    d.register_message_handler(update_staff, Text(equals=['обновить'], ignore_case=True), state=None)
    d.register_message_handler(update_staff_end, state=UpdateStaff.position)
    d.register_message_handler(delete_staff, Text(equals=['удалить'], ignore_case=True), state=None)

    d.register_message_handler(open_shift, Text(equals=['✅ Открыть смену'], ignore_case=True), state=None)
    d.register_message_handler(queue_num, Text(equals=['⏳ Позиция в очереди'], ignore_case=True), state=None)
    d.register_message_handler(drive_off, Text(equals=['🚗 Отъехать'], ignore_case=True), state=None)
    d.register_message_handler(exp, Text(equals=['⚡ После ЭКС/МОЛ'], ignore_case=True), state=None)
    d.register_message_handler(back, Text(equals=['🏠 На базе'], ignore_case=True), state=None)
    d.register_message_handler(close_shift_start, Text(equals=['❌ Закрыть смену'], ignore_case=True), state=None)
    d.register_message_handler(close_shift_end, state=CloseShift.yes)
    d.register_message_handler(queue, Text(equals=['Очередь'], ignore_case=True), state=None)
    dp.register_message_handler(empty)
