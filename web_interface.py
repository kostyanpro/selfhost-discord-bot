import sys
import time
import os
import subprocess
import threading
import json
import platform
from flask import Flask, render_template, request, redirect, url_for, Response

app = Flask(__name__)

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

with open('config.json', 'r') as f:
    config = json.load(f)

BOT_SCRIPT = 'bot.py'

bot_running = False
bot_process = None

# Корневая страница
@app.route('/')
def index():
    return redirect(url_for('control_panel'))

# Панель управления
@app.route('/control_panel')
def control_panel():
    return render_template('index.html', config=config, bot_running=bot_running)

# Запуск бота
@app.route('/start')
def start_bot():
    global bot_running, bot_process

    if not bot_running:
        try:
            if platform.system().startswith('W'):
                bot_process = subprocess.Popen(
                    [".\\winvenv\\Scripts\\python.exe", BOT_SCRIPT],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                bot_process = subprocess.Popen(
                    ['./linuxvenv/bin/python', BOT_SCRIPT],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            bot_running = True
            print("Бот запущен")

        except Exception as e:
            print(f"Ошибка при запуске бота: {e}")
            bot_running = False
    else:
        print("Бот уже запущен")

    return redirect(url_for('control_panel'))

# Остановка бота
@app.route('/stop')
def stop_bot():
    global bot_running, bot_process

    if bot_running and bot_process:
        try:
            if platform.system().startswith('W'):
                import signal
                bot_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                bot_process.terminate()

            bot_process.wait(timeout=10)
            bot_process = None
            bot_running = False
            print("Бот остановлен")
        except Exception as e:
            print(f"Ошибка при остановке бота: {e}")
    else:
        print("Бот не запущен")

    return redirect(url_for('control_panel'))

# Обновление конфига
@app.route('/update_config', methods=['POST'])
def update_config():
    global config
    new_config = {}
    for key in config:
        new_config[key] = request.form.get(key, config[key])
    with open('config.json', 'w') as f:
        json.dump(new_config, f, indent=4)
    config = new_config
    return redirect(url_for('control_panel'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)