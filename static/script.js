const translations = {
  en: {
    title: "Bot Control Panel",
    start: "Start Bot",
    stop: "Stop Bot",
    settings: "Configuration",
    save: "Save Changes",
    logs: "System Logs",
    status: "Status: "
  },
  ru: {
    title: "Панель управления",
    start: "Запустить",
    stop: "Выключить",
    settings: "Настройки",
    save: "Сохранить изменения",
    logs: "Логи системы",
    status: "Состояние: "
  }
};

const languageToggle = document.getElementById('language-toggle');
const themeToggle = document.getElementById('theme-toggle');
let currentLanguage = localStorage.getItem('language') || 'ru';

const updateTexts = (lang) => {
  document.getElementById('main-title').textContent = translations[lang].title;
  document.getElementById('btn-start-text').textContent = translations[lang].start;
  document.getElementById('btn-stop-text').textContent = translations[lang].stop;
  document.getElementById('settings-title').textContent = translations[lang].settings;
  document.getElementById('logs-title').textContent = translations[lang].logs;
  document.getElementById('btn-save-text').textContent = translations[lang].save;
  languageToggle.textContent = lang.toUpperCase();
};

// Переключение языка
languageToggle.addEventListener('click', () => {
  currentLanguage = currentLanguage === 'ru' ? 'en' : 'ru';
  localStorage.setItem('language', currentLanguage);
  updateTexts(currentLanguage);
});

// Переключение темы
themeToggle.addEventListener('click', () => {
  const isDark = document.body.getAttribute('data-theme') === 'dark';
  const newTheme = isDark ? 'light' : 'dark';
  document.body.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  themeToggle.innerHTML = newTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
});

// Инициализация темы
if (localStorage.getItem('theme') === 'dark') {
  document.body.setAttribute('data-theme', 'dark');
  themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
}

// Логи (SSE)
const logOutput = document.getElementById('log-output');
if (logOutput) {
  const eventSource = new EventSource('/stream_logs');
  eventSource.onmessage = (e) => {
    logOutput.value += e.data + '\n';
    logOutput.scrollTop = logOutput.scrollHeight;
  };
}

updateTexts(currentLanguage);