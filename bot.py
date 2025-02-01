import json
import os
import asyncio
import sys
import random


import discord
import sqlite3
import yt_dlp


from gtts import gTTS
from discord.ext import commands
from googletrans import Translator
from scripts.initrepdb import *


''' подгрузка конфига '''
try:
    file = open('config.json', 'r')
    config = json.load(file)
    print("Конфиг загружен")
except:
    print("Ошибка конфиг не загружен! Проверьте наличие файла config.json")

''' цвета для эмбедов '''
SUCCESS_COLOR = 0x2ecc71  # Зеленый
ERROR_COLOR = 0xe74c3c    # Красный
INFO_COLOR = 0x3498db     # Синий
WARN_COLOR = 0xf1c40f     # Желтый


''' иконки для эмбедов '''
SUCCESS_ICON = config["success_icon"]
ERROR_ICON = config["error_icon"]
INFO_ICON = config["info_icon"]
WARN_ICON = config["warn_icon"]


''' открытие файла для записи лога '''
log_file = open('bot.log', 'a')


''' перенаправление стандартного вывода и стандартной ошибки в файл '''
sys.stdout = log_file
sys.stderr = log_file


''' параметры включения бота '''
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(config['prefix'], intents=intents)
bot.remove_command('help')


''' начальный счетчик созданных каналов '''
created_channels = 0


''' начальный счетчики в команде !play '''
queue = []
current_song = None


''' подключение базы данных '''
conn = sqlite3.connect('reputation.db')
cursor = conn.cursor()
cursor.execute(f'''CREATE TABLE IF NOT EXISTS reputation (
    user_id INTEGER PRIMARY KEY,
    reputation INTEGER DEFAULT {config["start_rep"]}
)''')
cursor.execute(f'''CREATE TABLE IF NOT EXISTS rep_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    target_id INTEGER,
    change INTEGER,
    timestamp INTEGER,
    FOREIGN KEY (user_id) REFERENCES reputation(user_id),
    FOREIGN KEY (target_id) REFERENCES reputation(user_id)
)''')
conn.commit()


''' настройки '''
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}
FFMPEG_OPTIONS_MP3 = {
    'options': '-vn'
}


