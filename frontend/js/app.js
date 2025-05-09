// Main application logic
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in (based on localStorage for demo)
    checkAuthStatus();
    
    // Load content based on current route
    loadContent(window.location.pathname);
    
    // Initialize event listeners
    initEventListeners();
});

// Check if user is authenticated
function checkAuthStatus() {
    const userData = localStorage.getItem('userData');
    const userSection = document.getElementById('user-section');
    
    if (userData) {
        const user = JSON.parse(userData);
        userSection.innerHTML = `
            <div class="user-profile">
                <div class="user-avatar">
                    <img src="${user.avatar}" alt="${user.name}">
                </div>
                <div class="user-info">
                    <div class="user-name">${user.name}</div>
                    <div class="user-points"><span class="points-value">${user.points}</span> points</div>
                </div>
            </div>
        `;
    } else {
        userSection.innerHTML = `<a href="/auth/steam" class="steam-login">Login with Steam</a>`;
    }
}

// Initialize event listeners
function initEventListeners() {
    // Intercept navigation links to use the router
    document.addEventListener('click', function(e) {
        const target = e.target.closest('a');
        if (target && target.getAttribute('href').startsWith('/') && !target.getAttribute('href').startsWith('/auth')) {
            e.preventDefault();
            const url = target.getAttribute('href');
            history.pushState(null, '', url);
            loadContent(url);
        }
    });
    
    // Handle back/forward browser navigation
    window.addEventListener('popstate', function() {
        loadContent(window.location.pathname);
    });
}

// Load content based on route
function loadContent(route) {
    const contentElement = document.getElementById('content');
    
    // Simple router logic
    if (route === '/' || route === '') {
        // Home page is already in the HTML, no need to load
        document.title = 'CSReforge - CS:GO Skin Economy';
    } else if (route === '/cases') {
        loadCases(contentElement);
    } else if (route.startsWith('/cases/')) {
        const caseName = route.replace('/cases/', '');
        loadCaseDetails(contentElement, caseName);
    } else if (route === '/crafting') {
        loadCrafting(contentElement);
    } else if (route === '/leaderboard') {
        loadLeaderboard(contentElement);
    } else if (route.startsWith('/id/')) {
        const parts = route.split('/');
        if (parts.length >= 3) {
            const steamId = parts[2];
            if (parts.length >= 4 && parts[3] === 'inventory') {
                loadUserInventory(contentElement, steamId);
            } else if (parts.length >= 4 && parts[3] === 'profile') {
                loadUserProfile(contentElement, steamId);
            } else {
                loadUserProfile(contentElement, steamId);
            }
        }
    } else {
        // 404 Not Found
        contentElement.innerHTML = `
            <div class="not-found">
                <h1>404</h1>
                <p>Page not found</p>
                <a href="/" class="btn primary">Back to Home</a>
            </div>
        `;
        document.title = 'Not Found - CSReforge';
    }
}

// Load cases page
function loadCases(element) {
    // In a real app, this would fetch from API
    document.title = 'Cases - CSReforge';
    
    element.innerHTML = `
        <div class="page-header">
            <h1>Available Cases</h1>
            <p>Select a case to open and get awesome skins!</p>
        </div>
        
        <div class="case-grid">
            <div class="case-item">
                <div class="case-image">
                    <img src="images/cases/premium-case.png" alt="Premium Case">
                </div>
                <div class="case-info">
                    <div class="case-name">Premium Case</div>
                    <div class="case-price">
                        <span>Chance for rare skins</span>
                        <span class="case-points">1500 pts</span>
                    </div>
                </div>
                <a href="/cases/premium-case" class="case-link"></a>
            </div>
            
            <div class="case-item">
                <div class="case-image">
                    <img src="images/cases/standard-case.png" alt="Standard Case">
                </div>
                <div class="case-info">
                    <div class="case-name">Standard Case</div>
                    <div class="case-price">
                        <span>Most popular</span>
                        <span class="case-points">800 pts</span>
                    </div>
                </div>
                <a href="/cases/standard-case" class="case-link"></a>
            </div>
            
            <div class="case-item">
                <div class="case-image">
                    <img src="images/cases/knife-case.png" alt="Knife Case">
                </div>
                <div class="case-info">
                    <div class="case-name">Knife Case</div>
                    <div class="case-price">
                        <span>Knife collection</span>
                        <span class="case-points">3000 pts</span>
                    </div>
                </div>
                <a href="/cases/knife-case" class="case-link"></a>
            </div>
            
            <div class="case-item">
                <div class="case-image">
                    <img src="images/cases/starter-case.png" alt="Starter Case">
                </div>
                <div class="case-info">
                    <div class="case-name">Starter Case</div>
                    <div class="case-price">
                        <span>For beginners</span>
                        <span class="case-points">300 pts</span>
                    </div>
                </div>
                <a href="/cases/starter-case" class="case-link"></a>
            </div>
        </div>
    `;
}

