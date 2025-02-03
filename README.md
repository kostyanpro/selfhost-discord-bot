# 🚀 Self-Host Discord Bot

Этот проект позволяет вам запустить собственного Discord-бота на вашем компьютере. Просто следуйте инструкциям ниже, чтобы настроить и запустить бота за несколько шагов.

---

## 📖 Описание проекта

Этот Discord-бот разработан для того, чтобы пользователи могли легко запускать и настраивать его на своих устройствах. Бот поддерживает базовые функции, а также возможность проигрывания аудио через голосовые каналы. Проект идеально подходит для тех, кто хочет создать своего бота без необходимости глубоких знаний в программировании.

---

## 🛠 Установка и запуск

Следуйте этому пошаговому руководству, чтобы установить и запустить бота на вашем компьютере.

---

### 1. Скачивание архива проекта

Скачать архив со всеми файлами необходимыми для запуска бота можно [здесь.](https://github.com/kostyanpro/selfhost-discord-bot/releases)
> **Важно:** Необходимо скачивать последнюю доступную версию во избежание каких-либо ошибок.

---

### 2. Установите Python

Убедитесь, что у вас установлен **Python 3.10** или выше. Если Python не установлен, скачайте его с [официального сайта Python](https://www.python.org/downloads/).

> **Совет:** При установке Python на Windows обязательно установите флажок "Add Python to PATH", чтобы легко использовать Python из командной строки.

---

### 3. Установка виртуального окружения (только для Linux)

Если вы используете **Linux**, выполните следующую команду для установки необходимого пакета:

```bash
sudo apt install python3-venv -y
```

---

### 4. Создание виртуального окружения

#### Linux

Выполните следующую команду для установки необходимого пакета:

```bash
bash setup_venv.sh 
```

Этот скрипт создаст виртуальное окружение и активирует его.

#### Windows

Запустите файл **setup_venv.bat**, который выполнит аналогичные действия.

---

### 5. Запуск веб-интерфейса

#### Linux

Выполните следующую команду для запуска веб-интерфейса:

```bash
bash start.sh 
```

#### Windows

Запустите файл **start.bat**


---

### 6. Настройка конфига

После успешного запуска бота в терминале появятся ссылки для доступа к веб-интерфейсу. Перейдите по одной из них в вашем браузере. 

В веб-интерфейсе вы сможете настроить конфигурацию бота. Вам потребуется:

- **Токен бота**: Получите его на [портале разработчиков Discord](https://discord.com/developers/applications).
- **Префикс команд**: Установите префикс, который будет использоваться для вызова команд бота.
- **Каналы и роли**: Настройте, какие каналы и роли будет использовать бот.


>**Важно**: Если вы изменяете токен бота в конфиге, то нужно **перезапустить веб-интерфейс**.
Иконки для ембедов принимают только **URL** на картинку.
Цвета оформления ембедов обязательно вводить **hex-код**

---

### 7. Настройка бота для проигрывания аудио

Для работы бота с аудио необходима программа **FFmpeg**

####Linux

Введите в терминал:

```bash
sudo apt install ffmpeg
which ffmpeg
```

После второй команды вы увидите путь по которому установился **FFmpeg**. Его необходимо вставить в **конфиг**.

#### Windows

1. Скачайте **FFmpeg** с [официального сайта](https://www.ffmpeg.org/download.html).
2. Распакуйте архив.
3. Укажите путь до **FFmpeg.exe **в конфиге.

---

##🎉 Готово!

Теперь ваш Discord-бот готов к работе!
>Важно: Логи бота записываются в файл **bot.log**

##❓ Вопросы и поддержка

Если у вас возникли вопросы или проблемы, создайте **issue** в репозитории проекта.