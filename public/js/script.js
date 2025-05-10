document.addEventListener('DOMContentLoaded', function() {
    // Проверка и настройка видео на фоне
    setupVideoBackground();
    
    // Настройка анимации появления
    setupFadeInAnimation();
    
    // Настройка мобильного меню
    setupMobileMenu();
    
    // Проверка авторизации и отображение соответствующих элементов
    updateAuthUI();
    
    // Отображение flash-сообщений, если они есть
    displayFlashMessages();
});

// Функция настройки видео на фоне
function setupVideoBackground() {
    const video = document.getElementById('video-background');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    if (video) {
        function checkVideoReady() {
            if (video.readyState >= 3) {
                loadingOverlay.style.opacity = '0';
                setTimeout(() => {
                    loadingOverlay.style.display = 'none';
                }, 500);
            } else {
                setTimeout(checkVideoReady, 100);
            }
        }

        checkVideoReady();

        video.addEventListener('canplay', () => {
            loadingOverlay.style.opacity = '0';
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 500);
        });
        
        setTimeout(() => {
            if (loadingOverlay.style.display !== 'none') {
                loadingOverlay.style.opacity = '0';
                setTimeout(() => {
                    loadingOverlay.style.display = 'none';
                }, 500);
                
                video.style.display = 'none';
                document.querySelector('.hero').style.background = 'linear-gradient(rgba(18, 18, 18, 0.7), rgba(18, 18, 18, 0.9)), url("/images/background.jpg") no-repeat center center';
                document.querySelector('.hero').style.backgroundSize = 'cover';
            }
        }, 10000);
        
        function ensureVideoPlaying() {
            if (video.paused) {
                video.play().catch(err => {
                    console.log('Ошибка воспроизведения видео:', err);
                    setTimeout(ensureVideoPlaying, 1000);
                });
            }
        }

        video.addEventListener('loadedmetadata', ensureVideoPlaying);
        video.addEventListener('error', (e) => {
            console.error('Ошибка загрузки видео:', e);
            video.style.display = 'none';
            loadingOverlay.style.opacity = '0';
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 500);
            document.querySelector('.hero').style.background = 'linear-gradient(rgba(18, 18, 18, 0.7), rgba(18, 18, 18, 0.9)), url("/images/background.jpg") no-repeat center center';
            document.querySelector('.hero').style.backgroundSize = 'cover';
        });
    }
}

// Настройка анимации появления
function setupFadeInAnimation() {
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, { threshold: 0.1 });
    
    fadeElements.forEach(element => {
        observer.observe(element);
    });
}

// Настройка мобильного меню
function setupMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            if (navLinks.style.display === 'flex') {
                navLinks.style.display = 'none';
            } else {
                navLinks.style.display = 'flex';
                navLinks.style.position = 'absolute';
                navLinks.style.flexDirection = 'column';
                navLinks.style.top = '70px';
                navLinks.style.right = '20px';
                navLinks.style.backgroundColor = 'rgba(18, 18, 18, 0.95)';
                navLinks.style.padding = '20px';
                navLinks.style.borderRadius = '12px';
                navLinks.style.backdropFilter = 'blur(10px)';
                navLinks.style.border = '1px solid rgba(209, 212, 255, 0.1)';
                navLinks.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.3)';
                
                const navItems = navLinks.querySelectorAll('li');
                navItems.forEach(item => {
                    item.style.margin = '12px 0';
                });
            }
        });
    }
}

// Обновление интерфейса авторизации
function updateAuthUI() {
    const authContainer = document.getElementById('auth-container');
    if (!authContainer) return;
    
    fetch('/auth/check')
        .then(response => response.json())
        .then(data => {
            if (data.authenticated) {
                // Пользователь авторизован
                authContainer.innerHTML = `
                    <div class="user-profile">
                        <img src="${escapeHTML(data.user.avatar)}" alt="${escapeHTML(data.user.name)}" class="user-avatar">
                        <span class="user-name">${escapeHTML(data.user.name)}</span>
                        <a href="/auth/logout" class="logout-btn">Выйти</a>
                    </div>
                `;
            } else {
                // Пользователь не авторизован
                authContainer.innerHTML = `
                    <a href="/auth/steam" class="steam-login-btn">
                        <i class="fab fa-steam"></i> Войти через Steam
                    </a>
                `;
            }
        })
        .catch(error => {
            console.error('Ошибка при проверке авторизации:', error);
            
            // В случае ошибки показываем стандартную кнопку входа
            authContainer.innerHTML = `
                <a href="/auth/steam" class="steam-login-btn">
                    <i class="fab fa-steam"></i> Войти через Steam
                </a>
            `;
        });
}

// Отображение flash-сообщений
function displayFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        const type = message.dataset.type || 'info';
        const text = message.textContent;
        
        showNotification(text, type);
        
        // Удаляем элемент после отображения
        message.remove();
    });
}

// Функция для показа уведомлений
function showNotification(message, type = 'info') {
    // Проверяем, есть ли уже контейнер для уведомлений
    let notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        // Создаем контейнер, если его нет
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
    
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Иконка в зависимости от типа уведомления
    const icon = document.createElement('i');
    icon.className = type === 'error' ? 'fas fa-exclamation-circle' : 
                    type === 'success' ? 'fas fa-check-circle' : 'fas fa-info-circle';
    notification.appendChild(icon);
    
    // Текст уведомления
    const text = document.createElement('span');
    text.textContent = message;
    notification.appendChild(text);
    
    // Добавляем кнопку закрытия
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '&times;';
    closeButton.onclick = function() {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notificationContainer.contains(notification)) {
                notificationContainer.removeChild(notification);
            }
        }, 300);
    };
    notification.appendChild(closeButton);
    
    // Добавляем уведомление в контейнер
    notificationContainer.appendChild(notification);
    
    // Показываем уведомление с анимацией
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 10);
    
    // Автоматически скрываем через 5 секунд
    setTimeout(() => {
        if (notification.style.opacity !== '0') {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notificationContainer.contains(notification)) {
                    notificationContainer.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
}

// Вспомогательная функция для безопасного экранирования HTML
function escapeHTML(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}