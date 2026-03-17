import discord
from discord.ext import commands
import json
import sqlite3
import os
import sys

DEFAULT_CONFIG = {
    "token": "",
    "prefix": "!",
    "ffmpeg_path": "",
    "create_channel_category": "",
    "max_create_channel": "10",
    "start_rep": "0",
    "count_message_for_rep": "20",
    "guild_id": "",
    "role_id": "",
    "muted_role_id": "",
    "success_icon": "",
    "error_icon": "",
    "info_icon": "",
    "warn_icon": "",
    "success_color": "0x2ecc71",
    "error_color": "0xe74c3c",
    "info_color": "0x3498db",
    "warn_color": "0xf1c40f",
    "eight_ball_answers": [
        "Бесспорно.", "Предрешено.", "Никаких сомнений.", "Определённо да.",
        "Можешь быть уверен в этом.", "Мне кажется — «да».", "Вероятнее всего.",
        "Хорошие перспективы.", "Знаки говорят — «да».", "Пока не ясно, попробуй снова.",
        "Спроси позже.", "Лучше не рассказывать.", "Сейчас нельзя предсказать.",
        "Сконцентрируйся и спроси опять.", "Даже не думай.", "Мой ответ — «нет».",
        "По моим данным — «нет».", "Перспективы не очень хорошие.", "Весьма сомнительно."
    ],
    "debug": 0
}

CONFIG_PATH = 'config.json'

if not os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        print(f"Файл {CONFIG_PATH} не найден и был создан. Заполните 'token' и перезапустите бота.")
    except Exception as e:
        print(f"Не удалось создать конфиг: {e}")
    sys.exit()

try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
        config = json.load(file)
    print("Конфиг загружен")
except Exception as e:
    print(f"Ошибка чтения конфига: {e}")
    sys.exit()

if config.get("debug") != 1:
    log_file = open('bot.log', 'a', encoding='utf-8')
    sys.stdout = log_file
    sys.stderr = log_file

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

db_path = 'reputation.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
    print(f"Инициализация новой базы данных {db_path}...")
    cursor.execute('CREATE TABLE IF NOT EXISTS reputation (user_id INTEGER PRIMARY KEY, reputation INTEGER DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS message_counts (user_id INTEGER PRIMARY KEY, message_count INTEGER DEFAULT 0)')
    conn.commit()
else:
    print(f"Подключение к базе данных {db_path} установлено.")

bot.remove_command('help')

async def load_cogs():
    if not os.path.exists('./cogs'):
        os.makedirs('./cogs')
        print("Папка './cogs' создана.")
        return

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Ког {filename} успешно загружен")
            except Exception as e:
                print(f"Ошибка загрузки кога {filename}: {e}")

@bot.event
async def on_ready():
    print(f'Бот {bot.user.name} запущен!')
    await load_cogs()
    print('Коги загружены!')
    try:
        await bot.tree.sync()
        print('Команды синхронизированы!')
    except Exception as e:
        print(f"Ошибка синхронизации команд: {e}")

# Запуск
if config['token']:
    bot.run(config['token'])
else:
    print("Ошибка: Токен не указан в config.json!")