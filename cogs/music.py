'''

cogs/music.py

'''

import discord
from discord.ext import commands
import yt_dlp
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

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.current_song = None
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
        }
        
        # Настройки yt-dlp для поддержки ВК и Яндекс.Музыки
        self.YDL_OPTIONS = {
            'no_check_certificate': True,
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            # Для ВКонтакте
            'extractor_args': {
                'vkontakte': ['--no-playlist']
            },
            # Для Яндекс.Музыки
            'yandexmusic': {
                'format': 'bestaudio/best'
            },
            # Общие настройки
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }

    async def extract_info(self, query: str):
        """Асинхронное извлечение информации о треке"""
        loop = asyncio.get_event_loop()
        
        def extract():
            with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                # Определяем, является ли запрос URL или поисковым запросом
                if query.startswith(('http', 'https')):
                    # Прямой URL
                    info = ydl.extract_info(query, download=False)
                else:
                    # Поисковый запрос
                    info = ydl.extract_info(f"ytsearch:{query}", download=False)
                
                # Обрабатываем плейлисты или множественные результаты
                if 'entries' in info:
                    info = info['entries'][0]
                
                return info
        
        try:
            return await loop.run_in_executor(None, extract)
        except Exception as e:
            print(f"Ошибка при извлечении информации: {e}")
            return None

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

        # Показываем сообщение о поиске
        embed = discord.Embed(title="🔍 Поиск трека...", color=int(config["info_color"], 16))
        search_msg = await ctx.message.reply(embed=embed)

        try:
            # Извлекаем информацию о треке
            info = await self.extract_info(query)
            
            if not info:
                embed = discord.Embed(title="Ошибка", description='Не удалось найти трек.', color=int(config["error_color"], 16))
                embed.set_thumbnail(url=config["error_icon"])
                await search_msg.edit(embed=embed)
                return

            # Получаем URL аудиопотока
            url = info.get('url')
            if not url:
                # Если прямого URL нет, ищем среди форматов
                formats = info.get('formats', [])
                audio_formats = [f for f in formats if f.get('acodec') != 'none']
                if audio_formats:
                    url = audio_formats[0].get('url')
            
            if not url:
                embed = discord.Embed(title="Ошибка", description='Не удалось получить аудиопоток.', color=int(config["error_color"], 16))
                embed.set_thumbnail(url=config["error_icon"])
                await search_msg.edit(embed=embed)
                return

            title = info.get('title', 'Неизвестный трек')
            duration = info.get('duration', 0)
            formatted_duration = f"{duration // 60}:{duration % 60:02}" if duration else "Неизвестно"
            webpage_url = info.get('webpage_url', '')
            uploader = info.get('uploader', 'Неизвестный исполнитель')

            # Добавляем в очередь
            song_data = {
                'url': url,
                'title': title,
                'duration': formatted_duration,
                'webpage_url': webpage_url,
                'uploader': uploader,
                'ctx': ctx
            }
            
            self.queue.append(song_data)

            # Удаляем сообщение о поиске
            await search_msg.delete()

            # Отправляем сообщение о добавлении в очередь
            if len(self.queue) > 1 or voice_client.is_playing():
                embed = discord.Embed(
                    title="Трек добавлен!\n", 
                    description=f'**[{title}]({url})**\n\n**Исполнитель:** {uploader}\n\n**Длительность:** `{formatted_duration}`',
                    color=int(config["info_color"], 16)
                )
                embed.set_thumbnail(url=config["info_icon"])
                await ctx.message.reply(embed=embed)

            # Если ничего не играет, начинаем воспроизведение
            if not voice_client.is_playing():
                await self.play_next(ctx)

        except Exception as e:
            embed = discord.Embed(title="Ошибка", description=f'Произошла ошибка: {e}', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await search_msg.edit(embed=embed)

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
        if voice_client:
            if voice_client.is_playing():
                voice_client.stop()
            self.queue.clear()
            embed = discord.Embed(title="Воспроизведение остановлено", color=int(config["success_color"],16))
            embed.set_thumbnail(url=config["success_icon"])
            await ctx.message.reply(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка", description='Бот не подключен к голосовому каналу.', color=int(config["error_color"], 16))
            embed.set_thumbnail(url=config["error_icon"])
            await ctx.message.reply(embed=embed)

    @commands.command(name='queue')
    async def show_queue(self, ctx):
        if not self.queue:
            embed = discord.Embed(title="Очередь пуста", color=int(config["info_color"], 16))
            embed.set_thumbnail(url=config["info_icon"])
            await ctx.message.reply(embed=embed)
            return

        queue_list = "\n".join([f"{i+1}. **{item['title']}** - {item['uploader']} ({item['duration']})" for i, item in enumerate(self.queue)])
        embed = discord.Embed(title="Очередь воспроизведения", description=queue_list, color=int(config["info_color"], 16))
        embed.set_thumbnail(url=config["info_icon"])
        await ctx.message.reply(embed=embed)

    async def play_next(self, ctx, error=None):
        if error:
            print(f'Ошибка воспроизведения: {error}')

        voice_client = ctx.voice_client
        if not voice_client:
            return

        if not self.queue:
            # Очередь пуста, можно отправить сообщение
            embed = discord.Embed(title="Очередь воспроизведения завершена", color=int(config["info_color"], 16))
            embed.set_thumbnail(url=config["info_icon"])
            await ctx.send(embed=embed)
            return

        # Берем следующий трек из очереди
        next_song = self.queue.pop(0)
        
        try:
            # Создаем аудио источник
            source = discord.FFmpegOpusAudio(
                next_song['url'], 
                executable=config["ffmpeg_path"], 
                **self.FFMPEG_OPTIONS
            )

            def after_playing(error):
                # Запускаем воспроизведение следующего трека
                if error:
                    print(f'Ошибка воспроизведения: {error}')
                asyncio.run_coroutine_threadsafe(self.play_next(ctx, error), self.bot.loop)

            # Воспроизводим
            voice_client.play(source, after=after_playing)
            
            # Отправляем информацию о текущем треке
            embed = discord.Embed(
                title="♬ Сейчас играет", 
                description=f''' 
                **Трек:**           [{next_song["title"]}]({next_song["webpage_url"] or next_song["url"]})\n
                **Исполнитель:**    {next_song["uploader"]}\n
                **Длительность:**   `{next_song["duration"]}` 
                ''',
                color=int(config["info_color"], 16)
            )
            embed.set_thumbnail(url=config["info_icon"])
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Ошибка при воспроизведении: {e}")
            # Пробуем воспроизвести следующий трек
            await self.play_next(ctx)

async def setup(bot):
    await bot.add_cog(Music(bot))