#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import pytils
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import Throttled
from database.db import db
from services.config import Settings
from services.create_bot import bot, dp
from services.functions import get_current_datetime, write_report_csv
from services.keybords import *
from services.helper import positions, drive_out

tg = Settings().tg


async def cancel(message: types.Message, state=FSMContext):
    """Отмена действия"""
    if not message.chat.type == 'private':
        return
    user_id = message.from_user.id
    if user_id in tg.ADMINS or user_id in set(x[0] for x in await db.get_active()):
        current_state = await state.get_state()
        if message.text.lower() in ['отмена', 'отменить', '❌ отмена', '/cancel']:
            if current_state is None:
                await message.reply('Отмена выполнена')
                if user_id in tg.ADMINS:
                    await message.answer('Еще вопросы? 👇', reply_markup=admin_menu)
                elif await db.is_logist(user_id):
                    await message.answer('Менюшечка 👇', reply_markup=queue_menu)
                else:
                    await message.answer('Еще вопросы? 👇', reply_markup=staff_menu)
            else:
                await state.finish()
                await message.reply('Отмена выполнена')
                if user_id in tg.ADMINS:
                    await message.answer('Еще вопросы? 👇', reply_markup=admin_menu)
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
    """Обновление должности сотрудника"""
    staff = await db.get_active()
    if staff:
        staff_menu = InlineKeyboardMarkup(row_width=1) \
            .add(*(InlineKeyboardButton(text=f'{i[3]} {i[2]}', callback_data=f'upd={i[0]}') for i in staff))
        await message.reply('Выбери сотрудника 👇', reply_markup=staff_menu)
    else:
        await message.reply('Никого нет дома 😬', reply_markup=admin_menu)


async def update_staff_end(message: types.Message, state=FSMContext):
    text = message.text
    if text in positions:
        async with state.proxy() as data:
            data['position'] = text
        await UpdateStaff.next()
        await db.update('users', {'position': data['position']}, {'user_id': data['user_id']})
        await message.answer(f'Должность обновили на {text} 😁', reply_markup=admin_menu)
        await state.finish()
    else:
        await UpdateStaff.position.set()
        positions_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1) \
            .add(*(KeyboardButton(text) for text in positions))
        await message.reply('Выбери 👇', reply_markup=positions_menu)


async def delete_staff(message: types.Message):
    """Удаление сотрдника"""
    staff = await db.get_active()
    if staff:
        staff_menu = InlineKeyboardMarkup(row_width=1) \
            .add(*(InlineKeyboardButton(text=f'{i[3]} {i[2]}', callback_data=f'del={i[0]}') for i in staff))
        await message.reply('Выбери сотрудника 👇', reply_markup=staff_menu)
    else:
        await message.reply('Никого нет дома 😬', reply_markup=admin_menu)


