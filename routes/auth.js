const express = require('express');
const passport = require('passport');
const router = express.Router();

// Маршрут для начала авторизации через Steam
router.get('/steam', passport.authenticate('steam'), (req, res) => {
  // Этот код не будет выполнен, поскольку будет перенаправление на Steam
});

// Маршрут для обработки возврата от Steam
router.get('/steam/return', 
  passport.authenticate('steam', { failureRedirect: '/' }), 
  (req, res) => {
    // Успешная авторизация
    req.flash('success', 'Вы успешно вошли через Steam');
    res.redirect('/');
  }
);

// Маршрут для проверки состояния авторизации
router.get('/check', (req, res) => {
  if (req.isAuthenticated()) {
    res.json({
      authenticated: true,
      user: {
        steamId: req.user.id,
        name: req.user.displayName,
        avatar: req.user._json?.avatar,
        profileUrl: req.user._json?.profileurl
      }
    });
  } else {
    res.json({
      authenticated: false
    });
  }
});

// Маршрут для выхода
router.get('/logout', (req, res) => {
  req.logout((err) => {
    if (err) {
      console.error('Ошибка при выходе:', err);
      return res.redirect('/');
    }
    req.flash('success', 'Вы успешно вышли из системы');
    res.redirect('/');
  });
});

module.exports = router;