'''

cogs/moderation.py

'''

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import sys

with open('config.json', 'r') as file:
    config = json.load(file)

if config["debug"] != 1:
    log_file = open('bot.log', 'a', encoding='utf-8')
    sys.stdout = log_file
    sys.stderr = log_file

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='mute', description='Мутит указанного человека')
    @app_commands.describe(member="@Пользователь", minutes = "Кол-во минут", reason = "Причина")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, minutes: int, *, reason: str = "Не указана"):
        muted_role_id = int(config["muted_role_id"])
        if not muted_role_id:
            embed = discord.Embed(
                title="Ошибка",
                description='ID роли "Muted" не указан в конфиге',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
            return

        muted_role = ctx.guild.get_role(muted_role_id)
        if not muted_role:
            embed = discord.Embed(
                title="Ошибка",
                description='Роль "Muted" не найдена на сервере',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
            return

        if muted_role in member.roles:
            embed = discord.Embed(
                title="Ошибка",
                description=f'{member.mention} уже имеет мут',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
            return

        await member.add_roles(muted_role, reason=reason)
        embed = discord.Embed(
            title="Мут выдан",
            description=f'{member.mention} получил мут на {minutes} минут.\n**Причина:** {reason}',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed)

        await asyncio.sleep(minutes * 60)
        if muted_role in member.roles:
            await member.remove_roles(muted_role, reason="Время мута истекло")
            embed = discord.Embed(
                title="Мут снят",
                description=f'Мут для {member.mention} истек',
                color=int(config["info_color"], 16)
            )
            embed.set_thumbnail(url=config["info_icon"])
            await ctx.send(embed=embed)
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='kick', description='Кикает указанного человека')
    @app_commands.describe(member="@Пользователь", reason = "Причина")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "Не указана"):
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="Пользователь кикнут",
            description=f'{member.mention} был кикнут.\n**Причина:** {reason}',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed)
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='unmute', description='Размучивает указанного человека')
    @app_commands.describe(member="@Пользователь")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role_id = int(config["muted_role_id"])
        if not muted_role_id:
            embed = discord.Embed(
                title="Ошибка",
                description='ID роли "Muted" не указан в конфиге',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
            return

        muted_role = ctx.guild.get_role(muted_role_id)
        if not muted_role:
            embed = discord.Embed(
                title="Ошибка",
                description='Роль "Muted" не найдена на сервере',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
            return

        if muted_role not in member.roles:
            embed = discord.Embed(
                title="Ошибка",
                description=f'{member.mention} не имеет мута',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
            return

        await member.remove_roles(muted_role, reason="Мут снят модератором")
        embed = discord.Embed(
            title="Мут снят",
            description=f'Мут для {member.mention} снят.',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed)
    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='ban', description='Банит указанного человека')
    @app_commands.describe(member="@Пользователь", reason = "Причина")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "Не указана"):
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="Пользователь забанен",
            description=f'{member.mention} был забанен.\n**Причина:** {reason}',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed)
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='unban', description='Разбанивает указанного человека')
    @app_commands.describe(user_id="ID пользователя")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        embed = discord.Embed(
            title="Пользователь разбанен",
            description=f'{user.mention} был разбанен',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed)
    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='warn', description='Дает предупреждение указанному человеку')
    @app_commands.describe(member="@Пользователь", reason = "Причина")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "Не указана"):
        embed = discord.Embed(
            title="Предупреждение выдано",
            description=f'{member.mention} получил предупреждение.\n**Причина:** {reason}',
            color=int(config["warn_color"], 16)
        )
        embed.set_thumbnail(url=config["warn_icon"])
        await ctx.send(embed=embed)
    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='clear', description='Чистит н-ное количество сообщений в чате')
    @app_commands.describe(amount="Количество сообщений")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            title="Сообщения удалены",
            description=f'Удалено {amount} сообщений',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed, delete_after=5)
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='lock', description='Запрещает отправку сообщений в чате')
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = discord.Embed(
            title="Канал закрыт",
            description='Этот канал теперь закрыт для отправки сообщений',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed)
    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='unlock', description='Разрешает отправку сообщений в чате')
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(
            title="Канал открыт",
            description='Этот канал теперь открыт для отправки сообщений',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed)
    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='slowmode', description='Ставит медленный режим в чате')
    @app_commands.describe(seconds="Секунд между сообщениями")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        embed = discord.Embed(
            title="Медленный режим установлен",
            description=f'Медленный режим установлен на {seconds} секунд',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed)
    @slowmode.error
    async def slowmode_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='nick', description='Меняет ник человеку')
    @app_commands.describe(member="@Пользователь", nickname="Ник")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, nickname: str):
        await member.edit(nick=nickname)
        embed = discord.Embed(
            title="Никнейм изменен",
            description=f'Никнейм {member.mention} изменен на `{nickname}`',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed)
    @nick.error
    async def nick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='role', description='Дает/отбирает указанную роль у человека')
    @app_commands.describe(member="@Пользователь", role_id="ID роли")
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member, role_id: int):
        role = ctx.guild.get_role(role_id)
        if not role:
            embed = discord.Embed(
                title="Ошибка",
                description='Роль не найдена',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
            return

        if role in member.roles:
            await member.remove_roles(role)
            action = "убрана"
        else:
            await member.add_roles(role)
            action = "выдана"

        embed = discord.Embed(
            title="Роль изменена",
            description=f'Роль {role.name} {action} для {member.mention}',
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed)
    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='mutevoice', description='Мутит войс у человека')
    @app_commands.describe(member="@Пользователь")
    @commands.has_permissions(mute_members=True)
    async def mutevoice(self, ctx, member: discord.Member):
        if member.voice:
            await member.edit(mute=True)
            embed = discord.Embed(
                title="Пользователь заглушен",
                description=f'{member.mention} заглушен в голосовом канале.',
                color=int(config["success_color"], 16)
            )
            embed.set_thumbnail(url=config["success_icon"])
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка",
                description=f'{member.mention} не в голосовом канале.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
    @mutevoice.error
    async def mutevoice_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы.',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='unmutevoice', description='Размутит войс у человека')
    @app_commands.describe(member="@Пользователь")
    @commands.has_permissions(mute_members=True)
    async def unmutevoice(self, ctx, member: discord.Member):
        if member.voice:
            await member.edit(mute=False)
            embed = discord.Embed(
                title="Пользователь разглушен",
                description=f'{member.mention} разглушен в голосовом канале',
                color=int(config["success_color"], 16)
            )
            embed.set_thumbnail(url=config["success_icon"])
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка",
                description=f'{member.mention} не в голосовом канале',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
    @unmutevoice.error
    async def unmutevoice_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='move', description='Перемещает человека в войс')
    @app_commands.describe(member="@Пользователь", channel_id="ID войса")
    @commands.has_permissions(move_members=True)
    async def move(self, ctx, member: discord.Member, channel_id: int):
        channel = ctx.guild.get_channel(channel_id)
        if not channel or not isinstance(channel, discord.VoiceChannel):
            embed = discord.Embed(
                title="Ошибка",
                description='Голосовой канал не найден',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
            return

        if member.voice:
            await member.move_to(channel)
            embed = discord.Embed(
                title="Пользователь перемещен",
                description=f'{member.mention} перемещен в {channel.name}',
                color=int(config["success_color"], 16)
            )
            embed.set_thumbnail(url=config["success_icon"])
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка",
                description=f'{member.mention} не в голосовом канале',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
    @move.error
    async def move_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Ошибка",
                description='У вас нет прав для использования этой команды',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Ошибка",
                description='Пожалуйста, укажите корректные аргументы',
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))