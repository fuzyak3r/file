document.addEventListener('DOMContentLoaded', function() {
    // Обработка прямых переходов на профиль
    const handleProfileClick = (e) => {
        if (e.target.matches('a[href="/profile"]')) {
            e.preventDefault();
            const currentPath = window.location.pathname;
            if (currentPath !== '/profile') {
                window.location.href = '/profile';
            }
        }
    };
    document.addEventListener('click', handleProfileClick);

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
    checkFade();
    
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
            
            const loginItem = Array.from(navLinks.children).find(item => 
                item.querySelector('.steam-login') !== null
            );
            
            if (data.authenticated && data.user) {
                if (loginItem) {
                    loginItem.innerHTML = `
                        <div class="user-profile">
                            <img src="${data.user.photos[0].value}" alt="${data.user.displayName}" class="user-avatar">
                            <span class="user-name">${data.user.displayName}</span>
                        </div>
                    `;
                    
                    loginItem.classList.add('user-profile-container');
                    
                    const dropdown = document.createElement('ul');
                    dropdown.className = 'profile-dropdown';
                    dropdown.innerHTML = `
                        <li><a href="/profile" onclick="event.preventDefault(); window.location.href='/profile';">Профиль</a></li>
                        <li><a href="/auth/logout">Выйти</a></li>
                    `;
                    loginItem.appendChild(dropdown);
                    
                    const userProfile = loginItem.querySelector('.user-profile');
                    if (userProfile) {
                        userProfile.addEventListener('click', function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            dropdown.classList.toggle('active');
                            
                            if (dropdown.classList.contains('active')) {
                                function closeDropdown(e) {
                                    if (!loginItem.contains(e.target)) {
                                        dropdown.classList.remove('active');
                                        document.removeEventListener('click', closeDropdown);
                                    }
                                }
                                
                                setTimeout(() => {
                                    document.addEventListener('click', closeDropdown);
                                }, 10);
                            }
                        });
                    }

                    dropdown.addEventListener('click', function(e) {
                        const target = e.target;
                        if (target.tagName === 'A') {
                            e.preventDefault();
                            const href = target.getAttribute('href');
                            if (href === '/profile') {
                                window.location.href = '/profile';
                            } else {
                                window.location.href = href;
                            }
                        }
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error checking authentication:', error);
        });
});