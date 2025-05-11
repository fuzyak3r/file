require('dotenv').config();
const express = require('express');
const session = require('express-session');
const passport = require('passport');
const SteamStrategy = require('passport-steam').Strategy;
const path = require('path');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const MongoClient = require('mongodb').MongoClient;
const MongoStore = require('connect-mongo');
const { ObjectId } = require('mongodb');

const app = express();
const PORT = process.env.PORT || 3000;

// MongoDB Connection
let db;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/csreforge';

// Database Initialization Function
async function initializeDatabase() {
    try {
        // Check collections existence
        const collections = await db.listCollections().toArray();
        const collectionNames = collections.map(c => c.name);
        
        // List of all required collections
        const requiredCollections = {
            'cases': 'Cases collection',
            'items': 'Items collection',
            'rarities': 'Rarities collection',
            'users': 'Users collection',
            'case_openings': 'Case openings collection',
            'sessions': 'Sessions collection'
        };

        // Create missing collections
        for (const [collectionName, description] of Object.entries(requiredCollections)) {
            if (!collectionNames.includes(collectionName)) {
                try {
                    if (collectionName === 'cases' || collectionName === 'items' || collectionName === 'rarities') {
                        console.error(`${description} not found! Please run the Python initialization script first.`);
                        return false;
                    } else {
                        // Create other required collections
                        await db.createCollection(collectionName);
                        
                        // Create indexes for new collections immediately
                        if (collectionName === 'case_openings') {
                            await db.collection(collectionName).createIndex({ userId: 1 });
                            await db.collection(collectionName).createIndex({ timestamp: 1 });
                        } else if (collectionName === 'users') {
                            await db.collection(collectionName).createIndex({ steamId: 1 }, { unique: true });
                        }
                        
                        console.log(`Created ${description}`);
                    }
                } catch (error) {
                    if (error.code !== 48) { // Ignore "collection already exists" error
                        console.error(`Error creating collection ${collectionName}:`, error);
                    }
                }
            }
        }

        // Check data existence for required collections
        const casesCount = await db.collection('cases').countDocuments();
        const itemsCount = await db.collection('items').countDocuments();
        const raritiesCount = await db.collection('rarities').countDocuments();

        if (casesCount === 0 || itemsCount === 0 || raritiesCount === 0) {
            console.error('Required collections are empty! Please run the Python initialization script first.');
            return false;
        }

        console.log(`Database check completed successfully:`);
        console.log(`- Cases: ${casesCount}`);
        console.log(`- Items: ${itemsCount}`);
        console.log(`- Rarities: ${raritiesCount}`);
        
        return true;
    } catch (error) {
        console.error('Error checking database:', error);
        return false;
    }
}

// Create Indexes Function
async function createIndexes() {
    try {
        const collections = ['users', 'cases', 'items', 'case_openings'];
        
        for (const collectionName of collections) {
            try {
                const collection = db.collection(collectionName);
                const existingIndexes = await collection.listIndexes().toArray();
                
                switch(collectionName) {
                    case 'users':
                        if (!existingIndexes.some(index => index.name === 'steamId_1')) {
                            await collection.createIndex({ steamId: 1 }, { unique: true });
                        }
                        break;
                    case 'cases':
                        if (!existingIndexes.some(index => index.name === 'id_1')) {
                            await collection.createIndex({ id: 1 });
                        }
                        break;
                    case 'items':
                        if (!existingIndexes.some(index => index.name === 'case_id_1')) {
                            await collection.createIndex({ case_id: 1 });
                        }
                        if (!existingIndexes.some(index => index.name === 'rarity_1')) {
                            await collection.createIndex({ rarity: 1 });
                        }
                        break;
                    case 'case_openings':
                        if (!existingIndexes.some(index => index.name === 'userId_1')) {
                            await collection.createIndex({ userId: 1 });
                        }
                        if (!existingIndexes.some(index => index.name === 'timestamp_1')) {
                            await collection.createIndex({ timestamp: 1 });
                        }
                        break;
                }
            } catch (error) {
                if (error.code === 26) { // NamespaceNotFound
                    await db.createCollection(collectionName);
                    console.log(`Created missing collection: ${collectionName}`);
                    const collection = db.collection(collectionName);
                    if (collectionName === 'case_openings') {
                        await collection.createIndex({ userId: 1 });
                        await collection.createIndex({ timestamp: 1 });
                    }
                } else {
                    console.error(`Error creating indexes for ${collectionName}:`, error);
                }
            }
        }
        console.log('Indexes checked and created successfully');
    } catch (error) {
        console.error('Error managing indexes:', error);
    }
}