// Load case details page
function loadCaseDetails(element, caseName) {
    // In a real app, this would fetch from API
    document.title = `${formatCaseName(caseName)} - CSReforge`;
    
    // Mock case data (this would come from API)
    const caseData = {
        'premium-case': {
            name: 'Premium Case',
            description: 'The best case with the rarest skins. Try your luck!',
            price: 1500,
            image: 'images/cases/premium-case.png',
            items: [
                { name: 'Dragon Lore', weapon: 'AWP', rarity: 'exotic', image: 'images/skins/awp-dragonlore.png' },
                { name: 'Asiimov', weapon: 'M4A4', rarity: 'ancient', image: 'images/skins/m4a4-asiimov.png' },
                { name: 'Neo-Noir', weapon: 'USP-S', rarity: 'legendary', image: 'images/skins/usp-neonoir.png' },
                { name: 'Howl', weapon: 'M4A4', rarity: 'exotic', image: 'images/skins/m4a4-howl.png' },
                { name: 'Fire Serpent', weapon: 'AK-47', rarity: 'ancient', image: 'images/skins/ak47-fireserpent.png' },
                { name: 'Fade', weapon: 'Butterfly Knife', rarity: 'exotic', image: 'images/skins/butterfly-fade.png' },
                { name: 'Hyper Beast', weapon: 'AWP', rarity: 'legendary', image: 'images/skins/awp-hyperbeast.png' },
                { name: 'Printstream', weapon: 'Desert Eagle', rarity: 'legendary', image: 'images/skins/deagle-printstream.png' },
                { name: 'Bullet Rain', weapon: 'M4A4', rarity: 'mythical', image: 'images/skins/m4a4-bulletrain.png' },
                { name: 'Redline', weapon: 'AK-47', rarity: 'mythical', image: 'images/skins/ak47-redline.png' },
                { name: 'Decimator', weapon: 'M4A1-S', rarity: 'rare', image: 'images/skins/m4a1s-decimator.png' },
                { name: 'Cyrex', weapon: 'M4A1-S', rarity: 'rare', image: 'images/skins/m4a1s-cyrex.png' }
            ]
        },
        'standard-case': {
            name: 'Standard Case',
            description: 'A balanced case with good chances for quality skins.',
            price: 800,
            image: 'images/cases/standard-case.png',
            items: [
                { name: 'Asiimov', weapon: 'AWP', rarity: 'ancient', image: 'images/skins/awp-asiimov.png' },
                { name: 'Bloodsport', weapon: 'AK-47', rarity: 'legendary', image: 'images/skins/ak47-bloodsport.png' },
                { name: 'Cyrex', weapon: 'M4A1-S', rarity: 'rare', image: 'images/skins/m4a1s-cyrex.png' },
                { name: 'Hyper Beast', weapon: 'M4A1-S', rarity: 'legendary', image: 'images/skins/m4a1s-hyperbeast.png' },
                { name: 'Neon Rider', weapon: 'MAC-10', rarity: 'mythical', image: 'images/skins/mac10-neonrider.png' },
                { name: 'Ocean Drive', weapon: 'Glock-18', rarity: 'legendary', image: 'images/skins/glock-oceandrive.png' },
                { name: 'Neo-Noir', weapon: 'USP-S', rarity: 'legendary', image: 'images/skins/usp-neonoir.png' },
                { name: 'Water Elemental', weapon: 'Glock-18', rarity: 'mythical', image: 'images/skins/glock-waterelemental.png' },
                { name: 'Frontside Misty', weapon: 'AK-47', rarity: 'rare', image: 'images/skins/ak47-frontsidemisty.png' },
                { name: 'Phobos', weapon: 'M4A1-S', rarity: 'uncommon', image: 'images/skins/m4a1s-phobos.png' },
                { name: 'Worm God', weapon: 'AWP', rarity: 'uncommon', image: 'images/skins/awp-wormgod.png' },
                { name: 'Atomic Alloy', weapon: 'M4A1-S', rarity: 'rare', image: 'images/skins/m4a1s-atomicalloy.png' }
            ]
        },
        'knife-case': {
            name: 'Knife Case',
            description: 'Exclusive knife skins case with high value items.',
            price: 3000,
            image: 'images/cases/knife-case.png',
            items: [
                { name: 'Fade', weapon: 'Butterfly Knife', rarity: 'exotic', image: 'images/skins/butterfly-fade.png' },
                { name: 'Doppler', weapon: 'Karambit', rarity: 'exotic', image: 'images/skins/karambit-doppler.png' },
                { name: 'Marble Fade', weapon: 'M9 Bayonet', rarity: 'exotic', image: 'images/skins/m9-marblefade.png' },
                { name: 'Tiger Tooth', weapon: 'Butterfly Knife', rarity: 'exotic', image: 'images/skins/butterfly-tigertooth.png' },
                { name: 'Lore', weapon: 'Karambit', rarity: 'exotic', image: 'images/skins/karambit-lore.png' },
                { name: 'Crimson Web', weapon: 'M9 Bayonet', rarity: 'exotic', image: 'images/skins/m9-crimsonweb.png' },
                { name: 'Fade', weapon: 'Talon Knife', rarity: 'exotic', image: 'images/skins/talon-fade.png' },
                { name: 'Gamma Doppler', weapon: 'Karambit', rarity: 'exotic', image: 'images/skins/karambit-gammadoppler.png' },
                { name: 'Autotronic', weapon: 'Flip Knife', rarity: 'ancient', image: 'images/skins/flip-autotronic.png' },
                { name: 'Slaughter', weapon: 'Huntsman Knife', rarity: 'ancient', image: 'images/skins/huntsman-slaughter.png' },
                { name: 'Damascus Steel', weapon: 'Gut Knife', rarity: 'legendary', image: 'images/skins/gut-damascussteel.png' },
                { name: 'Vanilla', weapon: 'Butterfly Knife', rarity: 'legendary', image: 'images/skins/butterfly-vanilla.png' }
            ]
        },
        'starter-case': {
            name: 'Starter Case',
            description: 'Perfect for beginners. Affordable and contains good starter skins.',
            price: 300,
            image: 'images/cases/starter-case.png',
            items: [
                { name: 'Asiimov', weapon: 'P90', rarity: 'mythical', image: 'images/skins/p90-asiimov.png' },
                { name: 'Phobos', weapon: 'M4A1-S', rarity: 'uncommon', image: 'images/skins/m4a1s-phobos.png' },
                { name: 'Worm God', weapon: 'AWP', rarity: 'uncommon', image: 'images/skins/awp-wormgod.png' },
                { name: 'Wing Shot', weapon: 'USP-S', rarity: 'uncommon', image: 'images/skins/usp-wingshot.png' },
                { name: 'Eco', weapon: 'Galil AR', rarity: 'uncommon', image: 'images/skins/galil-eco.png' },
                { name: 'Evil Daimyo', weapon: 'M4A4', rarity: 'uncommon', image: 'images/skins/m4a4-evildaimyo.png' },
                { name: 'Torque', weapon: 'SSG 08', rarity: 'uncommon', image: 'images/skins/ssg08-torque.png' },
                { name: 'Copper Galaxy', weapon: 'Desert Eagle', rarity: 'rare', image: 'images/skins/deagle-coppergalaxy.png' },
                { name: 'Conspiracy', weapon: 'USP-S', rarity: 'rare', image: 'images/skins/usp-conspiracy.png' },
                { name: 'Urban Hazard', weapon: 'MP7', rarity: 'common', image: 'images/skins/mp7-urbanhazard.png' },
                { name: 'Elite Build', weapon: 'AK-47', rarity: 'common', image: 'images/skins/ak47-elitebuild.png' },
                { name: 'Basilisk', weapon: 'USP-S', rarity: 'common', image: 'images/skins/usp-basilisk.png' }
            ]
        }
    };
    
    const caseInfo = caseData[caseName] || {
        name: formatCaseName(caseName),
        description: 'Case details not found.',
        price: 0,
        image: 'images/cases/default-case.png',
        items: []
    };
    
    element.innerHTML = `
        <div class="page-header">
            <h1>${caseInfo.name}</h1>
        </div>
        
        <div class="case-details">
            <div class="case-preview">
                <div class="case-preview-image">
                    <img src="${caseInfo.image}" alt="${caseInfo.name}">
                </div>
                <div class="case-preview-info">
                    <div class="case-preview-name">${caseInfo.name}</div>
                    <div class="case-preview-description">${caseInfo.description}</div>
                    <div class="case-preview-price">Price: <span class="case-price-value">${caseInfo.price} points</span></div>
                    <button class="open-case-btn" onclick="startCaseOpening('${caseName}')">Open Case</button>
                </div>
            </div>
            
            <div class="case-items-list">
                <h2>Possible Items</h2>
                <div class="case-items-grid">
                    ${caseInfo.items.map(item => `
                        <div class="case-item-small">
                            <div class="case-item-small-image">
                                <img src="${item.image}" alt="${item.name}">
                            </div>
                            <div class="case-item-small-name">${item.name}</div>
                            <div class="case-item-small-weapon">${item.weapon}</div>
                            <div class="case-item-rarity rarity-${item.rarity}">${item.rarity}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
        
        <div class="case-opening-container" style="display: none;">
            <h2>Opening Case</h2>
            
            <div class="case-opening">
                <div class="case-marker"></div>
                <div class="case-items" id="case-items-container">
                    <!-- Items will be generated here -->
                </div>
            </div>
            
            <div class="case-result" id="case-result">
                <h3 class="case-result-title">You received:</h3>
                <div class="case-result-image">
                    <img src="" alt="Item" id="result-image">
                </div>
                <div class="case-result-info">
                    <div class="case-result-name" id="result-name"></div>
                    <div class="case-result-weapon" id="result-weapon"></div>
                    <div class="case-item-rarity" id="result-rarity"></div>
                </div>
                <div class="case-result-buttons">
                    <button class="btn primary" onclick="openAnotherCase()">Open Another</button>
                    <button class="btn secondary" onclick="viewInventory()">View Inventory</button>
                </div>
            </div>
        </div>
    `;
    
    // Add script for case opening
    const script = document.createElement('script');
    script.innerHTML = `
        function startCaseOpening(caseName) {
            // Check if user is logged in
            const userData = localStorage.getItem('userData');
            if (!userData) {
                alert('Please log in to open cases.');
                window.location.href = '/auth/steam';
                return;
            }
            
            const user = JSON.parse(userData);
            const caseData = ${JSON.stringify(caseData)}[caseName];
            
            if (user.points < caseData.price) {
                alert('Not enough points. You need ' + caseData.price + ' points to open this case.');
                return;
            }
            
            // In a real app, this would be an API call
            // For demo, we'll just update localStorage
            user.points -= caseData.price;
            localStorage.setItem('userData', JSON.stringify(user));
            
            // Update UI
            checkAuthStatus();
            document.querySelector('.case-opening-container').style.display = 'block';
            document.querySelector('.case-details').style.display = 'none';
            
            // Generate items for animation
            const items = caseData.items;
            const itemsContainer = document.getElementById('case-items-container');
            
            // Create a long sequence of random items (with extra padding)
            const sequence = [];
            for (let i = 0; i < 50; i++) {
                const randomItem = items[Math.floor(Math.random() * items.length)];
                sequence.push(randomItem);
            }
            
            // The winning item (near the end)
            const winningItemIndex = 40;
            const winningItem = sequence[winningItemIndex] = items[Math.floor(Math.random() * items.length)];
            
            // Generate HTML
            itemsContainer.innerHTML = sequence.map(item => `
                <div class="case-item-card">
                    <div class="case-item-image">
                        <img src="${item.image}" alt="${item.name}">
                    </div>
                    <div class="case-item-info">
                        <div class="case-item-name">${item.name}</div>
                        <div class="case-item-weapon">${item.weapon}</div>
                        <div class="case-item-rarity rarity-${item.rarity}">${item.rarity}</div>
                    </div>
                </div>
            `).join('');
            
            // Start animation
            setTimeout(() => {
                const containerWidth = itemsContainer.scrollWidth;
                const cardWidth = 200; // width + margin
                const centerPosition = (window.innerWidth / 2) - (cardWidth / 2);
                const endPosition = -(cardWidth * winningItemIndex) + centerPosition;
                
                itemsContainer.style.left = endPosition + 'px';
                
                // Show result after animation
                setTimeout(() => {
                    document.getElementById('result-image').src = winningItem.image;
                    document.getElementById('result-name').textContent = winningItem.name;
                    document.getElementById('result-weapon').textContent = winningItem.weapon;
                    document.getElementById('result-rarity').className = 'case-item-rarity rarity-' + winningItem.rarity;
                    document.getElementById('result-rarity').textContent = winningItem.rarity;
                    document.getElementById('case-result').classList.add('active');
                    
                    // Add item to inventory
                    const inventory = user.inventory || [];
                    inventory.push({
                        id: Date.now(), // Simple unique ID
                        name: winningItem.name,
                        weapon: winningItem.weapon,
                        rarity: winningItem.rarity,
                        image: winningItem.image,
                        obtained: new Date().toISOString()
                    });
                    user.inventory = inventory;
                    localStorage.setItem('userData', JSON.stringify(user));
                }, 10000); // Animation duration
            }, 500);
        }
        
        function openAnotherCase() {
            window.location.reload();
        }
        
        function viewInventory() {
            const userData = localStorage.getItem('userData');
            if (userData) {
                const user = JSON.parse(userData);
                const steamId = user.steamId || 'me';
                window.location.href = '/id/' + steamId + '/inventory';
            }
        }
    `;
    document.body.appendChild(script);
}

// Load user inventory
function loadUserInventory(element, steamId) {
    document.title = 'Inventory - CSReforge';
    
    // In a real app, this would fetch from API
    const userData = localStorage.getItem('userData');
    let inventory = [];
    let points = 0;
    let name = 'User';
    let avatar = 'images/default-avatar.png';
    
    if (userData) {
        const user = JSON.parse(userData);
        inventory = user.inventory || [];
        points = user.points || 0;
        name = user.name || 'User';
        avatar = user.avatar || 'images/default-avatar.png';
    }
    
    element.innerHTML = `
        <div class="page-header">
            <h1>Inventory</h1>
            <div class="user-stats">
                <div class="user-avatar">
                    <img src="${avatar}" alt="${name}">
                </div>
                <div class="user-info">
                    <div class="user-name">${name}</div>
                    <div class="user-points"><span class="points-value">${points}</span> points</div>
                </div>
            </div>
        </div>
        
        <div class="inventory-tabs">
            <button class="tab-btn active" data-tab="all">All Items</button>
            <button class="tab-btn" data-tab="rifles">Rifles</button>
            <button class="tab-btn" data-tab="pistols">Pistols</button>
            <button class="tab-btn" data-tab="knives">Knives</button>
        </div>
        
        <div class="inventory-grid">
            ${inventory.length > 0 ? inventory.map(item => `
                <div class="inventory-item" data-type="${getWeaponType(item.weapon)}">
                    <div class="inventory-item-image" style="border-color: var(--rarity-${item.rarity})">
                        <img src="${item.image}" alt="${item.name}">
                    </div>
                    <div class="inventory-item-info">
                        <div class="inventory-item-name">${item.name}</div>
                        <div class="inventory-item-weapon">${item.weapon}</div>
                        <div class="inventory-item-rarity rarity-${item.rarity}">${item.rarity}</div>
                    </div>
                    <div class="inventory-item-actions">
                        <button class="btn small primary" onclick="equipSkin(${item.id})">Equip</button>
                        <button class="btn small secondary" onclick="craftSkin(${item.id})">Craft</button>
                    </div>
                </div>
            `).join('') : '<div class="empty-inventory">Your inventory is empty. Open cases to get skins!</div>'}
        </div>
    `;
    
    // Add script for inventory functionality
    const script = document.createElement('script');
    script.innerHTML = `
        // Set up tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                const tab = this.dataset.tab;
                const items = document.querySelectorAll('.inventory-item');
                
                if (tab === 'all') {
                    items.forEach(item => item.style.display = 'block');
                } else {
                    items.forEach(item => {
                        if (item.dataset.type === tab) {
                            item.style.display = 'block';
                        } else {
                            item.style.display = 'none';
                        }
                    });
                }
            });
        });
        
        function equipSkin(id) {
            alert('Skin equipped! It will be available next time you join the server.');
            // In a real app, this would be an API call
        }
        
        function craftSkin(id) {
            window.location.href = '/crafting?item=' + id;
        }
    `;
    document.body.appendChild(script);
}

// Load user profile
function loadUserProfile(element, steamId) {
    document.title = 'Profile - CSReforge';
    
    // In a real app, this would fetch from API
    const userData = localStorage.getItem('userData');
    let stats = {
        points: 0,
        casesOpened: 0,
        itemsCollected: 0,
        legendaryItems: 0,
        exoticItems: 0,
        joinDate: '2023-01-01'
    };
    let name = 'User';
    let avatar = 'images/default-avatar.png';
    
    if (userData) {
        const user = JSON.parse(userData);
        name = user.name || 'User';
        avatar = user.avatar || 'images/default-avatar.png';
        stats.points = user.points || 0;
        stats.casesOpened = user.casesOpened || 0;
        stats.itemsCollected = user.inventory ? user.inventory.length : 0;
        stats.legendaryItems = user.inventory ? user.inventory.filter(item => item.rarity === 'legendary').length : 0;
        stats.exoticItems = user.inventory ? user.inventory.filter(item => item.rarity === 'exotic').length : 0;
    }
    
    element.innerHTML = `
        <div class="profile-header">
            <div class="profile-avatar">
                <img src="${avatar}" alt="${name}">
            </div>
            <div class="profile-info">
                <h1 class="profile-name">${name}</h1>
                <div class="profile-steam-id">Steam ID: ${steamId}</div>
                <div class="profile-joined">Member since: ${formatDate(stats.joinDate)}</div>
            </div>
        </div>
        
        <div class="profile-nav">
            <a href="/id/${steamId}/profile" class="profile-nav-item active">Overview</a>
            <a href="/id/${steamId}/inventory" class="profile-nav-item">Inventory</a>
            <a href="/id/${steamId}/stats" class="profile-nav-item">Statistics</a>
            <a href="/id/${steamId}/settings" class="profile-nav-item">Settings</a>
        </div>
        
        <div class="profile-content">
            <div class="profile-stats">
                <div class="stats-card">
                    <div class="stats-value">${stats.points}</div>
                    <div class="stats-label">Current Points</div>
                </div>
                <div class="stats-card">
                    <div class="stats-value">${stats.casesOpened}</div>
                    <div class="stats-label">Cases Opened</div>
                </div>
                <div class="stats-card">
                    <div class="stats-value">${stats.itemsCollected}</div>
                    <div class="stats-label">Items Collected</div>
                </div>
                <div class="stats-card">
                    <div class="stats-value">${stats.legendaryItems}</div>
                    <div class="stats-label">Legendary Items</div>
                </div>
                <div class="stats-card">
                    <div class="stats-value">${stats.exoticItems}</div>
                    <div class="stats-label">Exotic Items</div>
                </div>
            </div>
            
            <div class="recent-activity">
                <h2>Recent Activity</h2>
                <div class="activity-list">
                    <div class="activity-item">
                        <div class="activity-icon case-open"></div>
                        <div class="activity-content">
                            <div class="activity-title">Opened Premium Case</div>
                            <div class="activity-description">Received AWP | Hyper Beast</div>
                            <div class="activity-time">2 hours ago</div>
                        </div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-icon points-earned"></div>
                        <div class="activity-content">
                            <div class="activity-title">Earned 120 Points</div>
                            <div class="activity-description">For MVP and defusing the bomb</div>
                            <div class="activity-time">Yesterday</div>
                        </div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-icon craft"></div>
                        <div class="activity-content">
                            <div class="activity-title">Crafted New Skin</div>
                            <div class="activity-description">Combined 3 items into Glock-18 | Water Elemental</div>
                            <div class="activity-time">3 days ago</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Load crafting page
