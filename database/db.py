#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Union, List, Tuple, Dict

from aiosqlite import connect
from services.config import Settings
from services.logger import setup_logger

setup_logger("INFO")
tg = Settings().tg


class SingletonDecorator(object):
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = self.klass(*args, **kwargs)
        return self.instance

## основной
# class Singleton:
#     def __new__(cls, *args, **kwargs):
#         if not hasattr(cls, "_instance"):
#             cls._instance = super().__new__(cls)
#         return cls._instance

# class Singleton(object):
#     def __new__(cls):
#         if not hasattr(cls, 'instance'):
#             cls.instance = super(Singleton, cls).__new__(cls)
#         return cls.instance


@SingletonDecorator
# class Database(Singleton): # основной
class Database:
    """Класс для работы с базой данных"""

    def __init__(self, path: str, tables: dict):
        loop = asyncio.get_event_loop()
        loop.create_task(self._init(path, tables))

    async def _init(self, database, tables):
        self.conn = await connect(database)
        self.cursor = await self.conn.cursor()
        for i in tables.keys():
            await self.cursor.executescript(tables[i])

        rows = ['Смена открыта', 'На базе', 'Экспресс', 'Молния', 'Полный маршрут', 'Отъехал', 'Смена закрыта']
        # info = await self.cursor.execute('SELECT * FROM states')
        if await db.fetchall('states', ['*']) is None:
            await db.insert('states', [{'id': i, 'status': row} for i, row in enumerate(rows)])
            # await db.drop_table('states')
            # for user_id in tg.ADMINS:
            #     if not await db.is_user_exist(user_id):
            #         await db.insert('users', [{
            #             'user_id': user_id,
            #             'username': username,
            #             'first_name': first_name,
            #             'last_name': last_name,
            #             'status': 1
            #         }])

        logging.info(f"Database {database.split('/')[1].upper()} connection made successfully")

    async def is_user_exist(self, user_id: Union[str, int]) -> bool:
        """Проверка наличия user_id в БД(users) по user_id"""
        await self.cursor.execute("SELECT * FROM users WHERE user_id=?", [user_id])
        response = await self.cursor.fetchmany(1)
        return bool(len(response))

    async def get_user_name(self, user_id: Union[str, int]) -> List[Tuple]:
        """Получить Фамилия Имя по user_id из БД(users)"""
        await self.cursor.execute(f"SELECT last_name ||' '|| first_name FROM users WHERE user_id=?", [user_id])
        name = await self.cursor.fetchmany(1)
        if bool(len(name)):
            return name[0][0]
        else:
            return None

    async def get_user(self, user_id: Union[str, int]) -> List[Tuple]:
        """Получить Фамилия Имя по user_id из БД(users)"""
        await self.cursor.execute(f"SELECT * FROM users WHERE user_id=?", [user_id])
        name = await self.cursor.fetchmany(1)
        if bool(len(name)):
            return name[0]
        else:
            return None

    async def get_active_staff_names(self) -> List[Tuple]:
        """Получить user_id, first_name, last_name сотрудника из БД(users), статус активный (status=1)"""
        await self.cursor.execute(f"SELECT user_id, first_name, last_name FROM users "
                                  f"WHERE status=1 ORDER BY last_name").fetchall()
        return await self.cursor.fetchall()

    async def get_active(self) -> List[Tuple]:
        """Получить все данные по сотрудникам из БД(users), статус активный (status=1)"""
        await self.cursor.execute("SELECT * FROM users WHERE status=1 ORDER BY last_name")
        return await self.cursor.fetchall()

    async def get_no_active(self) -> List[Tuple]:
        """Получить все данные по сотрудникам из БД(users), статус активный (status=1)"""
        await self.cursor.execute("SELECT * FROM users WHERE status=0 ORDER BY last_name")
        return await self.cursor.fetchall()

    async def is_active(self, user_id: Union[str, int]) -> bool:
        """Проверка наличия user_id в БД(users) по user_id"""
        await self.cursor.execute("SELECT * FROM users WHERE user_id=? AND status=1", [user_id])
        response = await self.cursor.fetchmany(1)
        return bool(len(response))

    async def get_logists(self) -> List[Tuple]:
        """Получить список user_id Логистов из БД(users)"""
        await self.cursor.execute("SELECT user_id FROM users WHERE position='Логист' AND status=1")
        return await self.cursor.fetchall()

    async def is_logist(self, user_id: Union[str, int]) -> bool:
        """Проверка user_id, что должность Логист в БД(users)"""
        await self.cursor.execute(f"SELECT * FROM users "
                                  f"WHERE user_id=? AND position='Логист' AND status=1", [user_id])
        response = await self.cursor.fetchmany(1)
        return bool(len(response))

    async def is_open(self, user_id: Union[str, int], date: str) -> bool:
        """Проверка user_id, в очереди"""
        await self.cursor.execute(f"SELECT * FROM working_mode "
                                  f"WHERE user_id=? AND date(add_date_time)=? AND status=0", [user_id, date])
        response = await self.cursor.fetchmany(1)
        return bool(len(response))

    async def last_line(self, date: str):
        """Последний номер в очереди"""
        await self.cursor.execute(
            "SELECT MAX(line) FROM delivery WHERE date(add_date_time)=?", [date])
        line = await self.cursor.fetchone()
        if line:
            return line[0]
        else:
            return None

    async def queue_num(self, date: str):
        """Номер в очереди по user_id на дату"""
        await self.cursor.execute(
            f"SELECT user_id FROM delivery WHERE date(add_date_time)=?", [date])
        num = await self.cursor.fetchall()
        if num:
            return num
        else:
            return None

    async def queue(self, date: str):
        """Список очереди на дату"""
        await self.cursor.execute(
            f"SELECT user_id, staff, line, status FROM delivery "
            f"WHERE date(add_date_time)=? AND status=1", [date])  # ORDER BY line
        queue = await self.cursor.fetchall()
        if queue:
            return queue
        else:
            return None

    async def insert(self, table: str, column_values: List[dict]) -> None:
        """Вставить множество строк в таблицу из словаря"""
        for item in column_values:
            columns = ', '.join(item.keys())
            values = [tuple(item.values())]
            placeholders = ', '.join('?' * len(item.keys()))
            await self.cursor.executemany(f'INSERT OR IGNORE INTO {table} ({columns}) VALUES({placeholders})', values)
            await self.conn.commit()
            logging.info(f'Добавили данные в БД, таблица {table.upper()}')

    async def fetchone(self, table: str, columns: str, filters: dict) -> Union[Dict, None]:
        """Получить запись из таблицы"""
        cols = []
        for key in filters.keys():
            cols.append(f'{key}=?')
        value = ' AND '.join(cols)
        request = f'SELECT {columns} FROM {table} WHERE {value}'
        await self.cursor.execute(request, tuple(filters.values()))
        result = await self.cursor.fetchone()
        if not await result.fetchone():
            return
        result_dict = {}
        for index, col in enumerate(columns.split(',')):
            result_dict[col.strip()] = result[index]
        return result_dict

    async def fetchall(self, table: str, columns: List[str]) -> Union[List[Dict], None]:
        """Получить все записи из таблицы"""
        columns_joined = ", ".join(columns)
        await self.cursor.execute(f"SELECT {columns_joined} FROM {table}")
        rows = await self.cursor.fetchall()
        if not rows:
            return
        result = []
        for row in rows:
            dict_row = {}
            for index, column in enumerate(columns):
                dict_row[column] = row[index]
            result.append(dict_row)
        return result

    async def update(self, table: str, new_data: dict, filters: dict) -> None:
        """Обновить записи в таблице"""
        cols = []
        for key in new_data.keys():
            cols.append(f'{key}=?')
        new_data_str = ', '.join(cols)
        cols = []
        for key in filters.keys():
            cols.append(f'{key}=?')
        filters_str = ' AND '.join(cols)
        values = tuple(new_data.values()) + tuple(filters.values())
        await self.cursor.execute(f'UPDATE {table} SET {new_data_str} WHERE {filters_str}', values)
        await self.conn.commit()
        logging.info(f'Обновили данные в БД, таблица {table.upper()}')

    async def delete(self, table: str, column: str, value: str) -> None:
        """Удалить запись из таблицы"""
        await self.cursor.execute(f"DELETE FROM {table} WHERE {column}=?", [value])
        await self.conn.commit()

    async def drop_table(self, table: str) -> None:
        """Удалить все записи из таблицы"""
        rows = await self.cursor.execute(f'DELETE FROM {table};', )
        await self.conn.commit()
        logging.info(f'Удалили данные в БД, таблица {table.upper()} {rows.rowcount} записей')

    async def close(self, dp):
        await self.conn.close()