// Database Integrity Check Function
async function checkDatabaseIntegrity() {
    try {
        // Check rarities
        const raritiesCount = await db.collection('rarities').countDocuments();
        if (raritiesCount === 0) {
            const defaultRarities = [
                { id: 'consumer', name: 'Consumer Grade', color: '#b0c3d9' },
                { id: 'industrial', name: 'Industrial Grade', color: '#5e98d9' },
                { id: 'mil_spec', name: 'Mil-Spec Grade', color: '#4b69ff' },
                { id: 'restricted', name: 'Restricted', color: '#8847ff' },
                { id: 'classified', name: 'Classified', color: '#d32ce6' },
                { id: 'covert', name: 'Covert', color: '#eb4b4b' },
                { id: 'rare_special', name: 'Rare Special', color: '#ffae39' }
            ];
            await db.collection('rarities').insertMany(defaultRarities);
            console.log('Default rarities created');
        }

        // Check and repair user data
        const users = await db.collection('users').find({}).toArray();
        for (const user of users) {
            const updates = {};
            
            if (!user.inventory) {
                updates.inventory = [];
            }
            
            if (!user.coins && user.coins !== 0) {
                updates.coins = 0;
            }
            
            if (user.inventory) {
                const fixedInventory = user.inventory
                    .filter(item => item && item.rarity)
                    .map(item => ({
                        ...item,
                        inventoryId: item.inventoryId || `inv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
                    }));
                
                if (fixedInventory.length !== user.inventory.length) {
                    updates.inventory = fixedInventory;
                }
            }
            
            if (Object.keys(updates).length > 0) {
                await db.collection('users').updateOne(
                    { steamId: user.steamId },
                    { $set: updates }
                );
            }
        }
        
        console.log('Database integrity check completed');
    } catch (error) {
        console.error('Error during database integrity check:', error);
    }
}

// MongoDB Connection and App Initialization
MongoClient.connect(MONGO_URI, { useUnifiedTopology: true })
    .then(async client => {
        console.log('Connected to MongoDB');
        db = client.db();
        
        try {
            // Initialize database first
            const dbInitSuccess = await initializeDatabase();
            if (!dbInitSuccess) {
                console.error('Database initialization failed. Please run the Python initialization script first.');
                process.exit(1);
            }

            // Now initialize indexes and check integrity
            await Promise.all([
                createIndexes(),
                checkDatabaseIntegrity()
            ]);

            // Start the application
            initializeApp();
        } catch (error) {
            console.error('Error during initialization:', error);
            process.exit(1);
        }
    })
    .catch(error => {
        console.error('MongoDB connection error:', error);
        process.exit(1);
    });

// Application initialization function
function initializeApp() {
    // Security middleware
    app.use(helmet({
        contentSecurityPolicy: {
            directives: {
                defaultSrc: ["'self'"],
                scriptSrc: ["'self'", "'unsafe-inline'", "cdnjs.cloudflare.com"],
                styleSrc: ["'self'", "'unsafe-inline'", "cdnjs.cloudflare.com", "fonts.googleapis.com"],
                fontSrc: ["'self'", "fonts.gstatic.com", "cdnjs.cloudflare.com"],
                imgSrc: ["'self'", "data:", "steamcdn-a.akamaihd.net", "avatars.steamstatic.com", "*.steamusercontent.com"],
                connectSrc: ["'self'"],
                mediaSrc: ["'self'", "remo.uk.to"],
            }
        }
    }));

    // Rate limiting
    app.use('/auth/', rateLimit({
        windowMs: 15 * 60 * 1000,
        max: 100,
        standardHeaders: true,
        legacyHeaders: false,
    }));

    app.use('/api/cases/open', rateLimit({
        windowMs: 1 * 60 * 1000,
        max: 5,
        standardHeaders: true,
        legacyHeaders: false,
    }));

    // Session configuration
    app.use(session({
        secret: process.env.SESSION_SECRET || 'your-secret-key',
        name: 'reforge_session',
        resave: false,
        saveUninitialized: false,
        store: MongoStore.create({
            mongoUrl: MONGO_URI,
            collectionName: 'sessions'
        }),
        cookie: {
            secure: process.env.NODE_ENV === 'production',
            httpOnly: true,
            maxAge: 7 * 24 * 60 * 60 * 1000
        }
    }));

    // Passport initialization
    app.use(passport.initialize());
    app.use(passport.session());

    // Body parsing
    app.use(express.json());
    app.use(express.urlencoded({ extended: true }));

    // Steam authentication strategy
    passport.use(new SteamStrategy({
        returnURL: `${process.env.BASE_URL || 'http://localhost:3000'}/auth/steam/return`,
        realm: process.env.BASE_URL || 'http://localhost:3000',
        apiKey: process.env.STEAM_API_KEY
    },
    async function(identifier, profile, done) {
        try {
            const userData = {
                steamId: profile.id,
                displayName: profile.displayName,
                photos: profile.photos,
                profileUrl: profile._json.profileurl,
                lastLogin: new Date()
            };

            const user = await db.collection('users').findOneAndUpdate(
                { steamId: profile.id },
                { 
                    $set: {
                        displayName: profile.displayName,
                        photos: profile.photos,
                        profileUrl: profile._json.profileurl,
                        lastLogin: new Date()
                    },
                    $setOnInsert: { coins: 1000, inventory: [] }
                },
                { upsert: true, returnDocument: 'after' }
            );

            return done(null, userData);
        } catch (error) {
            console.error('Error during auth:', error);
            return done(error);
        }
    }));

    // Passport serialization
    passport.serializeUser((user, done) => {
        done(null, user.steamId);
    });

    passport.deserializeUser(async (steamId, done) => {
        try {
            const user = await db.collection('users').findOne({ steamId });
            done(null, user);
        } catch (error) {
            done(error);
        }
    });

    // Static files
    app.use(express.static(path.join(__dirname, '/')));

    // Authentication middleware
    function isAuthenticated(req, res, next) {
        if (req.isAuthenticated()) {
            return next();
        }
        res.redirect('/');
    }

    // Routes
    // Authentication routes
    app.get('/auth/steam', passport.authenticate('steam'));

    app.get('/auth/steam/return',
        passport.authenticate('steam', { failureRedirect: '/' }),
        (req, res) => {
            res.redirect('/');
        }
    );

    app.get('/auth/logout', (req, res) => {
        req.logout(function(err) {
            if (err) { return next(err); }
            res.redirect('/');
        });
    });

    // Page routes
    app.get('/profile', isAuthenticated, (req, res) => {
        res.sendFile(path.join(__dirname, 'profile.html'));
    });

    app.get('/cases', (req, res) => {
        res.sendFile(path.join(__dirname, 'cases.html'));
    });

    app.get('/inventory', isAuthenticated, (req, res) => {
        res.sendFile(path.join(__dirname, 'inventory.html'));
    });

    // API Routes
    app.get('/api/user', (req, res) => {
        if (req.isAuthenticated()) {
            res.json({
                authenticated: true,
                user: {
                    id: req.user.steamId,
                    displayName: req.user.displayName,
                    photos: req.user.photos,
                    profileUrl: req.user.profileUrl,
                    coins: req.user.coins || 0
                }
            });
        } else {
            res.json({
                authenticated: false
            });
        }
    });

    // Добавляем новый API маршрут для профиля
    app.get('/api/profile', isAuthenticated, async (req, res) => {
        try {
            const userId = req.user.steamId;
            const user = await db.collection('users').findOne({ steamId: userId });
            
            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }
            
            // Получаем данные о редкости предметов
            const rarities = await db.collection('rarities').find({}).toArray();
            if (!rarities || rarities.length === 0) {
                return res.status(500).json({ error: 'Rarity data not found' });
            }
            
            const raritiesMap = {};
            rarities.forEach(rarity => {
                if (rarity && rarity.id) {
                    raritiesMap[rarity.id] = rarity;
                }
            });
            
            // Формируем инвентарь с проверкой на null и undefined
            const inventory = user.inventory || [];
            
            // Проверяем каждый предмет на наличие свойства rarity
            const validInventory = inventory.filter(item => item && item.rarity);
            
            // Группируем предметы по редкости
            const byRarity = {};
            validInventory.forEach(item => {
                if (!byRarity[item.rarity]) {
                    byRarity[item.rarity] = [];
                }
                byRarity[item.rarity].push(item);
            });
            
            // Получаем статистику открытия кейсов
            const caseOpenings = await db.collection('case_openings')
                .countDocuments({ userId: userId });
            
            res.json({
                user: {
                    steamId: user.steamId,
                    displayName: user.displayName,
                    photos: user.photos || [],
                    profileUrl: user.profileUrl,
                    coins: user.coins || 0,
                    lastLogin: user.lastLogin || new Date()
                },
                stats: {
                    totalCasesOpened: caseOpenings
                },
                inventory: {
                    total: validInventory.length,
                    byRarity: byRarity
                },
                rarities: raritiesMap
            });
        } catch (error) {
            console.error('Error fetching profile data:', error);
            res.status(500).json({ error: 'Internal server error while fetching profile data' });
        }
    });

    // Get all cases
    app.get('/api/cases', async (req, res) => {
        try {
            const cases = await db.collection('cases').find({}).toArray();
            if (!cases || cases.length === 0) {
                return res.status(404).json({ error: 'No cases found in database' });
            }
            res.json(cases);
        } catch (error) {
            console.error('Error fetching cases:', error);
            res.status(500).json({ error: 'Internal server error while fetching cases' });
        }
    });

    // Get case details
    app.get('/api/cases/:caseId', async (req, res) => {
        try {
            const { caseId } = req.params;
            const caseData = await db.collection('cases').findOne({ id: caseId });
            
            if (!caseData) {
                return res.status(404).json({ error: 'Case not found' });
            }
            
            const items = await db.collection('items').find({ case_id: caseId }).toArray();
            if (!items || items.length === 0) {
                return res.status(404).json({ error: 'No items found in this case' });
            }
            
            const rarities = await db.collection('rarities').find({}).toArray();
            if (!rarities || rarities.length === 0) {
                return res.status(500).json({ error: 'Rarity data not found' });
            }
            
            const raritiesMap = {};
            rarities.forEach(rarity => {
                if (rarity && rarity.id) {
                    raritiesMap[rarity.id] = rarity;
                }
            });
            
            const itemsByRarity = {};
            items.forEach(item => {
                if (item && item.rarity) {
                    if (!itemsByRarity[item.rarity]) {
                        itemsByRarity[item.rarity] = [];
                    }
                    itemsByRarity[item.rarity].push(item);
                }
            });
            
            res.json({
                ...caseData,
                items: itemsByRarity,
                rarities: raritiesMap
            });
        } catch (error) {
            console.error('Error fetching case details:', error);
            res.status(500).json({ error: 'Internal server error' });
        }
    });

    // Исправленный маршрут для открытия кейса
    app.post('/api/cases/open/:caseId', isAuthenticated, async (req, res) => {
    try {
        const { caseId } = req.params;
        if (!caseId) {
            return res.status(400).json({ error: 'Case ID is required' });
        }
        
        const userId = req.user.steamId;
        
        const caseData = await db.collection('cases').findOne({ id: caseId });
        if (!caseData) {
            return res.status(404).json({ error: 'Case not found' });
        }
        
        const user = await db.collection('users').findOne({ steamId: userId });
        if (!user || user.coins < caseData.price) {
            return res.status(400).json({ error: 'Not enough coins' });
        }
        
        const items = await db.collection('items').find({ case_id: caseId }).toArray();
        if (!items || items.length === 0) {
            return res.status(404).json({ error: 'No items found in this case' });
        }
        
        // Rarity probabilities
        const rarityProbabilities = {
            rare_special: 0.01,
            covert: 0.04,
            classified: 0.10,
            restricted: 0.20,
            mil_spec: 0.65
        };
        
        // Select rarity
        const random = Math.random();
        let selectedRarity = 'mil_spec'; // Default
        let cumulativeProbability = 0;
        
        for (const [rarity, probability] of Object.entries(rarityProbabilities)) {
            cumulativeProbability += probability;
            if (random <= cumulativeProbability) {
                selectedRarity = rarity;
                break;
            }
        }
        
        // Проверяем наличие предметов с выбранной редкостью
        let validItems = items.filter(item => item && typeof item === 'object' && item.rarity === selectedRarity);
        
        // Если не нашли предметы с выбранной редкостью, берем mil_spec или любые доступные
        if (!validItems || validItems.length === 0) {
            validItems = items.filter(item => item && typeof item === 'object' && item.rarity === 'mil_spec');
            
            // Если всё еще нет предметов, берем любые валидные предметы
            if (!validItems || validItems.length === 0) {
                validItems = items.filter(item => item && typeof item === 'object' && item.rarity);
                
                // Если вообще нет валидных предметов, ошибка
                if (!validItems || validItems.length === 0) {
                    return res.status(500).json({ error: 'No valid items found in this case' });
                }
            }
        }
        
        // Выбираем случайный предмет из валидных
        const selectedItem = validItems[Math.floor(Math.random() * validItems.length)];
        
        // Create unique item copy for inventory
        if (!selectedItem || typeof selectedItem !== 'object') {
            return res.status(500).json({ error: 'Selected item is invalid' });
        }
        
        const itemForInventory = {
            ...selectedItem,
            inventoryId: `${selectedItem.id}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        };
        
        // Создаем массив предметов для прокрутки, гарантируя, что выигрышный предмет
        // будет именно тем, который сохраняется в инвентарь
        const rollItems = [];
        const totalRollItems = 100; // Количество предметов в прокрутке
        const winningPosition = 80; // Позиция, где появится выигрышный предмет
        
        for (let i = 0; i < totalRollItems; i++) {
            if (i === winningPosition) {
                // ВАЖНО: Используем тот же самый выбранный предмет, который будет добавлен в инвентарь
                rollItems.push(selectedItem);
            } else {
                // Для остальных позиций генерируем случайные предметы
                const randomRarity = Math.random();
                let itemRarity = 'mil_spec';
                let cumulative = 0;
                
                for (const [rarity, probability] of Object.entries(rarityProbabilities)) {
                    cumulative += probability;
                    if (randomRarity <= cumulative) {
                        itemRarity = rarity;
                        break;
                    }
                }
                
                // Фильтруем валидные предметы выбранной редкости
                const itemsOfRarity = items.filter(
                    item => item && typeof item === 'object' && item.rarity === itemRarity
                );
                
                let randomItem;
                
                if (itemsOfRarity && itemsOfRarity.length > 0) {
                    randomItem = itemsOfRarity[Math.floor(Math.random() * itemsOfRarity.length)];
                } else {
                    // Если нет предметов такой редкости, берем любой валидный
                    const allValidItems = items.filter(
                        item => item && typeof item === 'object' && item.rarity
                    );
                    
                    if (allValidItems && allValidItems.length > 0) {
                        randomItem = allValidItems[Math.floor(Math.random() * allValidItems.length)];
                    } else {
                        // Если нет валидных предметов, используем выбранный предмет
                        randomItem = selectedItem;
                    }
                }
                
                rollItems.push(randomItem);
            }
        }
        
        // Update user inventory and balance
        await db.collection('users').updateOne(
            { steamId: userId },
            { 
                $push: { inventory: itemForInventory },
                $inc: { coins: -caseData.price }
            }
        );
        
        // Record case opening
        await db.collection('case_openings').insertOne({
            userId,
            caseId,
            itemId: selectedItem.id,
            inventoryId: itemForInventory.inventoryId,
            timestamp: new Date()
        });
        
        // Send response with roll items and выигрышным предметом
        res.json({
            success: true,
            rollItems: rollItems,
            // Важно: используем то же имя поля, которое ожидает клиент (cases.html)
            item: itemForInventory,
            winningPosition: winningPosition,
            remainingCoins: user.coins - caseData.price
        });
    } catch (error) {
        console.error('Error opening case:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

    // Get user inventory
    app.get('/api/inventory', isAuthenticated, async (req, res) => {
        try {
            const userId = req.user.steamId;
            const user = await db.collection('users').findOne({ steamId: userId });
            
            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }
            
            const rarities = await db.collection('rarities').find({}).toArray();
            if (!rarities || rarities.length === 0) {
                return res.status(500).json({ error: 'Rarity data not found' });
            }

            const raritiesMap = {};
            rarities.forEach(rarity => {
                if (rarity && rarity.id) {
                    raritiesMap[rarity.id] = rarity;
                }
            });
            
            const inventory = user.inventory || [];
            const inventoryWithRarities = inventory
                .filter(item => item && item.rarity)
                .map(item => ({
                    ...item,
                    rarityInfo: raritiesMap[item.rarity] || null
                }));
            
            res.json({ 
                inventory: inventoryWithRarities,
                coins: user.coins || 0
            });
        } catch (error) {
            console.error('Error fetching inventory:', error);
            res.status(500).json({ error: 'Internal server error while fetching inventory' });
        }
    });

    // Error handlers
    app.use((req, res) => {
        res.status(404).sendFile(path.join(__dirname, '404.html'));
    });

    app.use((err, req, res, next) => {
        console.error('Error occurred:', err);
        res.status(500).json({
            error: 'Internal server error',
            message: process.env.NODE_ENV === 'development' ? err.message : undefined
        });
    });

    // Handle unhandled rejections
    process.on('unhandledRejection', (reason, promise) => {
        console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    });

    // Start server
    app.listen(PORT, () => {
        console.log(`Server is running on port ${PORT}`);
    });
}