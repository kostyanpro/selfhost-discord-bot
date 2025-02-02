import discord
import random
import json
import asyncio
from discord.ext import commands
import sys

# Перенаправление stdout и stderr в файл
log_file = open('bot.log', 'a', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

with open('config.json', 'r') as file:
    config = json.load(file)

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(title="Понг!", description=f"Задержка: `{latency} мс`", color=int(config["info_color"], 16))
        embed.set_thumbnail(url=config["info_icon"])
        await ctx.message.reply(embed=embed)

    @commands.command(name='roll')
    async def roll(self, ctx, limit='100'):
        if limit.isdigit():
            if int(limit) > 1000000000:
                embed = discord.Embed(title="Ошибка", description='Слишком большое число.', color=int(config["error_color"], 16))
                embed.set_thumbnail(url=config["error_icon"])
                await ctx.message.reply(embed=embed)
                return
            embed = discord.Embed(title=f"Случайное число (0-{limit}):", description=f'**{random.randint(0, int(limit))}**', color=int(config["success_color"],16))
            embed.set_thumbnail(url=config["success_icon"])
            await ctx.message.reply(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка", description='Некорректное число.', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)

    @commands.command(name='help')
    async def help(self, ctx):
        embed = discord.Embed(title="Список команд", color=int(config["info_color"], 16))
        embed.set_thumbnail(url=config["info_icon"])
        embed.add_field(name="!ping", value="Проверка задержки бота", inline=False)
        embed.add_field(name="!roll [лимит]", value="Случайное число от 0 до указанного числа", inline=False)
        embed.add_field(name="!play [ссылка на YT/запрос]", value="Включает музыку с указанного видео, либо с запроса", inline=False)
        embed.add_field(name="!skip", value="Пропуск текущего трека", inline=False)
        embed.add_field(name="!stop", value="Остановка воспроизведения", inline=False)
        embed.add_field(name="!queue", value="Показывает текущую очередь", inline=False)
        embed.add_field(name="!voice [текст]", value="Озвучка текста", inline=False)
        embed.add_field(name="!createroom [лимит] [название]", value="Создает новый голосовой канал с заданным названием и лимитом по пользователям. Канал будет удален через 5 минут отсутствия людей.", inline=False)
        embed.add_field(name="!repinfo [@пользователь]", value="Информация о репутации", inline=False)
        embed.add_field(name="!reptop", value="Топ 10 пользователей по репутации", inline=False)
        embed.add_field(name="!info [@Пользователь]", value="Выводит информацию о пользователе", inline=False)
        embed.add_field(name="!serverinfo", value="Выводит информацию о сервере", inline=False)
        embed.add_field(name="!help+", value="Список команд с повышенными правами", inline=False)
        message = await ctx.message.reply(embed=embed)
        await asyncio.sleep(180)
        await message.delete()

    @commands.command(name='help+')
    async def helpp(self, ctx):
        embed = discord.Embed(title="Список команд с повышенными правами", color=int(config["info_color"], 16))
        embed.set_thumbnail(url=config["info_icon"])
        embed.add_field(name="!mute [@Пользователь] [Кол-во минут] [Причина]", value="Запрещает пользователю отправлять сообщения", inline=False)
        embed.add_field(name="!unmute [@Пользователь]", value="Разрешает пользователю отправлять сообщения", inline=False)
        embed.add_field(name="!mutevoice [@Пользователь]", value="Запрещает пользователю разговаривать в голосовых каналах", inline=False)
        embed.add_field(name="!unmutevoice [@Пользователь]", value="Разрешает пользователю разговаривать в голосовых каналах", inline=False)
        embed.add_field(name="!ban [@Пользователь] [Причина]", value="Банит пользователя", inline=False)
        embed.add_field(name="!unban [ID пользователь]", value="Разбанит пользователя", inline=False)
        embed.add_field(name="!kick [@Пользователь] [Причина]", value="Выгоняет пользователя", inline=False)
        embed.add_field(name="!warn [@Пользователь] [Причина]", value="Дает предупреждение пользователю", inline=False)
        embed.add_field(name="!clear [Кол-во сообщений]", value="Очищает последние сообщения в указанном количестве", inline=False)
        embed.add_field(name="!lock", value="Закрывает текстовый чат для сообщений пользователей", inline=False)
        embed.add_field(name="!slowmode [Кол-во секунд]", value="Добавляют задержку между сообщениями пользователей", inline=False)
        embed.add_field(name="!nick [@Пользователь] [Ник]", value="Изменяет ник указанного пользователя", inline=False)
        embed.add_field(name="!role [@Пользователь] [ID роли]", value="Добавляет/Удаляет роль у указанного пользователя", inline=False)
        embed.add_field(name="!move [@Пользователь] [ID канала]", value="Перемещает пользователя в указанный голосовой канал", inline=False)
        embed.add_field(name="!deleteallroom", value="Очистка всех созданных голосовых каналов", inline=False)
        embed.add_field(name="!deleteroom [ID канала]", value="Удаление пользовательского голосового канала", inline=False)
        embed.add_field(name="!resetdbrep", value="Сброс базы данных репутации", inline=False)
        message = await ctx.message.reply(embed=embed)
        await asyncio.sleep(180)
        await message.delete()
        
    @commands.command(name='info')
    async def info(self, ctx, member: discord.Member):
        embed = discord.Embed(
            title=f"Информация о {member.name}",
            color=int(config["info_color"], 16)
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Статус", value=member.status, inline=False)
        embed.add_field(name="Присоединился", value=member.joined_at.strftime("%d.%m.%Y %H:%M:%S"), inline=False)
        embed.add_field(name="Роли", value=", ".join([role.name for role in member.roles if role.name != "@everyone"]), inline=False)
        await ctx.message.reply(embed=embed)

    @commands.command(name='serverinfo')
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(
            title=f"Информация о сервере {guild.name}",
            color=int(config["info_color"], 16)
        )
        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Владелец", value=guild.owner.mention, inline=False)
        embed.add_field(name="Участники", value=guild.member_count, inline=False)
        embed.add_field(name="Каналы", value=f"Текстовые: {len(guild.text_channels)}\nГолосовые: {len(guild.voice_channels)}", inline=False)
        embed.add_field(name="Создан", value=guild.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=False)
        await ctx.message.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))