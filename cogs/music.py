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

if config["debug"] != 1:
    log_file = open('bot.log', 'a', encoding='utf-8')
    sys.stdout = log_file
    sys.stderr = log_file

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.current_song = None
        self.last_message = None
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
        }
        
        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': False,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'cookiefile': 'cookie.txt', 
            'nocheckcertificate': True,
            'yandexmusic': {
                'format': 'm4a/bestaudio/best'
            },
        }
        
    async def extract_info(self, query: str):
        loop = asyncio.get_event_loop()
        
        def extract():
            if config['debug'] == 1:
                debug_opts = self.YDL_OPTIONS.copy()
                debug_opts['listformats'] = True 
                
                with yt_dlp.YoutubeDL(debug_opts) as ydl:
                    try:
                        ydl.extract_info(query if query.startswith('http') else f"ytsearch:{query}", download=False)
                    except Exception as e:
                        print(f"Ошибка при просмотре форматов: {e}")

            with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(query if query.startswith('http') else f"ytsearch:{query}", download=False)
                if 'entries' in info:
                    return list(info['entries'])
                return [info]
        
        try:
            return await loop.run_in_executor(None, extract)
        except Exception as e:
            print(f"Ошибка извлечения: {e}")
            return None

    @commands.hybrid_command(name='play', description='Включает музыку с указанного видео или по запросу')
    @app_commands.describe(query="Ссылка/запрос")
    async def play(self, ctx, *, query):
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(title="Ошибка", description='Вы не в голосовом чате.', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.ctx.send(embed=embed)
            return

        voice_channel = ctx.author.voice.channel
        voice_client = ctx.voice_client

        if voice_client is None:
            try:
                voice_client = await voice_channel.connect()
            except Exception as e:
                embed = discord.Embed(title="Ошибка", description=f'Не удалось подключиться к каналу: {e}', color=int(config["error_color"], 16))
                embed.set_thumbnail(url=config["error_icon"])
                await ctx.send(embed=embed)
                return
        else:
            if voice_client.channel != voice_channel:
                embed = discord.Embed(title="Ошибка", description='Бот подключен к другому каналу.', color=int(config["error_color"], 16))
                embed.set_thumbnail(url=config["error_icon"])
                await ctx.send(embed=embed)
                return

        embed = discord.Embed(title="🔍 Поиск трека...", color=int(config["info_color"], 16))
        search_msg = await ctx.send(embed=embed)

        try:
            entries = await self.extract_info(query)

            if not entries:
                error_embed = discord.Embed(
                    title="Ошибка", 
                    description="Ничего не найдено.", 
                    color=int(config["error_color"], 16)
                )
                await search_msg.edit(embed=error_embed)
                return

            added_count = 0
            for entry in entries:
                url = entry.get('url') or entry.get('webpage_url')
                raw_duration = int(entry.get('duration') or 0)
                minutes, seconds = divmod(raw_duration, 60)
                formatted_duration = f"{minutes}:{seconds:02}"
                uploader = entry.get('uploader') or entry.get('artist') or "Яндекс.Музыка"
                song_data = {
                    'url': entry.get('url') or entry.get('webpage_url'),
                    'title': entry.get('title') or "Неизвестный трек",
                    'duration': formatted_duration,
                    'webpage_url': entry.get('webpage_url'),
                    'uploader': uploader,
                    'ctx': ctx
                }
                self.queue.append(song_data)
                added_count += 1

            if added_count > 1:
                desc = f"Добавлено **{added_count}** треков из плейлиста."
            else:
                desc = f"Добавлено: **{self.queue[-1]['title']}**"

            success_embed = discord.Embed(
                title="Очередь обновлена", 
                description=desc, 
                color=int(config["info_color"], 16)
            )
            await search_msg.edit(embed=success_embed)

            if not ctx.voice_client.is_playing():
                await self.play_next(ctx)

        except Exception as e:
            await search_msg.edit(content=f"Произошла ошибка: {e}", embed=None)

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

    @commands.hybrid_command(name='queue', description='Показывает очередь воспроизведения')
    async def show_queue(self, ctx):
        if not self.queue:
            embed = discord.Embed(title="Очередь пуста", color=int(config["info_color"], 16))
            embed.set_thumbnail(url=config["info_icon"])
            await ctx.send(embed=embed)
            return

        upcoming = self.queue[:10]
        
        queue_list = ""
        for i, item in enumerate(upcoming):
            queue_list += f"{i+1}. **{item['title']}** - {item['uploader']} ({item['duration']})\n"

        embed = discord.Embed(
            title="Очередь воспроизведения", 
            description=queue_list, 
            color=int(config["info_color"], 16)
        )

        if len(self.queue) > 10:
            embed.set_footer(text=f"И еще {len(self.queue) - 10} треков в очереди...")
            
        embed.set_thumbnail(url=config["info_icon"])
        await ctx.send(embed=embed)

    async def play_next(self, ctx, error=None):
        if error:
            print(f'Ошибка воспроизведения: {error}')

        voice_client = ctx.voice_client
        if not voice_client or not self.queue:
            if self.last_message:
                try:
                    await self.last_message.delete()
                    self.last_message = None
                except:
                    pass
            return

        if self.last_message:
            try:
                await self.last_message.delete()
            except Exception as e:
                print(f"Не удалось удалить старое сообщение: {e}")

        song_data = self.queue.pop(0)
        
        try:
            info = await self.extract_info(song_data['webpage_url'])
            if isinstance(info, list):
                info = info[0]
                
            stream_url = info.get('url')
            source = discord.FFmpegOpusAudio(
                stream_url, 
                executable=config["ffmpeg_path"], 
                **self.FFMPEG_OPTIONS
            )

            def after_playing(err):
                if err:
                    print(f'Ошибка после завершения: {err}')
                asyncio.run_coroutine_threadsafe(self.play_next(ctx, err), self.bot.loop)

            voice_client.play(source, after=after_playing)

            thumbnail = info.get('thumbnail')
            uploader = info.get('uploader') or info.get('artist') or "Неизвестный исполнитель"
            
            raw_duration = int(info.get('duration') or 0)
            minutes, seconds = divmod(raw_duration, 60)
            duration_str = f"{minutes}:{seconds:02}"

            embed = discord.Embed(
                title=info.get("title"),
                description=uploader,
                color=int(config["info_color"], 16),
                url=song_data["webpage_url"]
            )
            if thumbnail:
                embed.set_thumbnail(url=thumbnail)
            
            embed.set_author(name="Сейчас играет")
            embed.set_footer(text=f"Длительность: {duration_str}")

            self.last_message = await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Критическая ошибка: {e}")
            await asyncio.sleep(1)
            await self.play_next(ctx)

async def setup(bot):
    await bot.add_cog(Music(bot))