'''

cogs/event.py

async def on_ready()
async def on_member_join()
async def on_message()

'''

import discord
from discord.ext import commands
import sqlite3
import json
import sys

with open('config.json', 'r') as file:
    config = json.load(file)

if config["debug"] != 1:
    # Перенаправление stdout и stderr в файл
    log_file = open('bot.log', 'a', encoding='utf-8')
    sys.stdout = log_file
    sys.stderr = log_file

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('reputation.db')
        self.cursor = self.conn.cursor()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Бот {self.bot.user.name} готов к работе!')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = member.guild.get_role(int(config["role_id"]))
        if role:
            try:
                await member.add_roles(role)
                print(f'Роль {role.name} выдана участнику {member.name}')
            except Exception as e:
                print(f'Ошибка при выдаче роли: {e}')

    @commands.Cog.listener()
    async def on_message(self, message):
        
        if message.author.bot:
            return

        user_id = message.author.id

        self.cursor.execute('SELECT message_count FROM message_counts WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()

        if result:
            message_count = result[0] + 1
            self.cursor.execute('UPDATE message_counts SET message_count = ? WHERE user_id = ?', (message_count, user_id))
        else:
            message_count = 1
            self.cursor.execute('INSERT INTO message_counts (user_id, message_count) VALUES (?, ?)', (user_id, message_count))

        if message_count >= int(config["count_message_for_rep"]):
            self.cursor.execute('SELECT reputation FROM reputation WHERE user_id = ?', (user_id,))
            rep_result = self.cursor.fetchone()

            if rep_result:
                new_rep = rep_result[0] + 1
                self.cursor.execute('UPDATE reputation SET reputation = ? WHERE user_id = ?', (new_rep, user_id))
            else:
                new_rep = int(config["start_rep"]) + 1
                self.cursor.execute('INSERT INTO reputation (user_id, reputation) VALUES (?, ?)', (user_id, new_rep))

            self.cursor.execute('UPDATE message_counts SET message_count = 0 WHERE user_id = ?', (user_id,))

        self.conn.commit()

async def setup(bot):
    await bot.add_cog(Events(bot))