import discord
import os
import sqlite3
import json
from discord.ext import commands
import sys

# Перенаправление stdout и stderr в файл
log_file = open('bot.log', 'a', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

with open('config.json', 'r') as file:
    config = json.load(file)

class Reputation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('reputation.db')
        self.cursor = self.conn.cursor()

    @commands.command(name='repinfo')
    async def repinfo(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author

        self.cursor.execute('SELECT reputation FROM reputation WHERE user_id = ?', (user.id,))
        result = self.cursor.fetchone()
        if result:
            reputation = result[0]
            embed = discord.Embed(title=f"Репутация пользователя {user.name}", description=f"Репутация: {reputation}", color=int(config["info_color"], 16))
            embed.set_thumbnail(url=config["info_icon"])
            await ctx.message.reply(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка", description=f"{user.mention} еще не начисляли репутацию.", color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)

    @commands.command(name='reptop')
    async def reptop(self, ctx):
        self.cursor.execute('SELECT user_id, reputation FROM reputation ORDER BY reputation DESC LIMIT 10')
        top_users = self.cursor.fetchall()

        if not top_users:
            embed = discord.Embed(title="Ошибка", description="Топ пользователей по репутации пуст.", color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        embed = discord.Embed(title="Топ 10 пользователей по репутации", color=int(config["success_color"],16))
        embed.set_thumbnail(url=config["success_icon"])
        for idx, user in enumerate(top_users, start=1):
            user_obj = self.bot.get_user(user[0])
            if user_obj:
                username = user_obj.name
            else:
                username = f"User ID {user[0]}"
            embed.add_field(name=f"{idx}. {username}", value=f"Репутация: {user[1]}", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='resetdbrep')
    @commands.has_permissions(administrator=True)
    async def resetdbrep(self, ctx):
        try:
            self.cursor.execute('DELETE FROM reputation')
            self.conn.commit()
            print("Все записи из таблицы reputation удалены.")

            self.cursor.execute('DELETE FROM message_counts')
            self.conn.commit()
            print("Все записи из таблицы message_counts удалены.")

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS reputation (
                    user_id INTEGER PRIMARY KEY,
                    reputation INTEGER DEFAULT 0
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS message_counts (
                    user_id INTEGER PRIMARY KEY,
                    message_count INTEGER DEFAULT 0
                )
            ''')
            self.conn.commit()
            print("Таблицы reputation и message_counts созданы заново.")

            embed = discord.Embed(title="База данных репутации сброшена", color=int(config["success_color"], 16))
            embed.set_thumbnail(url=config["success_icon"])
            await ctx.message.reply(embed=embed)
        except Exception as e:
            print(f"Ошибка при сбросе базы данных: {e}")
            embed = discord.Embed(title="Ошибка", description="Не удалось сбросить базу данных.", color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
    @resetdbrep.error
    async def resetdbrep_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Reputation(bot))