# Logistica Telegram bot

Telegram bot (Python >= **3.9**, aiogram) для организации очереди курьеров.<br/>

[![Donate](https://img.shields.io/badge/Donate-Yoomoney-green.svg)](https://yoomoney.ru/to/410019620244262)
![GitHub last commit](https://img.shields.io/github/last-commit/Guf-Hub/logistica_bot)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Guf-Hub/logistica_bot)
![lang](https://img.shields.io/badge/lang-Python-red)

### Установка
Скачать файлы:
```bash
https://github.com/Guf-Hub/logistica_bot.git
```
Обновить pip:
```bash
pip install --upgrade pip
```
Установить зависимости:
```bash
pip install -r requirements.txt
```

### Получить TELEGRAM_TOKEN
* Открыть в телеграм [@BotFather](https://t.me/BotFather);
* Меню команд > /mybots;
* Выбрать нужного бота;
* What do you want to do with the bot? > API Token.

### Содержимое .env файла
* TELEGRAM_TOKEN - API Token бота;
* ADMINS - массив (int или str) user id или '@username' администратора(-ов);
* GROUP_ID - массив (int или str) chanal id или '@chanal' канала(-ов).

```dotenv
TELEGRAM_TOKEN=
ADMINS=[]
GROUP_ID=[]
```