function loadCrafting(element) {
    document.title = 'Crafting - CSReforge';
    
    element.innerHTML = `
        <div class="page-header">
            <h1>Skin Crafting</h1>
            <p>Combine multiple skins to create new ones</p>
        </div>
        
        <div class="crafting-container">
            <div class="crafting-slots">
                <div class="crafting-slot-row">
                    <div class="crafting-slot" data-slot="1">
                        <div class="crafting-slot-placeholder">
                            <div class="crafting-slot-plus">+</div>
                            <div>Add Item</div>
                        </div>
                    </div>
                    <div class="crafting-slot" data-slot="2">
                        <div class="crafting-slot-placeholder">
                            <div class="crafting-slot-plus">+</div>
                            <div>Add Item</div>
                        </div>
                    </div>
                </div>
                <div class="crafting-slot-row">
                    <div class="crafting-slot" data-slot="3">
                        <div class="crafting-slot-placeholder">
                            <div class="crafting-slot-plus">+</div>
                            <div>Add Item</div>
                        </div>
                    </div>
                    <div class="crafting-slot" data-slot="4">
                        <div class="crafting-slot-placeholder">
                            <div class="crafting-slot-plus">+</div>
                            <div>Add Item</div>
                        </div>
                    </div>
                </div>
                <div class="crafting-controls">
                    <button class="btn primary crafting-btn" disabled>Craft Item</button>
                    <button class="btn secondary crafting-clear-btn">Clear All</button>
                    <div class="crafting-info">
                        Add 3-5 items of the same rarity to craft an item of higher rarity
                    </div>
                </div>
            </div>
            
            <div class="crafting-inventory">
                <h3>Your Inventory</h3>
                <div class="inventory-filter">
                    <input type="text" placeholder="Search items..." class="inventory-search">
                    <select class="inventory-rarity-filter">
                        <option value="all">All Rarities</option>
                        <option value="common">Common</option>
                        <option value="uncommon">Uncommon</option>
                        <option value="rare">Rare</option>
                        <option value="mythical">Mythical</option>
                        <option value="legendary">Legendary</option>
                        <option value="ancient">Ancient</option>
                    </select>
                </div>
                <div class="crafting-inventory-grid">
                    <!-- This would be populated from the user's inventory -->
                    <div class="empty-inventory">Log in to see your inventory items</div>
                </div>
            </div>
        </div>
    `;
}

