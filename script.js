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
    
    // Function to handle dropdown toggle
    function setupProfileDropdown(profileElement, dropdownElement) {
        if (!profileElement || !dropdownElement) return;
        
        // Toggle dropdown on click
        profileElement.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropdownElement.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!profileElement.contains(e.target) && !dropdownElement.contains(e.target)) {
                dropdownElement.classList.remove('active');
            }
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
                    // Create user profile element
                    loginItem.innerHTML = `
                        <div class="user-profile">
                            <img src="${data.user.photos[0].value}" alt="${data.user.displayName}" class="user-avatar">
                            <span class="user-name">${data.user.displayName}</span>
                        </div>
                        <div class="profile-dropdown">
                            <ul>
                                <li><a href="/profile"><i class="fas fa-user"></i> Профиль</a></li>
                                <li><a href="/auth/logout"><i class="fas fa-sign-out-alt"></i> Выйти</a></li>
                            </ul>
                        </div>
                    `;
                    
                    // Setup dropdown functionality
                    const profileElement = loginItem.querySelector('.user-profile');
                    const dropdownElement = loginItem.querySelector('.profile-dropdown');
                    setupProfileDropdown(profileElement, dropdownElement);
                }
            }
        })
        .catch(error => {
            console.error('Error checking authentication:', error);
        });
});