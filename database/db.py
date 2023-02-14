#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Union, List, Tuple, Dict

from aiosqlite import connect
from services.config import Settings
from services.logger import setup_logger
from services.helper import states

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


@SingletonDecorator
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

        if await db.fetchall('states', ['*']) is None:
            await db.insert('states', [{'id': i, 'status': row} for i, row in enumerate(states)])
        logging.info(f"Database {database.split('/')[1].upper()} connection made successfully")

    async def is_user_exist(self, user_id: Union[str, int]) -> bool:
        """Проверка наличия user_id в БД(users)"""
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
        """Получить * по user_id из БД(users)"""
        await self.cursor.execute(f"SELECT * FROM users WHERE user_id=?", [user_id])
        user = await self.cursor.fetchmany(1)
        if bool(len(user)):
            return user[0]
        else:
            return None

    async def get_active(self) -> List[Tuple]:
        """Получить все данные по сотрудникам из БД(users), статус активный (status=1)"""
        await self.cursor.execute("SELECT * FROM users WHERE status=1 ORDER BY last_name")
        return await self.cursor.fetchall()

    async def get_active_courier(self) -> List[Tuple]:
        """Получить все данные по Курьерам из БД(users), статус активный (status=1)"""
        await self.cursor.execute(f"SELECT user_id, last_name ||' '|| first_name FROM users "
                                  f"WHERE status=1 AND position='Курьер' ORDER BY last_name")
        return await self.cursor.fetchall()

    async def is_logist(self, user_id: Union[str, int]) -> bool:
        """Проверка user_id, что должность Логист в БД(users)"""
        await self.cursor.execute(f"SELECT * FROM users "
                                  f"WHERE user_id=? AND position='Логист' AND status=1", [user_id])
        response = await self.cursor.fetchmany(1)
        return bool(len(response))

    async def open_shift(self) -> bool:
        """Проверка количества открытых и закрытых смен в БД(working_mode)"""
        await self.cursor.execute(f"SELECT user_id, staff, COUNT(*) AS count "
                                  f"FROM working_mode WHERE status IN (0, 6) "
                                  f"GROUP BY staff HAVING COUNT(*) % 2 != 0;")
        return await self.cursor.fetchall()

    async def last_line(self):
        """Последний номер в очереди из БД(delivery)"""
        await self.cursor.execute(
            "SELECT MAX(line) FROM delivery")
        line = await self.cursor.fetchone()
        if line:
            return line[0]
        else:
            return None

    async def queue_num(self):
        """Номер в очереди по user_id из БД(delivery)"""
        await self.cursor.execute(
            f"SELECT user_id FROM delivery WHERE status in (1,2,3) ORDER BY line")
        num = await self.cursor.fetchall()
        if num:
            return num
        else:
            return None

    async def queue(self):
        """Список очереди из БД(delivery)"""
        await self.cursor.execute(
            f"SELECT user_id, staff, line, status FROM delivery WHERE status IN (1,2,3) ORDER BY line")
        queue = await self.cursor.fetchall()
        if queue:
            return queue
        else:
            return None

    async def report(self, user_id: Union[str, int]):
        """Отчет по user_id сотрудника из БД(working_mode)"""
        await self.cursor.execute(
            f"SELECT working_mode.add_date_time, working_mode.staff, states.status FROM working_mode "
            f"JOIN states ON states.id = working_mode.status "
            f"WHERE user_id=? AND date(add_date_time)>=date(("
            f"SELECT MAX(add_date_time) "
            f"FROM working_mode WHERE user_id=? AND status=0))", [user_id, user_id])
        response = await self.cursor.fetchall()
        if response:
            return response
        else:
            return None

    async def report_csv(self):
        """Получить все данные по сотрудникам из БД(working_mode)"""
        await self.cursor.execute(
            f"SELECT working_mode.add_date_time, working_mode.staff, states.status FROM working_mode "
            f"JOIN states ON states.id = working_mode.status")
        response = await self.cursor.fetchall()
        if response:
            return response
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
        if not result:
            return None
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
            return None
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
        """Закрыть соединение"""
        await self.conn.close()


sql_tables = {
    'working_mode': '''CREATE TABLE IF NOT EXISTS working_mode (
    id            INTEGER         PRIMARY KEY ASC AUTOINCREMENT,
    add_date_time DATETIME        DEFAULT (datetime('now', 'localtime') ),
    user_id       INTEGER         NOT NULL
                                  REFERENCES users (user_id) ON DELETE CASCADE
                                                             ON UPDATE CASCADE,
    staff         VARCHAR (1, 30) NOT NULL,
    status        INTEGER         DEFAULT (0) 
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
    username   VARCHAR (4, 32) NOT NULL,
    first_name VARCHAR (1, 64) NOT NULL,
    last_name  VARCHAR (1, 64) NOT NULL,
    position   VARCHAR (1, 30),
    status     INTEGER (1)     DEFAULT (0) 
                               NOT NULL);'''
}

db = Database('database/bot.db', sql_tables)
