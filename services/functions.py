#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import math
import os
import shutil
from datetime import datetime, timedelta, timezone

import aiofiles
import pytz
import csv
from aiocsv import AsyncWriter


# функции
def get_current_datetime(days: int = 0, hours: int = 0, minutes: int = 0, tz: str = "Europe/Moscow") -> datetime:
    """Возвращает сегодняшний datetime с учётом временной зоны Мск."""
    delta = timedelta(days=days, hours=hours, minutes=minutes)
    tz = pytz.timezone(tz)
    now = datetime.now(tz) + delta
    return now


def dt_formatted(str_type: int = None, minus_days: int = 0, plus_days: int = 0) -> str:
    """Возвращает сегодняшнюю дату строкой"""
    if str_type == 1:
        ft = '%d.%m.%Y'
    elif str_type == 2:
        ft = '%Y-%m-%d %H:%M:%S'
    elif str_type == 3:
        ft = '%d_%m_%Y'
    elif str_type == 4:
        ft = '%H:%M:%S'
    elif str_type == 5:
        ft = '%H'
    elif str_type == 6:
        ft = '%Y-%m-%d'
    elif str_type == 7:
        ft = '%d_%m_%y'
    else:
        ft = '%d.%m.%Y %H:%M:%S'

    return (get_current_datetime() - timedelta(days=minus_days) + timedelta(days=plus_days)).strftime(ft)


def to_datetime(date_string: str, date_format: str = '%Y-%m-%d %H:%M:%S'):
    return datetime.strptime(date_string, date_format)


def seconds_to_time(seconds: int, time_format: str = 'short') -> str:
    """Конвертация секунд в `ЧЧ:ММ:СС`
    
    :param seconds: количество секунд
    :param time_format: 'long' "%02d:%02d:%02d", 'short' "%02d:%02d"
    """
    seconds = seconds % (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    if time_format == 'long':
        return "%02d:%02d:%02d" % (hours, minutes, seconds)
    if time_format == 'short':
        return "%02d:%02d" % (hours, minutes)


# не используем
def _get_current_datetime(days: int = 0, hours: int = 3) -> datetime:
    """Получение реального времени на сервере. При добавлении days, можно получить смещение на n дней"""
    delta = timedelta(days=days, hours=hours, minutes=0)
    return datetime.now(timezone.utc) + delta


def time_in_range(period: int = None, date: str = None):
    """Текущее время в диапазоне [start, end]"""
    import datetime
    current = get_current_datetime().time()

    if period == 1:
        start = datetime.time(9, 0, 0)
        end = datetime.time(13, 00, 0)
        return start <= current <= end

    if period == 2:
        if dt_formatted(1) == date:
            start = datetime.time(22, 0, 0)
            end = datetime.time(23, 59, 59)
            return start <= current <= end
        elif dt_formatted(1, minus_days=1) == date:
            end = datetime.time(3, 00, 0)
            return current <= end
        else:
            return False
    else:
        return False


def unique(file_name: str) -> None:
    """Функция удаляющая дубли в переданном файле file_name: str название файла"""
    unique_lines = set(open(file_name, 'r', encoding='utf-8').readlines())
    open(file_name, 'w', encoding='utf-8').writelines(set(unique_lines))


async def write_report_csv(directory: str, name: str, headers: list, data: list):
    """Асинхронное создание файла csv"""
    file_name = f'{directory}/{name}'
    async with aiofiles.open(file_name, 'w', encoding='cp1251', newline='') as file:
        writer = AsyncWriter(file, quoting=csv.QUOTE_MINIMAL, delimiter=';')
        if headers:
            await writer.writerow(headers)
        await writer.writerows(data)
    return file_name


def create_directory(file_path: str) -> None:
    """Функция для создания директории file_path: str путь до файла"""
    if not os.path.exists(file_path):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
        try:
            os.makedirs(path)
        except Exception as e:
            logging.warning(f'{path} > {e}')


def clear_directory(file_path: str) -> None:
    """Функция удаляющая данные из папки file_path: str путь до файла"""
    if os.path.exists(file_path):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
        try:
            shutil.rmtree(path)
        except FileExistsError as e:
            logging.warning(f'{path} > {e}')


def make_lin(m_list):
    """Перевести вложенный список в плоский"""
    n_list = []
    for x in m_list:
        if isinstance(x, (list, tuple)):
            n_list += make_lin(x)
        else:
            n_list.append(x)
    return n_list


def add_to_startup(file_path=""):
    import getpass
    if file_path == "":
        file_path = os.path.dirname(os.path.realpath(__file__))
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % getpass.getuser()
    with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
        bat_file.write(r'start "" %s' % file_path)


def divide_list(list_string: list, size: int) -> list:
    """Функция возвращающая массив разделенный на равные части"""
    string_to_number = [string for string in list_string]
    divide = lambda lst, sz: [lst[i:i + sz] for i in range(0, len(lst), sz)]
    return divide(string_to_number, size)


def includes_number(text):
    """Функция проверяющая строку на число"""
    return any(map(str.isdigit, text))


def human_read_format(size):
    """Функция переводящая размер файла в понятный формат"""
    pwr = math.floor(math.log(size, 1024))
    suffix = ["Б", "КБ", "МБ", "ГБ", "ТБ", "ПБ", "ЭБ", "ЗБ", "ЙБ"]
    if size > 1024 ** (len(suffix) - 1):
        return "не знаю как назвать такое число :)"
    return f"{size / 1024 ** pwr:.0f}{suffix[pwr]}"
