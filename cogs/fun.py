'''

cogs/fun.py

'''

import discord
from discord.ext import commands
from discord import app_commands
import random
import aiohttp
import json
import sys
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io
import os

with open('config.json', 'r', encoding="utf-8") as file:
    config = json.load(file)

if config["debug"] != 1:
    log_file = open('bot.log', 'a', encoding='utf-8')
    sys.stdout = log_file
    sys.stderr = log_file

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='pic', description='Создает мем с текстом сверху и снизу изображения')
    @app_commands.describe(text="Текст")
    async def pic_command(self, ctx, *, text):
        if not ctx.message.attachments:
            await ctx.send("Пожалуйста, прикрепите изображение к сообщению")
            return

        attachment = ctx.message.attachments[0]
        if not attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'webp')):
            await ctx.send("Пожалуйста, прикрепите изображение в формате PNG, JPG, JPEG, GIF или WebP!")
            return

        processing_msg = await ctx.send("🔄 Обрабатываю изображение...")

        try:
            image_bytes = await attachment.read()
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            draw = ImageDraw.Draw(image)

            font = self.get_impact_font(image.height)

            top_text, bottom_text = self.split_text(text)

            if top_text:
                self.add_text_to_image(draw, font, top_text, "top", image.width, image.height)
            if bottom_text:
                self.add_text_to_image(draw, font, bottom_text, "bottom", image.width, image.height)

            output_buffer = io.BytesIO()
            image.save(output_buffer, "PNG")
            output_buffer.seek(0)

            await processing_msg.delete()
            await ctx.reply(file=discord.File(output_buffer, "meme.png"))

        except Exception as e:
            await processing_msg.delete()
            await ctx.send(f"Произошла ошибка при обработке изображения: {str(e)}")

    def get_impact_font(self, image_height):
        font_size = max(30, image_height // 10)

        font_paths = [
            "impact.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "C:/Windows/Fonts/impact.ttf",
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size=font_size)
            except:
                continue

        try:
            return ImageFont.truetype("arial.ttf", size=font_size)
        except:
            return ImageFont.load_default()

    def split_text(self, text):
        words = text.split()
        if len(words) <= 1:
            return text, ""
        
        half = len(words) // 2
        top_text = ' '.join(words[:half])
        bottom_text = ' '.join(words[half:])
        
        return top_text, bottom_text

    def add_text_to_image(self, draw, font, text, position, image_width, image_height):
        stroke_width = max(2, image_height // 200)

        max_chars_per_line = max(15, image_width // (font.size // 2))
        wrapped_text = textwrap.fill(text, width=max_chars_per_line)

        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (image_width - text_width) / 2
        
        if position == "top":
            y = image_height * 0.02
        else:
            y = image_height - text_height - image_height * 0.05

        for x_offset in range(-stroke_width, stroke_width + 1, stroke_width):
            for y_offset in range(-stroke_width, stroke_width + 1, stroke_width):
                if x_offset == 0 and y_offset == 0:
                    continue
                draw.text((x + x_offset, y + y_offset), wrapped_text, font=font, fill="black")

        draw.text((x, y), wrapped_text, font=font, fill="white")

    @commands.hybrid_command(name='meme', description='Отправляет случайный мем')
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
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Ошибка",
                        description="Не удалось получить мем.",
                        color=int(config["error_color"], 16)
                    )
                    embed.set_thumbnail(url=config["error_icon"])
                    await ctx.send(embed=embed)

    @commands.hybrid_command(name='joke', description='Отправляет случайный анекдот')
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
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Ошибка",
                        description="Не удалось получить шутку.",
                        color=int(config["error_color"], 16)
                    )
                    embed.set_thumbnail(url=config["error_icon"])
                    await ctx.send(embed=embed)

    @commands.hybrid_command(name='cat', description='Отправляет случайную картинку с котиком')
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
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Ошибка",
                        description="Не удалось получить котика.",
                        color=int(config["error_color"], 16)
                    )
                    embed.set_thumbnail(url=config["error_icon"])
                    await ctx.send(embed=embed)

    @commands.hybrid_command(name='dog', description='Отправляет случайную картинку с собакой')
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
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Ошибка",
                        description="Не удалось получить собачку.",
                        color=int(config["error_color"], 16)
                    )
                    embed.set_thumbnail(url=config["error_icon"])
                    await ctx.send(embed=embed)

    @commands.hybrid_command(name='8ball', description='Магический шар магически отвечает на вопрос')
    @app_commands.describe(question="Вопрос")
    async def eight_ball(self, ctx, *, question: str):
        responses = config["eight_ball_answers"]
        answer = random.choice(responses)
        embed = discord.Embed(
            title="🎱 Магический шар",
            description=f"**Вопрос:** {question}\n**Ответ:** {answer}",
            color=int(config["info_color"], 16)
        )
        embed.set_thumbnail(url=config["info_icon"])
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='roll', description='Бросает кости с указанным количеством сторон')
    @app_commands.describe(sides="Количество сторон(по умолчанию 6)")
    async def roll(self, ctx, sides: int = 6):
        if sides < 2:
            embed = discord.Embed(
                title="Ошибка",
                description="Количество сторон должно быть больше 1",
                color=int(config["error_color"], 16)
            )
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
            return

        result = random.randint(1, sides)
        embed = discord.Embed(
            title="🎲 Бросок кубика",
            description=f"Вы бросили кубик с {sides} сторонами и выпало **{result}**!",
            color=int(config["info_color"], 16)
        )
        embed.set_thumbnail(url=config["info_icon"])
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FunCommands(bot))