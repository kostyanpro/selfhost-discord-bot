import discord
from discord.ext import commands
import random
import aiohttp
import json
import sys

# Перенаправление stdout и stderr в файл
log_file = open('bot.log', 'a', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

with open('config.json', 'r') as file:
    config = json.load(file)

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='meme')
    async def meme(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://meme-api.com/gimme') as response:
                if response.status == 200:
                    data = await response.json()
                    meme_url = data['url']
                    embed = discord.Embed(
                        title=data['title'],
                        color=int(config["info_color"], 16)
                    )
                    embed.set_image(url=meme_url)
                    await ctx.message.reply(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Ошибка",
                        description="Не удалось получить мем.",
                        color=int(config["error_color"], 16)
                    )
                    embed.set_thumbnail(url=config["error_icon"])
                    await ctx.message.reply(embed=embed)

    @commands.command(name='joke')
    async def joke(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://v2.jokeapi.dev/joke/Any?lang=ru') as response:
                if response.status == 200:
                    data = await response.json()
                    if data['type'] == 'single':
                        joke_text = data['joke']
                    else:
                        joke_text = f"{data['setup']}\n\n{data['delivery']}"
                    embed = discord.Embed(
                        title="Шутка",
                        description=joke_text,
                        color=int(config["info_color"], 16)
                    )
                    embed.set_thumbnail(url=config["info_icon"])
                    await ctx.message.reply(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Ошибка",
                        description="Не удалось получить шутку.",
                        color=int(config["error_color"], 16)
                    )
                    embed.set_thumbnail(url=config["error_icon"])
                    await ctx.message.reply(embed=embed)

    @commands.command(name='cat')
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search') as response:
                if response.status == 200:
                    data = await response.json()
                    cat_url = data[0]['url']
                    embed = discord.Embed(
                        title="Котик!",
                        color=int(config["info_color"], 16)
                    )
                    embed.set_image(url=cat_url)
                    await ctx.message.reply(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Ошибка",
                        description="Не удалось получить котика.",
                        color=int(config["error_color"], 16)
                    )
                    embed.set_thumbnail(url=config["error_icon"])
                    await ctx.message.reply(embed=embed)

    @commands.command(name='dog')
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thedogapi.com/v1/images/search') as response:
                if response.status == 200:
                    data = await response.json()
                    dog_url = data[0]['url']
                    embed = discord.Embed(
                        title="Собачка!",
                        color=int(config["info_color"], 16)
                    )
                    embed.set_image(url=dog_url)
                    await ctx.message.reply(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Ошибка",
                        description="Не удалось получить собачку.",
                        color=int(config["error_color"], 16)
                    )
                    embed.set_thumbnail(url=config["error_icon"])
                    await ctx.message.reply(embed=embed)

    @commands.command(name='8ball')
    async def eight_ball(self, ctx, *, question: str):
        responses = [
            "Бесспорно.",
            "Предрешено.",
            "Никаких сомнений.",
            "Определённо да.",
            "Можешь быть уверен в этом.",
            "Мне кажется — «да».",
            "Вероятнее всего.",
            "Хорошие перспективы.",
            "Знаки говорят — «да».",
            "Пока не ясно, попробуй снова.",
            "Спроси позже.",
            "Лучше не рассказывать.",
            "Сейчас нельзя предсказать.",
            "Сконцентрируйся и спроси опять.",
            "Даже не думай.",
            "Мой ответ — «нет».",
            "По моим данным — «нет».",
            "Перспективы не очень хорошие.",
            "Весьма сомнительно."
        ]
        answer = random.choice(responses)
        embed = discord.Embed(
            title="🎱 Магический шар",
            description=f"**Вопрос:** {question}\n**Ответ:** {answer}",
            color=int(config["info_color"], 16)
        )
        embed.set_thumbnail(url=config["info_icon"])
        await ctx.message.reply(embed=embed)

    @commands.command(name='roll')
    async def roll(self, ctx, sides: int = 6):
        if sides < 2:
            embed = discord.Embed(
                title="Ошибка",
                description="Количество сторон должно быть больше 1.",
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        result = random.randint(1, sides)
        embed = discord.Embed(
            title="🎲 Бросок кубика",
            description=f"Вы бросили кубик с {sides} сторонами и выпало **{result}**!",
            color=int(config["info_color"], 16)
        )
        embed.set_thumbnail(url=config["info_icon"])
        await ctx.message.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(FunCommands(bot))