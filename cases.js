let isSpinning = false;

document.addEventListener('DOMContentLoaded', function() {
    // Load cases when page loads
    loadCases();
    
    // Check user authentication and update UI
    checkAuthAndUpdateUI();
});

// Load cases from server
async function loadCases() {
    try {
        const response = await fetch('/api/cases');
        if (!response.ok) {
            throw new Error('Failed to load cases');
        }
        
        const cases = await response.json();
        displayCases(cases);
    } catch (error) {
        console.error('Error loading cases:', error);
        showError('Error loading cases. Please try again later.');
    }
}

// Display cases in the UI
function displayCases(cases) {
    const container = document.querySelector('.cases-container');
    if (!container) return;

    // Group cases by year
    const casesByYear = cases.reduce((acc, case_) => {
        if (!acc[case_.year]) {
            acc[case_.year] = [];
        }
        acc[case_.year].push(case_);
        return acc;
    }, {});

    // Sort years in descending order
    const years = Object.keys(casesByYear).sort((a, b) => b - a);

    container.innerHTML = '';
    
    years.forEach(year => {
        const yearSection = document.createElement('div');
        yearSection.className = 'year-section';
        yearSection.innerHTML = `<h2>${year}</h2>`;
        
        const casesGrid = document.createElement('div');
        casesGrid.className = 'cases-grid';
        
        casesByYear[year].forEach(case_ => {
            const caseElement = createCaseElement(case_);
            casesGrid.appendChild(caseElement);
        });
        
        yearSection.appendChild(casesGrid);
        container.appendChild(yearSection);
    });
}

// Create individual case element
function createCaseElement(case_) {
    const element = document.createElement('div');
    element.className = 'case-item';
    element.innerHTML = `
        <img src="${case_.image}" alt="${case_.name}">
        <h3>${case_.name}</h3>
        <p>${case_.description}</p>
        <button class="open-case-btn" data-case-id="${case_.id}" data-case-price="${case_.price}">
            Open Case (${case_.price} coins)
        </button>
    `;
    
    element.querySelector('.open-case-btn').addEventListener('click', function() {
        if (!isAuthenticated) {
            showError('Please login to open cases');
            return;
        }
        openCase(case_.id);
    });
    
    return element;
}

// Open case function
function openCase(caseId) {
    if (isSpinning) return;
    
    fetch(`/api/cases/open/${caseId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showError(data.error);
            return;
        }

        // Update coins immediately
        updateCoins(data.remainingCoins);
        
        // Show spinning animation
        showSpinningAnimation(data.rollItems, data.winningItem, data.winningPosition);
    })
    .catch(error => {
        console.error('Error opening case:', error);
        showError('An error occurred while opening the case');
    });
}

// Show spinning animation
function showSpinningAnimation(rollItems, winningItem, winningPosition) {
    isSpinning = true;

    // Create or get modal
    let modal = document.querySelector('.case-opening-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.className = 'case-opening-modal';
        document.body.appendChild(modal);
    }

    // Create roll container
    const rollContainer = document.createElement('div');
    rollContainer.className = 'roll-container';

    // Add items to roll
    rollItems.forEach((item, index) => {
        const itemElement = createRollItemElement(item);
        if (index === winningPosition) {
            itemElement.classList.add('winning-item');
        }
        rollContainer.appendChild(itemElement);
    });

    // Set up modal content
    modal.innerHTML = '';
    modal.appendChild(rollContainer);
    modal.style.display = 'flex';

    // Start spinning animation
    requestAnimationFrame(() => {
        rollContainer.style.transition = 'none';
        rollContainer.style.transform = 'translateX(0)';

        requestAnimationFrame(() => {
            const itemWidth = 200; // Width of item + margin
            const finalPosition = -(winningPosition * itemWidth) + (window.innerWidth / 2 - itemWidth / 2);
            
            rollContainer.style.transition = 'transform 5s cubic-bezier(0.15, 0.35, 0, 1)';
            rollContainer.style.transform = `translateX(${finalPosition}px)`;

            // Show winning item after animation
            setTimeout(() => {
                showWinningItem(winningItem);
                isSpinning = false;
                modal.style.display = 'none';
            }, 5000);
        });
    });
}

// Create roll item element
function createRollItemElement(item) {
    const element = document.createElement('div');
    element.className = `roll-item ${item.rarity}`;
    element.innerHTML = `
        <img src="${item.image}" alt="${item.name}">
        <div class="item-name">${item.name}</div>
    `;
    return element;
}

// Show winning item modal
function showWinningItem(item) {
    const modal = document.createElement('div');
    modal.className = 'winning-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>You received:</h2>
            <div class="winning-item ${item.rarity}">
                <img src="${item.image}" alt="${item.name}">
                <div class="item-name">${item.name}</div>
            </div>
            <button onclick="this.parentElement.parentElement.remove()">Close</button>
        </div>
    `;
    document.body.appendChild(modal);
}

// Update coins display
function updateCoins(newAmount) {
    const coinsElement = document.querySelector('.user-coins');
    if (coinsElement) {
        coinsElement.textContent = newAmount;
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

// Check authentication and update UI
async function checkAuthAndUpdateUI() {
    try {
        const response = await fetch('/api/user');
        const data = await response.json();
        
        isAuthenticated = data.authenticated;
        
        if (data.authenticated && data.user) {
            document.querySelectorAll('.open-case-btn').forEach(btn => {
                btn.disabled = false;
            });
        } else {
            document.querySelectorAll('.open-case-btn').forEach(btn => {
                btn.disabled = true;
            });
        }
    } catch (error) {
        console.error('Error checking authentication:', error);
    }
}