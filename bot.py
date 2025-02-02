import discord
from discord.ext import commands
import json
import sqlite3
import os
import sys

# Открытие файла для записи лога
log_file = open('bot.log', 'a', encoding='utf-8')

# Перенаправление стандартного вывода и стандартной ошибки в файл
sys.stdout = log_file
sys.stderr = log_file

# Загрузка конфига
try:
    with open('config.json', 'r') as file:
        config = json.load(file)
    print("Конфиг загружен")
except Exception as e:
    print(f"Ошибка загрузки конфига: {e}")
    exit()

# Настройки бота
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

# Проверка наличия файла reputation.db
db_path = 'reputation.db'
if not os.path.exists(db_path):
    print(f"Файл базы данных {db_path} не найден. Создание новой базы данных.")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создание таблиц
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reputation (
            user_id INTEGER PRIMARY KEY,
            reputation INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_counts (
            user_id INTEGER PRIMARY KEY,
            message_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    print("Таблицы в базе данных созданы.")
else:
    # Подключение к существующей базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f"Подключение к базе данных {db_path} установлено.")

# Удаление стандартной команды help
bot.remove_command('help')

# Загрузка Cog-ов
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

# Запуск бота
@bot.event
async def on_ready():
    print(f'Бот {bot.user.name} запущен!')
    await load_cogs()
    print('Коги загружены!')

# Запуск бота
bot.run(config['token'])