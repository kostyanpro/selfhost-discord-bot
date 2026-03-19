'''

cogs/music.py

'''

import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import json
import sys

with open('config.json', 'r') as file:
    config = json.load(file)

UNLOADED_TITLE = "⏳ Загрузка данных..."

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.current_song = None
        self.last_message = None
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
            'options': '-vn',
        }
        
        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': False,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'cookiefile': 'cookie.txt',
            'nocheckcertificate': True,
            'ignoreerrors': True,
        }

    async def fetch_track_data(self, index):
        if index >= len(self.queue):
            return
            
        song = self.queue[index]
        if song['title'] != UNLOADED_TITLE:
            return

        loop = asyncio.get_event_loop()
        def extract():
            with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                return ydl.extract_info(song['webpage_url'], download=False)

        try:
            info = await loop.run_in_executor(None, extract)
            if info:
                raw_duration = int(info.get('duration') or 0)
                minutes, seconds = divmod(raw_duration, 60)
                
                self.queue[index].update({
                    'title': info.get('title', 'Неизвестный трек'),
                    'uploader': info.get('uploader') or info.get('artist') or "Исполнитель не найден",
                    'duration': f"{minutes}:{seconds:02}",
                    'thumbnail': info.get('thumbnail'),
                    'url': info.get('url')
                })
        except Exception as e:
            print(f"Ошибка подгрузки трека {index}: {e}")

    async def extract_minimize_info(self, query: str):
        loop = asyncio.get_event_loop()
        ydl_opts = self.YDL_OPTIONS.copy()
        ydl_opts['extract_flat'] = 'in_playlist'

        def extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(query if query.startswith('http') else f"ytsearch:{query}", download=False)
        
        try:
            return await loop.run_in_executor(None, extract)
        except Exception as e:
            print(f"Ошибка быстрого извлечения: {e}")
            return None

    @commands.hybrid_command(name='play', description='Добавляет музыку в очередь')
    @app_commands.describe(query="Ссылка/Запрос")
    async def play(self, ctx, *, query):
        if not ctx.author.voice:
            return await ctx.send("Вы не в голосовом канале!")

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        
        embed = discord.Embed(title="🔍 Обработка запроса...", color=int(config["info_color"], 16))
        msg = await ctx.send(embed=embed)

        data = await self.extract_minimize_info(query)
        if not data:
            return await msg.edit(content="Ничего не найдено.")

        added_count = 0
        # Обработка плейлиста или одиночного видео
        entries = data.get('entries', [data])
        
        for entry in entries:
            if not entry: continue
            
            url = entry.get('url') or entry.get('webpage_url')
            if not url and data.get('webpage_url'):
                url = data.get('webpage_url')

            self.queue.append({
                'webpage_url': url,
                'title': UNLOADED_TITLE,
                'uploader': "...",
                'duration': "??:??",
                'thumbnail': None,
                'url': None
            })
            added_count += 1

        desc = f"Добавлено треков: **{added_count}**"
        await msg.edit(embed=discord.Embed(title="Очередь обновлена", description=desc, color=int(config["info_color"], 16)))

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    @commands.hybrid_command(name='queue', description='Показывает очередь')
    async def show_queue(self, ctx):
        if not self.queue:
            return await ctx.send("Очередь пуста.")

        wait_embed = discord.Embed(title="⏳ Подгружаем информацию об очереди...", color=int(config["info_color"], 16))
        msg = await ctx.send(embed=wait_embed)

        tasks = [self.fetch_track_data(i) for i in range(min(10, len(self.queue)))]
        await asyncio.gather(*tasks)

        queue_list = ""
        for i, item in enumerate(self.queue[:10]):
            queue_list += f"{i+1}. **{item['title']}** — {item['uploader']} ({item['duration']})\n"

        final_embed = discord.Embed(title="Очередь воспроизведения", description=queue_list, color=int(config["info_color"], 16))
        if len(self.queue) > 10:
            final_embed.set_footer(text=f"И еще {len(self.queue) - 10} треков...")
        
        await msg.edit(embed=final_embed)

    @commands.hybrid_command(name='skip', description='Пропускает один или несколько треков')
    @app_commands.describe(count="Количество треков для пропуска (по умолчанию 1)")
    async def skip(self, ctx, count: int = 1):
        voice_client = ctx.voice_client
        
        if not voice_client or not voice_client.is_playing():
            embed = discord.Embed(title="Ошибка", description='Сейчас ничего не играет', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)
            return

        if count < 1:
            await ctx.send("Количество пропускаемых треков должно быть больше 0")
            return

        if count > 1:
            to_skip_from_queue = count - 1

            for _ in range(min(to_skip_from_queue, len(self.queue))):
                self.queue.pop(0)
            
            description = f"Пропущено треков: **{count}**"
        else:
            description = "Текущий трек пропущен"

        voice_client.stop()
        
        embed = discord.Embed(title="Трек пропущен", description=description, color=int(config["success_color"], 16))
        embed.set_thumbnail(url=config["success_icon"])
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='stop', description='Останавливает воспроизведение')
    async def stop(self, ctx):
        voice_client = ctx.voice_client
        if voice_client:
            if voice_client.is_playing():
                voice_client.stop()
            self.queue.clear()
            embed = discord.Embed(title="Воспроизведение остановлено", color=int(config["success_color"],16))
            embed.set_thumbnail(url=config["success_icon"])
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка", description='Бот не подключен к голосовому каналу.', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.send(embed=embed)

    async def play_next(self, ctx, error=None):
        voice_client = ctx.voice_client
        if not voice_client or not self.queue:
            return

        if self.queue[0]['title'] == UNLOADED_TITLE:
            await self.fetch_track_data(0)

        song_data = self.queue.pop(0)

        if not song_data.get('url'):
            await self.play_next(ctx)
            return

        try:
            source = discord.FFmpegOpusAudio(
                song_data['url'],
                executable=config.get("ffmpeg_path"),
                **self.FFMPEG_OPTIONS
            )

            def after_playing(err):
                asyncio.run_coroutine_threadsafe(self.play_next(ctx, err), self.bot.loop)

            voice_client.play(source, after=after_playing)

            embed = discord.Embed(
                title=song_data['title'],
                description=song_data['uploader'],
                color=int(config["info_color"], 16),
                url=song_data["webpage_url"]
            )
            if song_data['thumbnail']:
                embed.set_thumbnail(url=song_data['thumbnail'])
            embed.set_author(name="Сейчас играет")
            embed.set_footer(text=f"Длительность: {song_data['duration']}")

            if self.last_message:
                try: await self.last_message.delete()
                except: pass
            self.last_message = await ctx.send(embed=embed)

        except Exception as e:
            print(f"Ошибка запуска: {e}")
            await self.play_next(ctx)

async def setup(bot):
    await bot.add_cog(Music(bot))