'''

cogs/rooms.py

'''

import discord
from discord.ext import commands
import asyncio
import json
import sys

with open('config.json', 'r') as file:
    config = json.load(file)

if config["debug"] != 1:
    # Перенаправление stdout и stderr в файл
    log_file = open('bot.log', 'a', encoding='utf-8')
    sys.stdout = log_file
    sys.stderr = log_file

class Rooms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.created_channels = 0
        self.empty_channels = {} 
        self.bot.loop.create_task(self.check_empty_channels())

    async def check_empty_channels(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            guild = self.bot.get_guild(int(config["guild_id"]))
            category = discord.utils.get(guild.categories, id=int(config["create_channel_category"]))

            if not category:
                print("Категория для пользовательских каналов не найдена!")
                await asyncio.sleep(60)
                continue

            for channel in category.voice_channels:
                if len(channel.members) == 0:
                    if channel.id not in self.empty_channels:
                        self.empty_channels[channel.id] = asyncio.get_event_loop().time()
                    else:
                        if asyncio.get_event_loop().time() - self.empty_channels[channel.id] >= 300:
                            try:
                                await channel.delete()
                                print(f"Канал {channel.name} удален.")
                                del self.empty_channels[channel.id]
                                self.created_channels -= 1
                            except Exception as e:
                                print(f"Ошибка при удалении канала: {e}")
                else:
                    if channel.id in self.empty_channels:
                        del self.empty_channels[channel.id]

            await asyncio.sleep(60)

    @commands.command(name='createroom')
    async def createroom(self, ctx, limit: int, *, name: str):
        if self.created_channels >= int(config['max_create_channel']):
            embed = discord.Embed(
                title="Ошибка создания",
                description=f'Превышено максимальное количество каналов ({config["max_create_channel"]}).',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        if limit >= 100:
            embed = discord.Embed(
                title="Ошибка создания",
                description='Максимальный лимит 99.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        self.created_channels += 1
        guild = ctx.guild
        category = discord.utils.get(guild.categories, id=int(config["create_channel_category"]))

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=True),
            guild.me: discord.PermissionOverwrite(connect=True),
        }

        await guild.create_voice_channel(name=name, overwrites=overwrites, category=category, user_limit=limit)
        embed = discord.Embed(
            title="",
            description=f'Канал "{name}" создан.',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.message.reply(embed=embed)

    @commands.command(name='deleteallroom')
    @commands.has_permissions(manage_channels=True)
    async def deleteallroom(self, ctx):
        guild = ctx.guild
        category = discord.utils.get(guild.categories, id=int(config["create_channel_category"]))
        if category is None:
            embed = discord.Embed(
                title="Ошибка",
                description=f'Категория {config["create_channel_category"]} не найдена.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        deleted_channels = 0
        for channel in category.channels:
            if isinstance(channel, discord.VoiceChannel) or isinstance(channel, discord.TextChannel):
                if len(channel.members) == 0:
                    await channel.delete()
                    deleted_channels += 1
                    self.created_channels -= 1

        embed = discord.Embed(
            title="",
            description=f'Удалено {deleted_channels} каналов.',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.message.reply(embed=embed)

    @deleteallroom.error
    async def deleteallroom_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
        elif isinstance(error, commands.MissingRole):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет необходимой роли для использования этой команды.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)

    @commands.command(name='deleteroom')
    @commands.has_permissions(manage_channels=True)
    async def deleteroom(self, ctx, channel_id: int):
        guild = ctx.guild
        channel = guild.get_channel(channel_id)

        if channel is None:
            embed = discord.Embed(
                title="Ошибка",
                description='Канал с таким ID не найден.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        if not isinstance(channel, discord.VoiceChannel):
            embed = discord.Embed(
                title="Ошибка",
                description='Указанный канал не является голосовым.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        category = channel.category
        if category.id != int(config["create_channel_category"]):
            embed = discord.Embed(
                title="Ошибка",
                description='Канал не является пользовательским.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        await channel.delete()
        embed = discord.Embed(
            title="",
            description=f'Канал "{channel.name}" удален.',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.message.reply(embed=embed)

    @deleteroom.error
    async def deleteroom_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректный ID канала.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Rooms(bot))