// Load leaderboard page
function loadLeaderboard(element) {
    document.title = 'Leaderboard - CSReforge';
    
    // In a real app, this would fetch from API
    const leaderboardData = [
        { rank: 1, name: 'Player1', points: 15420, avatar: 'images/avatars/avatar1.jpg', items: 32 },
        { rank: 2, name: 'XxSniperxX', points: 12850, avatar: 'images/avatars/avatar2.jpg', items: 28 },
        { rank: 3, name: 'HeadshotMaster', points: 11240, avatar: 'images/avatars/avatar3.jpg', items: 25 },
        { rank: 4, name: 'CSGOLegend', points: 10980, avatar: 'images/avatars/avatar4.jpg', items: 30 },
        { rank: 5, name: 'FragMachine', points: 9560, avatar: 'images/avatars/avatar5.jpg', items: 22 },
        { rank: 6, name: 'SkinCollector', points: 8970, avatar: 'images/avatars/avatar6.jpg', items: 40 },
        { rank: 7, name: 'Bombplanter', points: 7820, avatar: 'images/avatars/avatar7.jpg', items: 18 },
        { rank: 8, name: 'NoScope360', points: 6540, avatar: 'images/avatars/avatar8.jpg', items: 15 },
        { rank: 9, name: 'AimGod', points: 5930, avatar: 'images/avatars/avatar9.jpg', items: 14 },
        { rank: 10, name: 'RushBKing', points: 5280, avatar: 'images/avatars/avatar10.jpg', items: 12 }
    ];
    
    element.innerHTML = `
        <div class="page-header">
            <h1>Leaderboard</h1>
            <p>Top players ranked by points earned</p>
        </div>
        
        <div class="leaderboard-tabs">
            <button class="tab-btn active" data-tab="points">Points</button>
            <button class="tab-btn" data-tab="cases">Cases Opened</button>
            <button class="tab-btn" data-tab="items">Items Collected</button>
        </div>
        
        <div class="leaderboard-container">
            <div class="leaderboard-top">
                <div class="leaderboard-top-item second">
                    <div class="leaderboard-rank">2</div>
                    <div class="leaderboard-avatar">
                        <img src="${leaderboardData[1].avatar}" alt="${leaderboardData[1].name}">
                    </div>
                    <div class="leaderboard-name">${leaderboardData[1].name}</div>
                    <div class="leaderboard-points">${leaderboardData[1].points.toLocaleString()}</div>
                </div>
                <div class="leaderboard-top-item first">
                    <div class="leaderboard-rank">1</div>
                    <div class="leaderboard-avatar">
                        <img src="${leaderboardData[0].avatar}" alt="${leaderboardData[0].name}">
                    </div>
                    <div class="leaderboard-name">${leaderboardData[0].name}</div>
                    <div class="leaderboard-points">${leaderboardData[0].points.toLocaleString()}</div>
                </div>
                <div class="leaderboard-top-item third">
                    <div class="leaderboard-rank">3</div>
                    <div class="leaderboard-avatar">
                        <img src="${leaderboardData[2].avatar}" alt="${leaderboardData[2].name}">
                    </div>
                    <div class="leaderboard-name">${leaderboardData[2].name}</div>
                    <div class="leaderboard-points">${leaderboardData[2].points.toLocaleString()}</div>
                </div>
            </div>
            
            // Continuing from where we left off...
                <div class="leaderboard-table">
                    <div class="leaderboard-table-header">
                        <div class="leaderboard-cell rank-cell">Rank</div>
                        <div class="leaderboard-cell player-cell">Player</div>
                        <div class="leaderboard-cell points-cell">Points</div>
                        <div class="leaderboard-cell items-cell">Items</div>
                    </div>
                    ${leaderboardData.slice(3).map(player => `
                        <div class="leaderboard-table-row">
                            <div class="leaderboard-cell rank-cell">${player.rank}</div>
                            <div class="leaderboard-cell player-cell">
                                <div class="player-avatar">
                                    <img src="${player.avatar}" alt="${player.name}">
                                </div>
                                <div class="player-name">${player.name}</div>
                            </div>
                            <div class="leaderboard-cell points-cell">${player.points.toLocaleString()}</div>
                            <div class="leaderboard-cell items-cell">${player.items}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    // Add script for leaderboard functionality
    const script = document.createElement('script');
    script.innerHTML = `
        // Set up tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // In a real app, this would fetch different leaderboard data
                // For demo, we'll just show an alert
                alert('Switched to ' + this.dataset.tab + ' leaderboard');
            });
        });
    `;
    document.body.appendChild(script);
}

// Helper functions
function formatCaseName(slug) {
    return slug.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

function getWeaponType(weapon) {
    if (weapon.includes('AK-47') || weapon.includes('M4A4') || weapon.includes('M4A1-S') || weapon.includes('AWP') || weapon.includes('SSG 08')) {
        return 'rifles';
    } else if (weapon.includes('Knife') || weapon.includes('Bayonet') || weapon.includes('Karambit')) {
        return 'knives';
    } else if (weapon.includes('Glock') || weapon.includes('USP') || weapon.includes('Desert Eagle') || weapon.includes('P250')) {
        return 'pistols';
    } else {
        return 'other';
    }
}