async def open_shift(message: types.Message):
    """Начало работы"""
    user_id = message.from_user.id
    if user_id in set(x[0] for x in await db.get_active()):
        line = await db.last_line()
        name = await db.get_user_name(user_id)

        await db.insert('working_mode', [{
            'user_id': user_id,
            'staff': name,
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

        await db.insert('working_mode', [{
            'user_id': user_id,
            'staff': name,
            'status': 1
        }])

        await message.reply(f'<b>Смена открыта</b>\nВы записаны в очередь.\nХорошего рабочего дня.',
                            reply_markup=queue_menu)

        date_time = pytils.dt.ru_strftime(u"%d %B %y, %a", inflected=True, date=get_current_datetime())
        await bot.send_message(tg.GROUP_ID[0], f'<b>{name}</b>\n{date_time}\nОткрыл смену', reply_markup=remove)
    else:
        await message.reply('Нет доступа', reply_markup=remove)


async def queue_num(message: types.Message):
    """Позиция курьера в очереди"""
    user_id = message.from_user.id
    if user_id in set(x[0] for x in await db.get_active()):
        queue = await db.queue_num()
        if queue:
            for i, u_id in enumerate(queue):
                if u_id[0] == user_id:
                    await message.answer(f'Ваш номер: {i + 1}', reply_markup=queue_menu)
                    break
        else:
            await message.answer(f'⚠ Вас нет в очереди!!!', reply_markup=staff_menu)
    else:
        await message.reply('Нет доступа', reply_markup=remove)


async def queue(message: types.Message):
    """Список курьеров в очереди"""
    user_id = message.from_id
    if user_id in tg.ADMINS or user_id in set(x[0] for x in await db.get_active()):
        queue = await db.queue()
        if queue:
            queue_staff_menu = InlineKeyboardMarkup(row_width=1) \
                .add(*(InlineKeyboardButton(text=f'{text[1]}', callback_data=f'get_queue={text[0]}') for text in queue))
            await message.answer(f'✅ Текущая очередь:', reply_markup=queue_staff_menu)
        else:
            if user_id in tg.ADMINS:
                await message.answer(f'⚠ Очередь пуста!!!', reply_markup=admin_menu)
            else:
                await message.answer(f'⚠ Очередь пуста!!!', reply_markup=logist_menu)
    else:
        await message.reply('Нет доступа', reply_markup=remove)


async def drive_off(message: types.Message):
    """Отъехать"""
    if message.from_id in set(x[0] for x in await db.get_active()):
        drive_out_menu =  InlineKeyboardMarkup(row_width=1) \
            .add(*(InlineKeyboardButton(text=f'{i}', callback_data={i}) for i in drive_out))
        await message.answer('Куда отъезжаете?', reply_markup=drive_out_menu)
    else:
        await message.reply('Нет доступа', reply_markup=remove)


@dp.callback_query_handler()
async def callback_handler(call: types.CallbackQuery, state=FSMContext):
    """Отработка CallbackQuery"""
    try:
        await dp.throttle('vote', rate=1)
    except Throttled:
        return await call.answer('Слишком много запросов...')

    if call.data in ['Мойка', 'Шинка', 'Обед', 'Магазин', 'Прочее']:
        user_id = call.from_user.id
        name = await db.get_user_name(user_id)
        await db.update('delivery', {'status': 5}, {'user_id': user_id})
        await db.insert('working_mode', [{'user_id': user_id, 'staff': name, 'status': 5}])
        date_time = pytils.dt.ru_strftime(u"%d %B %y, %a", inflected=True, date=get_current_datetime())
        await bot.send_message(tg.GROUP_ID[0], f'<b>{name}</b>\n{date_time}\nОтъехал <i>({call.data})</i>')
        await call.message.edit_text(f'✅ Статус установлен')
        await bot.send_message(user_id, 'Когда вернётесь, нажмите кнопку 👇', reply_markup=back_menu_inline)

    elif 'get_queue=' in call.data:
        user_id = call.data.split('=')[1]
        name = await db.get_user_name(user_id)
        status = await db.fetchone('delivery', 'status', {'user_id': user_id})
        if status['status'] not in [2, 3]:
            route_type = InlineKeyboardMarkup(row_width=2) \
                .add(
                InlineKeyboardButton(text='ЭКС', callback_data=f'set_queue={user_id}=2'),
                InlineKeyboardButton(text='МОЛ', callback_data=f'set_queue={user_id}=3'),
                InlineKeyboardButton(text='Полный', callback_data=f'set_queue={user_id}=4'))
            await call.message.edit_text(f'{name}\nКуда отправляем?', reply_markup=route_type)
        else:
            await call.message.edit_text(f'Курьер недоступен\n{name}\nУже на маршруте')

    elif 'set_queue=' in call.data:
        _, user_id, status = call.data.split('=')
        user = await db.get_user(user_id)
        name = f'{user[3]} {user[2]}'
        username = user[1]
        date_time = pytils.dt.ru_strftime(u"%d %B %y, %a", inflected=True, date=get_current_datetime())

        if int(user_id) in set(x[0] for x in await db.get_active()):
            if status == "2":
                await db.insert('working_mode', [{'user_id': user_id, 'staff': name, 'status': 2}])
                await db.update('delivery', {'status': status, 'staff': f'ЭКСП - {name}'}, {'user_id': user_id})
                msg = f'Вы отправлены на ЭКСП доставку.\nКогда вернётесь, нажмите кнопку 👇'
                await bot.send_message(user_id, msg, reply_markup=exp_menu)

                await bot.send_message(tg.GROUP_ID[0],
                                       f'@{user[1]}\n<b>{name} (ЭКСП)</b>\n{date_time}\nНа экспресс доставке',
                                       reply_markup=remove)
                await bot.send_message(tg.GROUP_ID[1],
                                       f'@{user[1]}\n<b>{name} (ЭКСП)</b>\n{date_time}\nНа экспресс доставке',
                                       reply_markup=remove)
            elif status == "3":
                await db.insert('working_mode', [{'user_id': user_id, 'staff': name, 'status': 3}])
                await db.update('delivery', {'status': status, 'staff': f'МОЛ - {name}'}, {'user_id': user_id})
                msg = f'Вы отправлены на МОЛ доставку.\nКогда вернётесь, нажмите кнопку 👇'
                await bot.send_message(user_id, msg, reply_markup=exp_menu)

                await bot.send_message(tg.GROUP_ID[0], f'@{user[1]}\n<b>{name} (МОЛ)</b>\n{date_time}\nНа молнии',
                                       reply_markup=remove)
                await bot.send_message(tg.GROUP_ID[1], f'@{user[1]}\n<b>{name} (МОЛ)</b>\n{date_time}\nНа молнии',
                                       reply_markup=remove)
            else:
                await db.insert('working_mode', [{'user_id': user_id, 'staff': name, 'status': 4}])
                await db.update('delivery', {'status': status}, {'user_id': user_id})
                msg = 'Вы отправлены на полный маршрут.\nКогда вернётесь, нажмите кнопку 👇'
                await bot.send_message(user_id, msg, reply_markup=long_menu)

                await bot.send_message(tg.GROUP_ID[0], f'@{user[1]}\n<b>{name}</b>\n{date_time}\nНа полном маршруте',
                                       reply_markup=remove)
                await bot.send_message(tg.GROUP_ID[1], f'@{user[1]}\n<b>{name}</b>\n{date_time}\nНа полном маршруте',
                                       reply_markup=remove)
            await call.message.edit_text("✅ Статус установлен")

    elif call.data == "1":
        user_id = call.from_user.id
        name = await db.get_user_name(user_id)
        await db.update('delivery', {'status': 1}, {'user_id': user_id})
        await db.insert('working_mode', [{'user_id': user_id, 'staff': name, 'status': 1}])
        date_time = pytils.dt.ru_strftime(u"%d %B %y, %a", inflected=True, date=get_current_datetime())
        await bot.send_message(tg.GROUP_ID[0], f'<b>{name}</b>\n{date_time}\nНа базе', reply_markup=remove)
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
        await db.delete('users', 'user_id', str(user_id))
        await call.message.edit_text(f'Удалили сотрудника 😈')
        await bot.send_message(call.from_user.id, f'Еще вопросы? 👇', reply_markup=admin_menu)

    elif 'report=' in call.data:
        user_id = call.data.split('=')[1]
        response = await db.report(user_id)
        await call.message.edit_text('\n'.join([f'{i[0][0:-3]} | {i[1]} - {i[2]}' for i in response if i is not None]))

    elif 'close=' in call.data:
        user_id = call.data.split('=')[1]
        name = await db.get_user_name(user_id)
        close_name = await db.get_user_name(call.from_user.id)
        await db.delete('delivery', 'user_id', str(user_id))
        await db.insert('working_mode', [{'user_id': user_id, 'staff': name, 'status': 6}])
        date_time = pytils.dt.ru_strftime(u"%d %B %y, %a", inflected=True, date=get_current_datetime())
        if close_name:
            await bot.send_message(tg.GROUP_ID[0], f'<b>{name}</b>\n{date_time}\n{close_name} - закрыл смену')
        else:
            await bot.send_message(tg.GROUP_ID[0], f'<b>{name}</b>\n{date_time}\nАдмин - закрыл смену')
        if user_id in set(x[0] for x in await db.get_active()):
            await bot.send_message(user_id, '✅ Смена закрыта', reply_markup=start_menu)
        await call.message.edit_text(f'✅ Смена закрыта')


async def back(message: types.Message):
    """На базе"""
    user_id = message.from_user.id
    if user_id in set(x[0] for x in await db.get_active()):
        line = await db.last_line()
        name = await db.get_user_name(user_id)
        if line:
            await db.update('delivery', {'line': line + 1, 'status': 1}, {'user_id': user_id})
        else:
            await db.update('delivery', {'line': 1, 'status': 1}, {'user_id': user_id})
        await db.insert('working_mode', [{'user_id': user_id, 'staff': name, 'status': 1}])
        date_time = pytils.dt.ru_strftime(u"%d %B %y, %a", inflected=True, date=get_current_datetime())
        await bot.send_message(tg.GROUP_ID[0], f'<b>{name}</b>\n{date_time}\nНа базе', reply_markup=remove)
        await message.answer(f'✅ Запись добавлена.\nВы записаны в очередь.', reply_markup=queue_menu)
    else:
        await message.reply('Нет доступа', reply_markup=remove)


async def exp(message: types.Message):
    """После ЭКС/МОЛ"""
    user_id = message.from_user.id
    if user_id in set(x[0] for x in await db.get_active()):
        name = await db.get_user_name(user_id)
        await db.update('delivery', {'status': 1, 'staff': name}, {'user_id': user_id})
        await db.insert('working_mode', [{'user_id': user_id, 'staff': name, 'status': 1}])
        date_time = pytils.dt.ru_strftime(u"%d %B %y, %a", inflected=True, date=get_current_datetime())
        await bot.send_message(tg.GROUP_ID[0], f'<b>{name}</b>\n{date_time}\nВернулся с ЭКС/МОЛ', reply_markup=remove)
        await message.answer(f'✅ Запись добавлена.\nВы записаны в очередь.', reply_markup=queue_menu)
    else:
        await message.reply('Нет доступа', reply_markup=remove)


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
        await db.insert('working_mode', [{'user_id': user_id, 'staff': name, 'status': 6}])
        date_time = pytils.dt.ru_strftime(u"%d %B %y, %a", inflected=True, date=get_current_datetime())
        await bot.send_message(tg.GROUP_ID[0], f'<b>{name}</b>\n{date_time}\nЗакрыл смену', reply_markup=remove)
        await message.answer('✅ Смена закрыта', reply_markup=start_menu)
        await state.finish()
    else:
        await message.answer('Ошиблись, ну с кем не бывает 😁', reply_markup=staff_menu)
        await state.finish()


async def close_open_shift(message: types.Message):
    staff = await db.open_shift()
    if staff:
        staff_menu = InlineKeyboardMarkup(row_width=1) \
            .add(*(InlineKeyboardButton(text=f'{text[1]}', callback_data=f'close={text[0]}') for text in staff))
        await message.answer('Выберите сотрудника 👇', reply_markup=staff_menu)
    else:
        await message.answer('Все смены закрыты 😃')


async def report_staff(message: types.Message):
    """Отчет по сотруднику с последней открытой смены"""
    staff = await db.get_active_courier()
    staff_menu = InlineKeyboardMarkup(row_width=1) \
        .add(*(InlineKeyboardButton(text=f'{text[1]}', callback_data=f'report={text[0]}') for text in staff))
    await message.answer('Выберите сотрудника 👇', reply_markup=staff_menu)


async def report_all(message: types.Message):
    """Выгрузка всех данных по сотрудникам"""
    data = await db.report_csv()
    dir_name = 'src'
    if not os.path.exists(os.path.join(os.getcwd(), dir_name)):
        os.mkdir(dir_name)

    file = await write_report_csv(directory=os.path.join(os.getcwd(), dir_name),
                                  name='courier.csv',
                                  headers=['add_date_time', 'staff', 'status'],
                                  data=data)
    await bot.send_document(message.from_user.id, open(file, 'rb'))
    os.remove(file)


async def empty(message: types.Message):
    """Не понятные сообщения"""
    if not message.chat.type == 'private':
        return

    user_id = message.from_user.id
    if user_id in tg.ADMINS or user_id in set(x[0] for x in await db.get_active()):
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
    d.register_message_handler(close_open_shift, Text(equals=['❌ Закрыть'], ignore_case=True), state=None)
    d.register_message_handler(queue, Text(equals=['Очередь'], ignore_case=True), state=None)
    d.register_message_handler(report_staff, Text(equals=['📊 По сотруднику'], ignore_case=True), state=None)
    d.register_message_handler(report_all, Text(equals=['🗂 Отчет .csv'], ignore_case=True), state=None)
    dp.register_message_handler(empty)
