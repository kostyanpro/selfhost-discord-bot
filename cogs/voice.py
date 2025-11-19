'''

cogs/voice.py

'''

import discord
from discord.ext import commands
from gtts import gTTS
import os
import json
import sys

with open('config.json', 'r') as file:
    config = json.load(file)

if config["debug"] != 1:
    # Перенаправление stdout и stderr в файл
    log_file = open('bot.log', 'a', encoding='utf-8')
    sys.stdout = log_file
    sys.stderr = log_file

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.FFMPEG_OPTIONS_MP3 = {
            'options': '-vn'
        }

    @commands.command(name='voice')
    async def voice(self, ctx, *, text: str):
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(title="Ошибка", description='Вы не в голосовом канале!', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        if len(text) > 500:
            embed = discord.Embed(title="Ошибка", description='Слишком много символов.', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        try:
            tts = gTTS(text=text, lang='ru')
            tts.save('output.mp3')
        except Exception as e:
            embed = discord.Embed(title="Ошибка", description=f'Ошибка при создании аудиофайла: {e}', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        voice_client = ctx.voice_client
        if not voice_client:
            try:
                voice_client = await ctx.author.voice.channel.connect()
            except Exception as e:
                embed = discord.Embed(title="Ошибка", description=f'Не удалось подключиться к каналу: {e}', color=int(config["error_color"], 16))
                embed.set_thumbnail(url=config["error_icon"])
                await ctx.message.reply(embed=embed)
                return

        #voice_client.play(discord.FFmpegPCMAudio(source='output.mp3', executable=config["ffmpeg_path"]), )
        embed = discord.Embed(title="Озвучка текста", description=text, color=int(config["info_color"], 16))
        embed.set_thumbnail(url=config["info_icon"])
        await ctx.message.reply(embed=embed)

        def after_playing(error):
            if error:
                print(f'Ошибка воспроизведения: {error}')
            os.remove('output.mp3')

        voice_client.play(discord.FFmpegPCMAudio(source='output.mp3', executable=config["ffmpeg_path"], **self.FFMPEG_OPTIONS_MP3), after=after_playing)

async def setup(bot):
    await bot.add_cog(Voice(bot))