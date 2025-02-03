import discord
from discord.ext import commands
import random
import json
import asyncio
import sys

# Перенаправление stdout и stderr в файл
log_file = open('bot.log', 'a', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

with open('config.json', 'r') as file:
    config = json.load(file)

class UserInteractionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name='avatar')
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        avatar_url = member.avatar.url
        embed = discord.Embed(
            title=f"Аватар {member.name}",
            color=int(config["info_color"], 16)
        )
        embed.set_image(url=avatar_url)
        await ctx.message.reply(embed=embed)

    @commands.command(name='hug')
    async def hug(self, ctx, member: discord.Member):
        hug_gifs = [
            "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
            "https://media.giphy.com/media/3ZnBrkqoaI2hq/giphy.gif",
            "https://media.giphy.com/media/wnsgren9NtITS/giphy.gif",
            "https://media.giphy.com/media/IRUb7GTCaPU8E/giphy.gif",
            "https://media.giphy.com/media/PHZ7v9tfQu0o0/giphy.gif"
        ]
        hug_gif = random.choice(hug_gifs)
        embed = discord.Embed(
            title=f"{ctx.author.name} обнимает {member.name}!",
            color=int(config["info_color"], 16)
        )
        embed.set_image(url=hug_gif)
        await ctx.message.reply(embed=embed)

    @commands.command(name='poll')
    async def poll(self, ctx, *, question: str):
        parts = question.split("|")
        if len(parts) < 3:
            embed = discord.Embed(
                title="Ошибка",
                description="Укажите вопрос и хотя бы два варианта ответа через `|`.",
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        poll_question = parts[0].strip()
        options = [option.strip() for option in parts[1:]]

        poll_text = f"**{poll_question}**\n\n"
        for i, option in enumerate(options):
            poll_text += f"{i + 1}. {option}\n"

        embed = discord.Embed(
            title="Опрос",
            description=poll_text,
            color=int(config["info_color"], 16)
        )
        embed.set_thumbnail(url=config["info_icon"])
        poll_message = await ctx.message.reply(embed=embed)

        for i in range(len(options)):
            await poll_message.add_reaction(f"{i + 1}\u20e3")

        self.bot.loop.create_task(self.close_poll(poll_message, options))

    async def close_poll(self, poll_message, options):
        await asyncio.sleep(300)

        try:
            poll_message = await poll_message.channel.fetch_message(poll_message.id)
        except discord.NotFound:
            return

        results = {}
        for reaction in poll_message.reactions:
            if reaction.emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]:
                option_index = int(reaction.emoji[0]) - 1
                results[option_index] = reaction.count - 1

        poll_question = poll_message.embeds[0].description.split("\n")[0]
        result_text = f"**{poll_question}**\n\n"
        for option_index, count in results.items():
            option_text = options[option_index]
            result_text += f"{option_text}: **{count}** голосов\n"

        embed = discord.Embed(
            title="Результаты опроса",
            description=result_text,
            color=int(config["info_color"], 16)
        )
        embed.set_thumbnail(url=config["info_icon"])
        await poll_message.edit(embed=embed)

    @commands.command(name='compliment')
    async def compliment(self, ctx, member: discord.Member):
        compliments = [
            "Ты выглядишь потрясающе сегодня!",
            "Ты — источник вдохновения!",
            "Ты делаешь этот мир лучше!",
            "Ты невероятно талантлив!",
            "Ты — настоящий герой!",
            "Ты светишься, как звезда!",
            "Ты — пример для подражания!",
            "Ты заслуживаешь всего самого лучшего!",
            "Ты — уникальный человек!",
            "Ты делаешь всех вокруг счастливее!"
        ]
        compliment = random.choice(compliments)
        embed = discord.Embed(
            title=f"Комплимент для {member.name}",
            description=compliment,
            color=int(config["success_color"], 16)
        )
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.message.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInteractionCommands(bot))