import time
import os
import subprocess
import threading
import json
import platform


from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)


''' загрузка конфига '''
with open('config.json', 'r') as f:
    config = json.load(f)


''' путь до бота '''
BOT_SCRIPT = 'bot.py'


''' статусы бота '''
bot_running = False
bot_process = None


''' считывание логов '''
def read_log():
    try:
        with open('bot.log', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Лог не найден."


''' корневая страница '''
@app.route('/')
def index():
    return redirect(url_for('control_panel'))


''' панель управления '''
@app.route('/control_panel')
def control_panel():
    return render_template('index.html', config=config, log=read_log())


''' запуск бота '''
@app.route('/start')
def start_bot():
    global bot_running, bot_process
    if not bot_running:
        if platform.system().startswith('W'):
            bot_process = subprocess.Popen([".\\winvenv\\Scripts\\python.exe", BOT_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        else:
            bot_process = subprocess.Popen(['./linuxvenv/bin/python', BOT_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        bot_running = True
        print("Бот запущен")
    return redirect(url_for('control_panel'))


''' остановка бота '''
@app.route('/stop')
def stop_bot():
    global bot_running, bot_process
    if bot_running and bot_process:
        bot_process.terminate()
        bot_process = None
        bot_running = False
        print("Бот остановлен")
    return redirect(url_for('control_panel'))


''' обновление конфига '''
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
    os.system('source linuxvenv/bin/activate')
    def run_bot():
        os.system(f'./linuxvenv/bin/python {BOT_SCRIPT}')
        if platform.system().startswith('W'):
            os.system(f'.\\winvenv\\Scripts\\python.exe {BOT_SCRIPT}')
        else:
            os.system(f'./linuxvenv/bin/python {BOT_SCRIPT}')

    app.run(host='0.0.0.0', port=5000)