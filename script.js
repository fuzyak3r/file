document.addEventListener('DOMContentLoaded', function() {
    // Video loading handler
    const video = document.getElementById('video-background');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    if (video && loadingOverlay) {
        video.addEventListener('canplaythrough', function() {
            loadingOverlay.style.opacity = '0';
            setTimeout(function() {
                loadingOverlay.style.display = 'none';
            }, 500);
        });
        
        // Fallback if video takes too long to load
        setTimeout(function() {
            loadingOverlay.style.opacity = '0';
            setTimeout(function() {
                loadingOverlay.style.display = 'none';
            }, 500);
        }, 5000);
    }
    
    // Fade-in elements on scroll
    const fadeElements = document.querySelectorAll('.fade-in');
    
    function checkFade() {
        fadeElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('active');
            }
        });
    }
    
    window.addEventListener('scroll', checkFade);
    checkFade(); // Check on initial load
    
    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Check authentication status
    fetch('/api/user')
        .then(response => response.json())
        .then(data => {
            const navLinks = document.querySelector('.nav-links');
            if (!navLinks) return;
            
            // Find the Steam login button or container
            const loginItem = Array.from(navLinks.children).find(item => 
                item.querySelector('.steam-login') !== null
            );
            
            if (data.authenticated && data.user) {
                // User is logged in, replace login button with user profile
                if (loginItem) {
                    loginItem.innerHTML = `
                        <div class="user-profile">
                            <img src="${data.user.photos[0].value}" alt="${data.user.displayName}" class="user-avatar">
                            <span class="user-name">${data.user.displayName}</span>
                        </div>
                    `;
                    
                    // Добавляем класс для стилизации
                    loginItem.classList.add('user-profile-container');
                    
                    // Создаем выпадающее меню заранее и добавляем его
                    const dropdown = document.createElement('ul');
                    dropdown.className = 'profile-dropdown';
                    dropdown.innerHTML = `
                        <li><a href="/profile">Профиль</a></li>
                        <li><a href="/auth/logout">Выйти</a></li>
                    `;
                    loginItem.appendChild(dropdown);
                    
                    // Добавляем обработчик клика для отображения/скрытия выпадающего меню
                    const userProfile = loginItem.querySelector('.user-profile');
                    if (userProfile) {
                        userProfile.addEventListener('click', function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            // Переключаем класс active для выпадающего меню
                            dropdown.classList.toggle('active');
                            
                            // Если меню открыто, добавляем обработчик для закрытия при клике вне меню
                            if (dropdown.classList.contains('active')) {
                                function closeDropdown(e) {
                                    if (!loginItem.contains(e.target)) {
                                        dropdown.classList.remove('active');
                                        document.removeEventListener('click', closeDropdown);
                                    }
                                }
                                
                                // Добавляем обработчик с задержкой, чтобы избежать немедленного закрытия
                                setTimeout(() => {
                                    document.addEventListener('click', closeDropdown);
                                }, 10);
                            }
                        });
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error checking authentication:', error);
        });
});