''' получение репутации '''
def get_reputation(user_id):
    cursor.execute('SELECT reputation FROM reputation WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute('INSERT INTO reputation (user_id, reputation) VALUES (?, ?)', (user_id, config["start_rep"]))
        conn.commit()
        return config["start_rep"]
    
    
''' обновление репутации '''
def update_reputation(user_id, amount):
    cursor.execute('UPDATE reputation SET reputation = reputation + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()


''' отправка сообщения в ответ '''
async def send_reply(name='', value=''):
    embed = discord.Embed(title="", color=0xfaab34)
    embed.add_field(name=name, value=value, inline=False)
    return embed


''' форматирование времени '''
def format_duration(seconds):
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


''' получение ссылки на воспроизведение '''
async def get_audio_url(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        #'cookiefile': 'cookies.txt'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if not (query.startswith('https://www.youtube.com/') or query.startswith('www.youtube.com/')):
            info_dict = ydl.extract_info(query, download=False)
            if 'entries' in info_dict:
                video = info_dict['entries'][0]
                query = video['webpage_url']
            else:
                query = info_dict.get('webpage_url', None)
        try:
            info_dict = ydl.extract_info(query, download=False)
            if 'url' in info_dict:
                duration = info_dict.get('duration') or info_dict.get('duration_seconds')
                formatted_duration = format_duration(duration) 
                return {
                    'sourceurl': info_dict['url'], 
                    'title': info_dict.get('title'), 
                    'duration': formatted_duration, 
                    'url': info_dict.get('webpage_url')
                    }

            elif 'entries' in info_dict:
                video = info_dict['entries'][0]
                duration = info_dict.get('duration') or info_dict.get('duration_seconds')
                formatted_duration = format_duration(duration) 
                print(formatted_duration)

                return {
                    'sourceurl': video['url'], 
                    'title': video.get('title'), 
                    'duration': formatted_duration, 
                    'url': video.get('webpage_url')
                    }
            return None
        except yt_dlp.utils.DownloadError as e:
            print(f"Ошибка при извлечении информации о видео: {e}")
            return None


''' перевод текста '''
async def translate_text(word):
     async with Translator() as translator:
        result = await translator.translate(word, dest='russian')
        return result.text


''' озвучка текста '''
async def text_to_speech(text, output_file='output.mp3', lang='ru'):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(output_file)
        print(f"Аудиофайл сохранен как {output_file}")
    except Exception as e:
        print(f"Ошибка при создании аудиофайла: {e}")
        raise e


'''
функция при включении бота
'''
@bot.event
async def on_ready():
    print('Запуск бота')

    guild = bot.get_guild(config["guild_id"])
    bot.loop.create_task(manage_channels())

    if guild is None:
        print("Гильдия не найдена")
        return

    role_id = config["role_id"]
    role = guild.get_role(role_id)
    if role is None:
        print("Роль по умолчанию не найдена")
        return

    for member in guild.members:
        if not member.bot and len(member.roles) == 1:
            try:
                await member.add_roles(role)
                print(f'Роль {role.name} выдана участнику {member.name}')
            except discord.Forbidden:
                print(f'Нет прав для выдачи роли {role.name} участнику {member.name}')
            except discord.HTTPException as e:
                print(f'Ошибка при выдаче роли {role.name} участнику {member.name}: {e}')
    print('Проверка всех ролей прошла')


'''
цикл для проверки пустых 
пользовательских каналов
'''
async def manage_channels():
    await bot.wait_until_ready()
    global created_channels
    guild = bot.guilds[0]
    category_name = int(config["create_channel_category"])
    category = discord.utils.get(guild.categories, id=category_name)

    if category is None:
        print(f"Категория '{category_name}' не найдена")
        return

    while not bot.is_closed():
        for channel in category.voice_channels:
            if len(channel.members) == 0:
                print(f"Канал '{channel.name}' будет удален")
                await asyncio.sleep(60)
                if len(channel.members) == 0:
                    await channel.delete()
                    created_channels -= 1
                    print(f"Канал '{channel.name}' удален")
        await asyncio.sleep(60)


'''
ping command
'''
@bot.command(name='ping')
async def ping(ctx):
    embed = discord.Embed(title="Понг!", description="Проверка задержки...", color=INFO_COLOR)
    embed.set_thumbnail(url=INFO_ICON)
    message = await ctx.send(embed=embed)
    latency = bot.latency
    embed = discord.Embed(title="Понг!", description=f"Задержка: `{round(latency * 1000)} мс`", color=SUCCESS_COLOR)
    embed.set_thumbnail(url=SUCCESS_ICON)
    await message.edit(embed=embed)


'''
автоматическая роль при
входе нового человека
'''
@bot.event
async def on_member_join(member):
    guild = member.guild
    role_id = 859491650019524660
    role = guild.get_role(role_id)

    if role is None:
        print(f"роль с ID {role_id} не найдена на сервере {guild.name}")
        return
    try:
        await member.add_roles(role)
        print(f"роль с ID {role_id} выдана пользователю {member.name}")
    except discord.Forbidden:
        print(f"недостаточно прав для выдачи роли с ID {role_id} пользователю {member.name}")
    except discord.HTTPException as e:
        print(f"ошибка при выдаче роли с ID {role_id} пользователю {member.name}: {e}")


'''
Команда help
'''
@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(title="Список команд", color=INFO_COLOR)
    embed.set_thumbnail(url=INFO_ICON)
    embed.add_field(name="!ping", value="Проверка задержки бота", inline=False)
    embed.add_field(name="!roll [лимит]", value="Случайное число от 0 до указанного числа", inline=False)
    embed.add_field(name="!createroom [лимит] [название]", value="Создает новый голосовой канал с заданным названием и лимитом по пользователям. Канал будет удален через 5 минут отсутствия людей.", inline=False)
    embed.add_field(name="!play [ссылка на YT]", value="Включает музыку с указанного видео", inline=False)
    embed.add_field(name="!skip", value="Пропуск текущего трека", inline=False)
    embed.add_field(name="!queue", value="Список очереди треков", inline=False)
    embed.add_field(name="!stop", value="Остановка воспроизведения треков", inline=False)
    embed.add_field(name="!voice [текст]", value="Озвучка текста", inline=False)
    embed.add_field(name="!repinfo [@пользователь]", value="Информация о репутации пользователя", inline=False)
    embed.add_field(name="!reptop", value="Топ 10 пользователей по репутации", inline=False)
    embed.add_field(name="!help+", value="Список команд с повышенными правами", inline=False)
    message = await ctx.message.reply(embed=embed)

    await asyncio.sleep(180)
    await message.delete()


'''
Команда !help
'''
@bot.command(name='help+')
async def helpp(ctx):
    embed = discord.Embed(title="Список команд с повышенными правами", color=INFO_COLOR)
    embed.set_thumbnail(url=INFO_ICON)
    embed.add_field(name="!deleteallroom", value="Очистка всех созданных голосовых каналов", inline=False)
    embed.add_field(name="!deleteroom [ID канала]", value="Удаление пользовательского голосового канала", inline=False)
    embed.add_field(name="!join", value="Присоединение бота к каналу", inline=False)
    embed.add_field(name="!resetdbrep", value="Сброс базы данных репутации", inline=False)
    embed.add_field(name="!off", value="Корректное выключение бота", inline=False)
    message = await ctx.message.reply(embed=embed)

    await asyncio.sleep(180)
    await message.delete()


'''
Команда join
'''
@bot.command(name='join')
@commands.has_permissions(manage_channels=True)
async def join(ctx):
    if ctx.author.voice is None:
        embed = discord.Embed(title="Ошибка", description="Вы не в голосовом канале.", color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
    else:
        try:
            channel = ctx.author.voice.channel
            await channel.connect()
            embed = discord.Embed(title="Присоединение", description=f'Бот присоединился к каналу {channel.name}.', color=SUCCESS_COLOR)
            embed.set_thumbnail(url=SUCCESS_ICON)
            await ctx.message.reply(embed=embed)
        except discord.ClientException as e:
            embed = discord.Embed(title="Ошибка", description=f'Не удалось присоединиться к каналу: {e}', color=ERROR_COLOR)
            embed.set_thumbnail(url=ERROR_ICON)
            await ctx.message.reply(embed=embed)


'''
Обработка ошибок для команды !join
'''
@join.error
async def join_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="Ошибка", description='У вас недостаточно прав для использования этой команды.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)


'''
Команда !play
'''
@bot.command(name='play')
async def play(ctx, *, query):
    if not ctx.author.voice or not ctx.author.voice.channel:
        embed = discord.Embed(title="Ошибка", description='Вы не в голосовом чате.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    voice_channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    if voice_client is None:
        try:
            voice_client = await voice_channel.connect()
        except Exception as e:
            embed = discord.Embed(title="Ошибка", description=f'Не удалось подключиться к каналу: {e}', color=ERROR_COLOR)
            embed.set_thumbnail(url=ERROR_ICON)
            await ctx.message.reply(embed=embed)
            return
    else:
        if voice_client.channel != voice_channel:
            embed = discord.Embed(title="Ошибка", description='Бот подключен к другому каналу.', color=ERROR_COLOR)
            embed.set_thumbnail(url=ERROR_ICON)
            await ctx.message.reply(embed=embed)
            return
    track = await get_audio_url(query)
    if not track:
        embed = discord.Embed(title="Ошибка", description='Не удалось получить ссылку на аудио.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    queue.append(
            {
            'sourceurl': track['sourceurl'], 
            'title': track['title'], 
            'voice_client': voice_client, 
            'ctx': ctx, 
            'duration': track['duration'],
            'url': track['url']
            }
        )

    if not voice_client.is_playing():
        await play_next(ctx)

    if len(queue) > 1:
        embed = discord.Embed(
            title="Добавленно в очередь.", 
            description=f' \n[{queue[len(queue)-1]['title']}]({queue[len(queue)-1]['url']})\n**Длительность**\n`{queue[len(queue)-1]['duration']}`', 
            color=INFO_COLOR
            )
        embed.set_thumbnail(url=INFO_ICON)
        await ctx.message.reply(embed=embed)


''' Функция для воспроизведения следующего трека '''
async def play_next(ctx):
    global current_song
    if not queue:
        return

    current_song = queue[0]
    voice_client = current_song['voice_client']

    def after_play(error):
        if error:
            print(f'Ошибка при воспроизведении: {error}')
        queue.pop(0)
        current_song = None
        asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)

    try:
        print('voice_client.play')
        voice_client.play(discord.FFmpegPCMAudio(source=current_song['sourceurl'], executable=config["ffmpeg_path"],**FFMPEG_OPTIONS), after=after_play)

        embed = discord.Embed(
            title="Сейчас играет:", 
            description=f' [{current_song["title"]}]({current_song['url']}).. \n**Длительность**\n `{current_song['duration']}`',
            color=INFO_COLOR
            )

        embed.set_thumbnail(url=INFO_ICON)
        await current_song['ctx'].message.reply(embed=embed)
    except Exception as e:
        print(f'Ошибка при воспроизведении: {e}')
        queue.pop(0)
        current_song = None
        embed = discord.Embed(title="Ошибка", description=f'{e}..', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        await play_next(ctx)


''' команда !skip '''
@bot.command(name='skip')
async def skip(ctx):
    if not current_song:
        embed = discord.Embed(title="Ошибка", description='Сейчас ничего не играет.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    voice_client = current_song['voice_client']
    if voice_client.is_playing():
        voice_client.stop()
        embed = discord.Embed(title="", description='Текущий трек пропущен.', color=SUCCESS_COLOR)
        embed.set_thumbnail(url=SUCCESS_ICON)
        await ctx.message.reply(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка", description='Сейчас ничего не играет.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)


''' Команда !stop '''
@bot.command(name='stop')
async def stop(ctx):
    if not current_song:
        embed = discord.Embed(title="Ошибка", description='Сейчас ничего не играет.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    voice_client = current_song['voice_client']
    if voice_client.is_playing():
        voice_client.stop()
        queue.clear()
        embed = discord.Embed(title="", description='Воспроизведение остановлено и очередь очищена.', color=SUCCESS_COLOR)
        embed.set_thumbnail(url=SUCCESS_ICON)
        await ctx.message.reply(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка", description='Сейчас ничего не играет.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)


''' Команда !queue '''
@bot.command(name='queue')
async def show_queue(ctx):
    if not queue:
        await ctx.message.reply('Очередь пуста.')
        return
    queue_list = '\n'.join([f'{i+1}. {item["title"]}' for i, item in enumerate(queue)])
    embed = discord.Embed(title="Очередь", description=f'{queue_list}', color=INFO_COLOR)
    embed.set_thumbnail(url=INFO_ICON)
    await ctx.message.reply(embed=embed)


'''
озвучка текста
'''
@bot.command(name='voice')
async def voice(ctx, *, text: str):
    if not ctx.author.voice or not ctx.author.voice.channel:
        embed = discord.Embed(title="Ошибка", description='Вы не в голосовом канале!', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    voice_channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    if voice_client is None:
        try:
            voice_client = await voice_channel.connect()
        except Exception as e:
            embed = discord.Embed(title="Ошибка при подключении к голосовому каналу", description=f'{e}', color=ERROR_COLOR)
            embed.set_thumbnail(url=ERROR_ICON)
            await ctx.message.reply(embed=embed)
            return
    else:
        if voice_client.channel != voice_channel:
            embed = discord.Embed(title="Ошибка", description='Бот уже подключен к другому каналу.', color=ERROR_COLOR)
            embed.set_thumbnail(url=ERROR_ICON)
            await ctx.message.reply(embed=embed)
            return

    if len(text) > 500:
        embed = discord.Embed(title="Ошибка", description='Слишком много символов.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    try:
        translated_text = await translate_text(text)
    except Exception as e:
        embed = discord.Embed(title="Ошибка при переводе", description=f'{e}', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    try:
        await text_to_speech(text=translated_text)
    except Exception as e:
        embed = discord.Embed(title="Ошибка при создании аудиофайла", description=f'{e}', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    audio_file = 'output.mp3' 

    if not os.path.exists(audio_file):
        embed = discord.Embed(title="Ошибка", description='Аудиофайл не найден.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    def after_play(error):
        if error:
            print(f'Ошибка при воспроизведении: {error}')
        else:
            print(f'Воспроизведение завершено: {audio_file}')
        try:
            os.remove(audio_file)
            print(f'Файл {audio_file} удален.')
            voice_client.stop()
        except Exception as e:
            print(f'Ошибка при удалении файла: {e}')

    try:
        voice_client.play(discord.FFmpegOpusAudio(source=audio_file, executable=config["ffmpeg_path"], **FFMPEG_OPTIONS_MP3), after=after_play)
        embed = discord.Embed(title="Сейчас озвучивается", description=f'{translated_text}', color=INFO_COLOR)
        embed.set_thumbnail(url=INFO_ICON)
        await ctx.message.reply(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="Ошибка", description=f'{e}', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)


'''           
создание пользователького
голосового канала
'''
@bot.command(name='createroom')
async def createroom(ctx, limit: int, *, name: str):
    global created_channels
    if created_channels >= int(config['max_create_channel']):
        embed = discord.Embed(title="Ошибка создания", description=f'Превышено максимальное количество каналов ({config['max_create_channel']}).', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return
    if limit >= 100:
        embed = discord.Embed(title="Ошибка создания", description='Максимальный лимит 99.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    created_channels += 1
    guild = ctx.guild
    category = discord.utils.get(guild.categories, id=int(config["create_channel_category"]))

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(connect=True),
        guild.me: discord.PermissionOverwrite(connect=True),
    }
    
    await guild.create_voice_channel(name=name, overwrites=overwrites, category=category, user_limit=limit)
    embed = discord.Embed(title="", description=f'Канал "{name}" создан.', color=SUCCESS_COLOR)
    embed.set_thumbnail(url=SUCCESS_ICON)
    await ctx.message.reply(embed=embed)


'''
удаление всех пользовательских
комнат
'''
@bot.command()
@commands.has_permissions(manage_channels=True)
async def deleteallroom(ctx):
    global created_channels
    guild = ctx.guild
    category = discord.utils.get(guild.categories, id=int(config["create_channel_category"]))
    if category is None:
        embed = discord.Embed(title="Ошибка", description=f'Категория {config["create_channel_category"]} не найдена.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    deleted_channels = 0
    for channel in category.channels:
        if isinstance(channel, discord.VoiceChannel) or isinstance(channel, discord.TextChannel):
            if len(channel.members) == 0:
                await channel.delete()
                deleted_channels += 1
                created_channels -= 1

    embed = discord.Embed(title="", description=f'Удалено {deleted_channels} каналов.', color=SUCCESS_COLOR)
    embed.set_thumbnail(url=SUCCESS_ICON)
    await ctx.message.reply(embed=embed)


'''
обработка ошибок для команды !deleteallroom
'''
@deleteallroom.error
async def clearcreatedroom_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="Ошибка", description='У вас нет прав для использования этой команды.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
    elif isinstance(error, commands.MissingRole):
        embed = discord.Embed(title="Ошибка", description='У вас нет необходимой роли для использования этой команды.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)


'''
удаление комнаты по ID
'''
@bot.command()
@commands.has_permissions(manage_channels=True)
async def deleteroom(ctx, channel_id: int):
    guild = ctx.guild
    channel = guild.get_channel(channel_id)

    if channel is None:
        embed = discord.Embed(title="Ошибка", description='Канал с таким ID не найден.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    if not isinstance(channel, discord.VoiceChannel):
        embed = discord.Embed(title="Ошибка", description='Указанный канал не является голосовым.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return
    category = channel.category
    if category.id != int(config["create_channel_category"]):
        embed = discord.Embed(title="Ошибка", description='Канал не является пользовательским.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return
    await channel.delete()
    embed = discord.Embed(title="", description=f'Канал "{channel.name}" удален.', color=SUCCESS_COLOR)
    embed.set_thumbnail(url=SUCCESS_ICON)
    await ctx.message.reply(embed=embed)


'''
обработка ошибок для команды !deleteroom
'''
@deleteroom.error
async def deletechannel_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="Ошибка", description='У вас нет прав для использования этой команды.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="Ошибка", description='Пожалуйста, укажите корректный ID канала.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)


'''
случайное число
'''
@bot.command(name='roll')
async def roll(ctx, limit='100'):
    if limit.isdigit():
        if int(limit) > 1000000000:
            embed = discord.Embed(title="Ошибка", description='Слишком большое число.', color=ERROR_COLOR)
            embed.set_thumbnail(url=ERROR_ICON)
            await ctx.message.reply(embed=embed)
            return
        embed = discord.Embed(title=f"Случайное число (0-{limit}):", description=f'**{random.randint(0, int(limit))}**', color=SUCCESS_COLOR)
        embed.set_thumbnail(url=SUCCESS_ICON)
        await ctx.message.reply(embed=embed)
    else:
        embed = discord.Embed(title="Ошибка", description='Некорректное число.', color=ERROR_COLOR)
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)


''' 
обработка сообщений 
'''
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith(config['prefix']):
        await bot.process_commands(message)
        return
    user_id = message.author.id
    cursor.execute('SELECT message_count FROM message_counts WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        message_count = result[0] + 1
        cursor.execute('UPDATE message_counts SET message_count = ? WHERE user_id = ?', (message_count, user_id))
    else:
        message_count = 1
        cursor.execute('INSERT INTO message_counts (user_id, message_count) VALUES (?, ?)', (user_id, message_count))
    conn.commit()

    if message_count >= 20:
        cursor.execute('SELECT reputation FROM reputation WHERE user_id = ?', (user_id,))
        rep_result = cursor.fetchone()
        if rep_result:
            reputation = rep_result[0] + 1
            cursor.execute('UPDATE reputation SET reputation = ? WHERE user_id = ?', (reputation, user_id))
        else:
            reputation = config["start_rep"] + 1
            cursor.execute('INSERT INTO reputation (user_id, reputation) VALUES (?, ?)', (user_id, reputation))
        cursor.execute('UPDATE message_counts SET message_count = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
        print(f'+1, {user_id}')

    await bot.process_commands(message)


'''
информация о репутации
'''
@bot.command(name='repinfo')
async def repinfo(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author

    cursor.execute('SELECT reputation FROM reputation WHERE user_id = ?', (user.id,))
    result = cursor.fetchone()
    if result:
        reputation = result[0]
        embed = discord.Embed(
            title=f"Репутация пользователя {user.name}",
            description=f"Репутация: {reputation}",
            color=INFO_COLOR
        )
        embed.set_thumbnail(url=INFO_ICON)
        await ctx.message.reply(embed=embed)
    else:
        embed = discord.Embed(
            title="Ошибка",
            description=f"{user.mention} еще не начисляли репутацию.",
            color=ERROR_COLOR
        )
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)


'''
топ 10 по репутации
'''
@bot.command(name='reptop')
async def reptop(ctx):
    cursor.execute('SELECT user_id, reputation FROM reputation ORDER BY reputation DESC LIMIT 10')
    top_users = cursor.fetchall()

    if not top_users:
        embed = discord.Embed(
            title="Ошибка",
            description="Топ пользователей по репутации пуст.",
            color=ERROR_COLOR
        )
        embed.set_thumbnail(url=ERROR_ICON)
        await ctx.message.reply(embed=embed)
        return

    embed = discord.Embed(
        title="Топ 10 пользователей по репутации",
        color=SUCCESS_COLOR
    )
    embed.set_thumbnail(url=SUCCESS_ICON)
    for idx, user in enumerate(top_users, start=1):
        user_obj = bot.get_user(user[0])
        if user_obj:
            username = user_obj.name
        else:
            username = f"User ID {user[0]}"
        embed.add_field(
            name=f"{idx}. {username}",
            value=f"Репутация: {user[1]}",
            inline=False
        )

    await ctx.send(embed=embed)


'''
сброс базы данных с репутацией
'''
@bot.command(name='resetdbrep')
@commands.has_permissions(administrator=True)
async def resetdbrep(ctx):
    global conn
    global cursor
    conn.close()
    os.remove('.\\reputation.db')
    print('reputation.db удалена')
    await initialize_database()
    conn = sqlite3.connect('reputation.db')
    cursor = conn.cursor()

    await ctx.message.reply(embed=await send_reply(name='```датабаза репутаций сброшена```', value=f''))
@resetdbrep.error
async def resetdbrep_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.message.reply(embed=await send_reply(name='ошибка', value=f'у вас нет прав для использования этой команды'))


'''
выключение бота
'''
@bot.command(name='off')
@commands.has_permissions(administrator=True)
async def off(ctx):
    await ctx.message.reply(embed=await send_reply(name='```выключение бота!```', value=f''))
    voice_clients = bot.voice_clients
    for voice_client in voice_clients:
        if voice_client.is_playing():
            voice_client.stop()
        await voice_client.disconnect()

    guild = ctx.guild
    category = discord.utils.get(guild.categories, id=int(config["create_channel_category"]))
    for channel in category.channels:
        if len(channel.members) == 0:
            if isinstance(channel, discord.VoiceChannel) or isinstance(channel, discord.TextChannel):
                await channel.delete()
    await bot.close()
@off.error
async def shutdown_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.message.reply(embed=await send_reply(name='ошибка', value=f'у вас нет прав для использования этой команды'))


'''
выключение
'''
@bot.event
async def on_disconnect():
    print('Выключение бота!')
    

bot.run(config['token'])