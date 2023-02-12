# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
#
# from aiogram import types
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Text
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.utils.exceptions import Throttled
#
# from database.db import db
# from services.config import Settings
# from services.create_bot import bot, dp
# from services.functions import *
# from services.keybords import *
#
# tg = Settings().tg
# g = Settings().gl
#
#
# class NewStaff(StatesGroup):
#     """Класс для добавления нового сотрудника в БД(users)"""
#     user_id = State()
#     first_name = State()
#     position = State()
#
#
# # @dp.callback_query_handler() #Text(contains=['добавить','обновить', 'удалить'], ignore_case=True), state=None
# # async def callback_handler_staff(call: types.CallbackQuery, state=FSMContext):
# #     try:
# #         await dp.throttle('vote', rate=1)
# #     except Throttled:
# #         return await call.answer('Слишком много запросов...')
# #
# #     answer_data = call.data
# #
# #     if 'upd=' in call:
# #         user_id = answer_data.split('=')[1]
# #         await db.update('users', {'positon': "Логист"}, {'user_id':user_id})
# #         await message.answer('Обновили данные сотрудника 😁', reply_markup=boss_menu)
# #
# #     if 'act=' in answer_data:
# #         user_id = answer_data.split('=')[1]
# #         await db.update('users', {'status': 1}, {'user_id': user_id})
# #         await call.answer('Удалили сотрудника 😈')
# #
# #     elif 'del=' in answer_data:
# #         user_id = answer_data.split('=')[1]
# #         await db.delete('users', 'user_id', str(user_id))
# #         await call.message.edit_text('Удалили сотрудника 😈')
# #
# #     elif 'add=' in answer_data:
# #         _, user_id, first_name = answer_data.split('=')
# #         print( _, user_id, first_name)
# #
# #         if not await db.is_active(user_id):
# #             async with state.proxy() as data:
# #                 data['user_id'] = user_id
# #                 data['first_name'] = first_name
# #             await NewStaff.next()
# #             await NewStaff.position.set()
# #             await bot.send_message(call.from_user.id, 'Выбери должность 👇', reply_markup=positions_menu)
# #         else:
# #             data = await db.get_user(user_id)
# #             print(data)
# #             data = f'Сотрудник: {data[3]} {data[2]}\n' \
# #                    f'Должность: {data[4]}\n' \
# #                    f'Статус: {data[5]}'
# #
# #             await bot.send_message(call.from_user.id, f'Сотрудник уже в базе 🤷‍♂\n{data}',
# #                                    reply_markup=boss_menu)
# #             await state.finish()
#
#
# async def add_staff(message: types.Message, state=FSMContext):
#     async with state.proxy() as data:
#         data['position'] = message.text
#     await NewStaff.next()
#     user_id = data['user_id']
#     await db.update('users', {'position': data['position'], 'status': 1}, {'user_id': user_id})
#     try:
#         await bot.send_message(user_id,
#                                f'Аккаунт активирован ✌\n'
#                                f'{data["first_name"]}, теперь ты в команде!!!'
#                                f'\nМенюшечка 👇', reply_markup=start_menu)
#         await message.answer(f'Аккаунт активирован ✌')
#     except Exception as e:
#         logging.warning(f'{user_id} {e}')
#     await state.finish()
#
#
# class UpdateStaff(StatesGroup):
#     """Класс для обновления данных по сотруднику в БД(users)"""
#     last_name = State()
#     position = State()
#     point = State()
#     is_admin = State()
#     is_supervisor = State()
#     points = State()
#
#
# async def update_staff(message: types.Message):
#     """Text(equals=['обновить']"""
#     staff = await db.get_active()
#     if staff:
#         staff_menu = InlineKeyboardMarkup(row_width=1) \
#             .add(*(InlineKeyboardButton(text=f'{i[3]} {i[2]}', callback_data=f'upd={i[0]}') for i in staff))
#         await message.reply('Выбери сотрудника 👇', reply_markup=staff_menu)
#     else:
#         await message.reply('Никого нет дома 😬', reply_markup=boss_menu)
#
# #
# # async def update_staff_position(message: types.Message, state=FSMContext):
# #     async with state.proxy() as data:
# #         data['position'] = message.text
# #     await UpdateStaff.next()
# #     db.update_staff(last_name=data['last_name'], position=data['position'], point=data['point'],
# #                     is_admin=data['is_admin'], is_supervisor=data['is_supervisor'], points=data['points'])
# #
# #     await message.answer('Обновили 😁', reply_markup=boss_menu)
# #     await state.finish()
#
#
# async def delete_staff(message: types.Message):
#     """Text(equals=['удалить']"""
#     staff = await db.get_active()
#     if staff:
#         staff_menu = InlineKeyboardMarkup(row_width=1) \
#             .add(*(InlineKeyboardButton(text=f'{i[3]} {i[2]}', callback_data=f'del={i[0]}') for i in staff))
#         await message.reply('Выбери сотрудника 👇', reply_markup=staff_menu)
#     else:
#         await message.reply('Никого нет дома 😬', reply_markup=boss_menu)
#
#
# async def activate_staff(message: types.Message):
#     """Text(equals=['активировать']"""
#     staff = await db.get_active()
#     if staff:
#         staff_menu = InlineKeyboardMarkup(row_width=1) \
#             .add(*(InlineKeyboardButton(text=f'{i[3]} {i[2]}', callback_data=f'act={i[0]}') for i in staff))
#         await message.reply('Выбери сотрудника 👇', reply_markup=staff_menu)
#     else:
#         await message.reply('Нет не активированных 😬', reply_markup=boss_menu)
#
#
# async def report_by_day(message: types.Message):
#     """Отчет по отправленным за день"""
#     date = dt_formatted(6)
#     data = db.get_report_by_period(date, date)
#
#     sv_data = db.get_supervisors()
#     point_count = dict(zip([p[2] for p in sv_data], [len(p[1].split(", ")) for p in sv_data]))
#
#     res = []
#     for i in data:
#         x = f'Ср. время: {(seconds_to_time(i[4]))} ч.\n' if i[4] is not None else ''
#         y = f'Норматив: {point_count[i[0]]} шт.\n' if i[0] in point_count else ''
#         res.append(f'{i[0]}\n'
#                    f'Тип: {i[1]}\n'
#                    f'{x}'
#                    f'{y}'
#                    f'Получено: {i[2]} шт.\n'
#                    f'Вовремя: {i[3]} шт.\n'
#                    f'{round(i[3] / i[2] * 100.0, 1)} %')
#
#     if len(res):
#         await bot.send_message(message.from_user.id, f'\n{"*" * 15}\n'.join(res), allow_sending_without_reply=True,
#                                reply_markup=boss_report_menu)
#     else:
#         await bot.send_message(message.from_user.id, f'Нет данных 🤷‍♂', allow_sending_without_reply=True,
#                                reply_markup=boss_report_menu)
#
#
# async def exception(message: types.Message):
#     """Отправить log файл"""
#     await message.answer_document(open(f'app.log', 'rb'), reply_markup=boss_menu)
#
#
# def register_handlers_admin(d: Dispatcher):
#     d.register_message_handler(add_staff, state=NewStaff.position)
#     d.register_message_handler(update_staff, Text(equals=['обновить'], ignore_case=True), state=None)
#     d.register_message_handler(activate_staff, Text(equals=['активировать'], ignore_case=True), state=None)
#     d.register_message_handler(delete_staff, Text(equals=['удалить'], ignore_case=True), state=None)
#     d.register_message_handler(report_by_day, Text(equals='📈 за сегодня', ignore_case=True))
#     d.register_message_handler(exception, Text(equals='!!', ignore_case=True))