sql_tables = {
    'working_mode': '''CREATE TABLE IF NOT EXISTS working_mode (
    id            INTEGER         PRIMARY KEY ASC AUTOINCREMENT,
    add_date_time DATETIME        DEFAULT (datetime('now', 'localtime') ),
    user_id       INTEGER         NOT NULL
                                  REFERENCES users (user_id) ON DELETE CASCADE
                                                             ON UPDATE CASCADE,
    staff         VARCHAR (1, 30) NOT NULL,
    status        INTEGER         DEFAULT (1) 
                                  NOT NULL
                                  REFERENCES status (id) ON DELETE CASCADE
                                                         ON UPDATE CASCADE);''',

    'delivery': '''CREATE TABLE IF NOT EXISTS delivery (
    id            INTEGER         PRIMARY KEY ASC AUTOINCREMENT,
    add_date_time DATETIME        DEFAULT (datetime('now', 'localtime') ),
    user_id       INTEGER         NOT NULL
                                  REFERENCES users (user_id) ON DELETE CASCADE
                                                             ON UPDATE CASCADE,
    line          INTEGER         NOT NULL,
    staff         VARCHAR (1, 30) NOT NULL,
    status        INTEGER         DEFAULT (1) 
                                  NOT NULL
                                  REFERENCES status (id) ON DELETE CASCADE
                                                         ON UPDATE CASCADE);''',

    'states': '''CREATE TABLE IF NOT EXISTS states (
    id            INTEGER         PRIMARY KEY ASC,
    status        VARCHAR (1, 30) NOT NULL);''',

    'users': '''CREATE TABLE IF NOT EXISTS users (
    user_id    INTEGER         PRIMARY KEY ASC,
    username   VARCHAR (4, 32)    NOT NULL,
    first_name VARCHAR (1, 64) NOT NULL,
    last_name  VARCHAR (1, 64) NOT NULL,
    position   VARCHAR (1, 30),
    status     INTEGER (1)     DEFAULT (0) 
                               NOT NULL);'''
}

db = Database('database/bot.db', sql_tables)
