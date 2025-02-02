import sqlite3
import sys

# Перенаправление stdout и stderr в файл
log_file = open('bot.log', 'a', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

async def initialize_database():
    # Подключение к базе данных SQLite
    conn = sqlite3.connect('reputation.db')
    cursor = conn.cursor()

    # Создание таблицы для репутации
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reputation (
            user_id INTEGER PRIMARY KEY,
            reputation INTEGER DEFAULT 100
        )
    ''')

    # Создание таблицы для истории изменений репутации
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rep_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            target_id INTEGER,
            change INTEGER,
            timestamp INTEGER,
            FOREIGN KEY (user_id) REFERENCES reputation(user_id),
            FOREIGN KEY (target_id) REFERENCES reputation(user_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_counts (
            user_id INTEGER PRIMARY KEY,
            message_count INTEGER DEFAULT 0
        )
    ''')

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()
    print('инициализация прошла успешно!')
