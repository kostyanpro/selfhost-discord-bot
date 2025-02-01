const themeToggle = document.getElementById('theme-toggle');
const currentTheme = localStorage.getItem('theme');
const translations = {
  en: {
    title: "Bot Panel",
    start: "Start",
    stop: "Stop",
    settings: "Settings",
    token: "Token:",
    prefix: "Prefix:",
    ffmpeg_path: "FFmpeg Path:",
    create_channel_category: "Category ID for user rooms:",
    max_create_channel: "Maximum number of created rooms:",
    start_rep: "Initial reputation:",
    guild_id: "Server ID:",
    role_id: "Auto role ID for new members:",
    success_icon: "Success icon URL:",
    error_icon: "Error icon URL:",
    info_icon: "Info icon URL:",
    warn_icon: "Warning icon URL:",
    save: "Save",
    logs: "Logs"
  },
  ru: {
    title: "Панель управления ботом",
    start: "Запустить",
    stop: "Выключить",
    settings: "Настройки",
    token: "Токен:",
    prefix: "Префикс:",
    ffmpeg_path: "Путь до FFmpeg:",
    create_channel_category: "ID категории для пользовательских комнат:",
    max_create_channel: "Максимальное значение созданных комнат:",
    start_rep: "Начальная репутация:",
    guild_id: "ID сервера:",
    role_id: "ID автоматической роли при входе участника:",
    success_icon: "Ссылка на иконку успешного выполнения:",
    error_icon: "Ссылка на иконку ошибки при выполнении:",
    info_icon: "Ссылка на иконку вывода информации:",
    warn_icon: "Ссылка на иконку предупреждения при выполнении:",
    save: "Сохранить",
    logs: "Логи"
  }
};

const languageToggle = document.getElementById('language-toggle');
const currentLanguage = localStorage.getItem('language') || 'ru';

const updateTexts = (language) => {
  document.title = translations[language].title;
  document.querySelector('h2').textContent = translations[language].title;
  document.querySelector('.settings h2').textContent = translations[language].settings;
  document.querySelector('.logs h2').textContent = translations[language].logs;
  document.querySelector('button[onclick="location.href=\'/start\'"]').textContent = translations[language].start;
  document.querySelector('button[onclick="location.href=\'/stop\'"]').textContent = translations[language].stop;
  document.querySelector('form button[type="submit"]').textContent = translations[language].save;

  document.querySelector('label[for="token"]').textContent = translations[language].token;
  document.querySelector('label[for="prefix"]').textContent = translations[language].prefix;
  document.querySelector('label[for="ffmpeg_path"]').textContent = translations[language].ffmpeg_path;
  document.querySelector('label[for="create_channel_category"]').textContent = translations[language].create_channel_category;
  document.querySelector('label[for="max_create_channel"]').textContent = translations[language].max_create_channel;
  document.querySelector('label[for="start_rep"]').textContent = translations[language].start_rep;
  document.querySelector('label[for="guild_id"]').textContent = translations[language].guild_id;
  document.querySelector('label[for="role_id"]').textContent = translations[language].role_id;
  document.querySelector('label[for="success_icon"]').textContent = translations[language].success_icon;
  document.querySelector('label[for="error_icon"]').textContent = translations[language].error_icon;
  document.querySelector('label[for="info_icon"]').textContent = translations[language].info_icon;
  document.querySelector('label[for="warn_icon"]').textContent = translations[language].warn_icon;
};

updateTexts(currentLanguage);
languageToggle.textContent = currentLanguage === 'ru' ? 'EN' : 'RU';

languageToggle.addEventListener('click', () => {
  const newLanguage = currentLanguage === 'ru' ? 'en' : 'ru';
  localStorage.setItem('language', newLanguage);
  updateTexts(newLanguage);
  languageToggle.textContent = newLanguage === 'ru' ? 'EN' : 'RU';
});

if (currentTheme === 'dark') {
  document.body.setAttribute('data-theme', 'dark');
  themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
} else {
  document.body.setAttribute('data-theme', 'light');
  themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
}

themeToggle.addEventListener('click', () => {
  const theme = document.body.getAttribute('data-theme');
  if (theme === 'light') {
    document.body.setAttribute('data-theme', 'dark');
    themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    localStorage.setItem('theme', 'dark');
  } else {
    document.body.setAttribute('data-theme', 'light');
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    localStorage.setItem('theme', 'light');
  }
});