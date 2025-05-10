// Загружаем переменные окружения из .env файла
require('dotenv').config();

// Импортируем зависимости
const express = require('express');
const session = require('express-session');
const passport = require('passport');
const SteamStrategy = require('passport-steam').Strategy;
const path = require('path');
const helmet = require('helmet');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const flash = require('connect-flash');
const fs = require('fs');

// Создаем экземпляр приложения Express
const app = express();
const PORT = process.env.PORT || 3000;

// Настройка безопасности
app.use(helmet({
  contentSecurityPolicy: false // Отключаем CSP для разработки, включить в production
}));
app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true
}));

// Настройка парсинга данных
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Настройка сессий
app.use(session({
  secret: process.env.SESSION_SECRET || 'your_session_secret',
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: 24 * 60 * 60 * 1000 // 24 часа
  }
}));

// Настройка flash-сообщений
app.use(flash());

// Инициализация Passport
app.use(passport.initialize());
app.use(passport.session());

// Настройка Steam Strategy
passport.use(new SteamStrategy({
  returnURL: process.env.REDIRECT_URL,
  realm: process.env.REDIRECT_URL.split('/auth')[0],
  apiKey: process.env.STEAM_API_KEY
}, (identifier, profile, done) => {
  // Обработка данных профиля
  process.nextTick(() => {
    profile.identifier = identifier;
    return done(null, profile);
  });
}));

// Сериализация и десериализация пользователя для сессии
passport.serializeUser((user, done) => {
  done(null, user);
});

passport.deserializeUser((obj, done) => {
  done(null, obj);
});

// Промежуточное ПО для передачи информации о пользователе в ответы
app.use((req, res, next) => {
  res.locals.user = req.user || null;
  res.locals.error = req.flash('error');
  res.locals.success = req.flash('success');
  next();
});

// Статические файлы
app.use(express.static(path.join(__dirname, 'public')));

// Простой шаблонизатор для HTML файлов
app.engine('html', (filePath, options, callback) => {
  fs.readFile(filePath, (err, content) => {
    if (err) return callback(err);
    
    // Простая замена переменных в HTML
    let rendered = content.toString();
    
    // Обработка частичных шаблонов
    if (options.partials) {
      for (const [key, value] of Object.entries(options.partials)) {
        const partialPath = path.join(__dirname, 'views', 'partials', `${value}.html`);
        try {
          const partialContent = fs.readFileSync(partialPath, 'utf8');
          rendered = rendered.replace(new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g'), partialContent);
        } catch (error) {
          console.error(`Ошибка при загрузке частичного шаблона ${value}:`, error);
        }
      }
    }
    
    // Обработка данных пользователя
    if (options.user) {
      rendered = rendered.replace(/\{\{\s*user\.authenticated\s*\}\}/g, 'true');
      rendered = rendered.replace(/\{\{\s*user\.name\s*\}\}/g, options.user.displayName || '');
      rendered = rendered.replace(/\{\{\s*user\.avatar\s*\}\}/g, options.user._json?.avatar || '');
      rendered = rendered.replace(/\{\{\s*user\.profileUrl\s*\}\}/g, options.user._json?.profileurl || '');
      rendered = rendered.replace(/\{\{\s*user\.id\s*\}\}/g, options.user.id || '');
    } else {
      rendered = rendered.replace(/\{\{\s*user\.authenticated\s*\}\}/g, 'false');
    }
    
    // Замена других переменных
    for (const [key, value] of Object.entries(options)) {
      if (key !== 'partials' && key !== 'user' && typeof value === 'string') {
        rendered = rendered.replace(new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g'), value);
      }
    }
    
    callback(null, rendered);
  });
});
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'html');

// Маршруты
app.use('/', require('./routes/index'));
app.use('/auth', require('./routes/auth'));

// Обработка 404
app.use((req, res) => {
  res.status(404).render('error', { 
    title: 'Страница не найдена',
    message: 'Запрашиваемая страница не существует',
    statusCode: 404,
    partials: { header: 'header', footer: 'footer' },
    user: req.user
  });
});

// Обработка ошибок
app.use((err, req, res, next) => {
  console.error('Ошибка сервера:', err);
  
  res.status(err.status || 500).render('error', {
    title: 'Ошибка сервера',
    message: process.env.NODE_ENV === 'production' 
      ? 'Произошла внутренняя ошибка сервера' 
      : err.message,
    statusCode: err.status || 500,
    stack: process.env.NODE_ENV === 'production' ? null : err.stack,
    partials: { header: 'header', footer: 'footer' },
    user: req.user
  });
});

// Запуск сервера
app.listen(PORT, () => {
  console.log(`Сервер запущен на http://localhost:${PORT}`);
  console.log(`Режим: ${process.env.NODE_ENV || 'development'}`);
});