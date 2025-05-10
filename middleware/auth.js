// Проверка авторизации пользователя
function ensureAuthenticated(req, res, next) {
  if (req.isAuthenticated()) {
    return next();
  }
  
  req.flash('error', 'Для доступа к этой странице необходимо авторизоваться');
  res.redirect('/');
}

module.exports = {
  ensureAuthenticated
};