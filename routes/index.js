const express = require('express');
const router = express.Router();
const { ensureAuthenticated } = require('../middleware/auth');

// Главная страница
router.get('/', (req, res) => {
  res.render('index', {
    title: 'Counter-Strike: Reforge',
    partials: { header: 'header', footer: 'footer' },
    user: req.user
  });
});

// Защищенная страница профиля (доступна только после авторизации)
router.get('/profile', ensureAuthenticated, (req, res) => {
  res.render('profile', {
    title: 'Ваш профиль',
    partials: { header: 'header', footer: 'footer' },
    user: req.user
  });
});

module.exports = router;