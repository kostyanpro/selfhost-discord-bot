import discord
from discord.ext import commands
import yt_dlp
import asyncio
import json
import sys

# Перенаправление stdout и stderr в файл
log_file = open('bot.log', 'a', encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

with open('config.json', 'r') as file:
    config = json.load(file)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.current_song = None
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            'options': '-vn'
        }

    @commands.command(name='play')
    async def play(self, ctx, *, query):
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(title="Ошибка", description='Вы не в голосовом чате.', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)
            return

        voice_channel = ctx.author.voice.channel
        voice_client = ctx.voice_client

        if voice_client is None:
            try:
                voice_client = await voice_channel.connect()
            except Exception as e:
                embed = discord.Embed(title="Ошибка", description=f'Не удалось подключиться к каналу: {e}', color=int(config["error_color"], 16))
                embed.set_thumbnail(url=config["error_icon"])
                await ctx.message.reply(embed=embed)
                return
        else:
            if voice_client.channel != voice_channel:
                embed = discord.Embed(title="Ошибка", description='Бот подключен к другому каналу.', color=int(config["error_color"], 16))
                embed.set_thumbnail(url=config["error_icon"])
                await ctx.message.reply(embed=embed)
                return

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch1',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
                url = info['url']
                title = info['title']
                duration = info.get('duration', 0)
                formatted_duration = f"{duration // 60}:{duration % 60:02}"
            except Exception as e:
                embed = discord.Embed(title="Ошибка", description=f'Не удалось получить информацию о треке: {e}', color=int(config["error_color"], 16))
                embed.set_thumbnail(url=config["error_icon"])
                await ctx.message.reply(embed=embed)
                return

        self.queue.append({
            'url': url,
            'title': title,
            'duration': formatted_duration,
            'ctx': ctx
        })

        if not voice_client.is_playing():
            await self.play_next(ctx)
        if len(self.queue) != 0:
            embed = discord.Embed(title="Добавлено в очередь", description=f'[{title}]({url})\n**Длительность:** `{formatted_duration}`', color=int(config["info_color"], 16))
            embed.set_thumbnail(url=config["info_icon"])
            await ctx.message.reply(embed=embed)

    @commands.command(name='skip')
    async def skip(self, ctx):
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            embed = discord.Embed(title="Трек пропущен", color=int(config["success_color"],16))
            embed.set_thumbnail(url=config["success_icon"])
            await ctx.message.reply(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка", description='Сейчас ничего не играет.', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)

    @commands.command(name='stop')
    async def stop(self, ctx):
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            self.queue.clear()
            embed = discord.Embed(title="Воспроизведение остановлено", color=int(config["success_color"],16))
            embed.set_thumbnail(url=config["success_icon"])
            await ctx.message.reply(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка", description='Сейчас ничего не играет.', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)

    @commands.command(name='queue')
    async def show_queue(self, ctx):
        if not self.queue:
            embed = discord.Embed(title="Очередь пуста", color=int(config["info_color"], 16))
            embed.set_thumbnail(url=config["info_icon"])
            await ctx.message.reply(embed=embed)
            return

        queue_list = "\n".join([f"{i+1}. {item['title']} ({item['duration']})" for i, item in enumerate(self.queue)])
        embed = discord.Embed(title="Очередь воспроизведения", description=queue_list, color=int(config["info_color"], 16))
        embed.set_thumbnail(url=config["info_icon"])
        await ctx.message.reply(embed=embed)

    async def play_next(self, ctx):
        if not self.queue:
            return

        voice_client = ctx.voice_client
        if not voice_client:
            return

        next_song = self.queue.pop(0)
        source = discord.FFmpegPCMAudio(next_song['url'], executable=config["ffmpeg_path"], **self.FFMPEG_OPTIONS)

        def after_playing(error):
            if error:
                print(f'Ошибка воспроизведения: {error}')
            asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)

        voice_client.play(source, after=after_playing)
        embed = discord.Embed(title="Сейчас играет", description=f'[{next_song["title"]}]({next_song["url"]})\n**Длительность:** `{next_song["duration"]}`', color=int(config["info_color"], 16))
        embed.set_thumbnail(url=config["info_icon"])
        await ctx.message.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))