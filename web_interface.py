import time
import os
import subprocess
import threading
import json
import platform
from flask import Flask, render_template, request, redirect, url_for, Response

app = Flask(__name__)

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