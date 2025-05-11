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

const app = express();
const PORT = process.env.PORT || 3000;

// MongoDB Connection
let db;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/csreforge';

MongoClient.connect(MONGO_URI, { useUnifiedTopology: true })
  .then(client => {
    console.log('Connected to MongoDB');
    db = client.db();
    
    // Initialize app after database connection
    initializeApp();
  })
  .catch(error => {
    console.error('MongoDB connection error:', error);
    process.exit(1);
  });

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
  const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    standardHeaders: true,
    legacyHeaders: false,
  });

  app.use('/auth/', limiter);
  app.use('/api/cases/open', rateLimit({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 5, // Limit each IP to 5 case opens per minute
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
      maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
    }
  }));

  // Initialize Passport
  app.use(passport.initialize());
  app.use(passport.session());

  // JSON parsing
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Steam Strategy configuration
  passport.use(new SteamStrategy({
      returnURL: `${process.env.BASE_URL || 'http://localhost:3000'}/auth/steam/return`,
      realm: process.env.BASE_URL || 'http://localhost:3000',
      apiKey: process.env.STEAM_API_KEY
    },
    async function(identifier, profile, done) {
      try {
        // User data to store
        const userData = {
          steamId: profile.id,
          displayName: profile.displayName,
          photos: profile.photos,
          profileUrl: profile._json.profileurl,
          lastLogin: new Date(),
          coins: 1000, // Starting coins for new users
        };

        // Check if user exists and update or create
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
    }
  ));

  // Serialize user into session
  passport.serializeUser((user, done) => {
    done(null, user.steamId);
  });

  // Deserialize user from session
  passport.deserializeUser(async (steamId, done) => {
    try {
      const user = await db.collection('users').findOne({ steamId });
      done(null, user);
    } catch (error) {
      done(error);
    }
  });

  // Serve static files
  app.use(express.static(path.join(__dirname, '/')));

  // Create folder for case images if it doesn't exist
  const fs = require('fs');
  const casesDir = path.join(__dirname, 'images/cases');
  const skinsDir = path.join(__dirname, 'images/skins');
  
  if (!fs.existsSync(casesDir)) {
    fs.mkdirSync(casesDir, { recursive: true });
  }
  
  if (!fs.existsSync(skinsDir)) {
    fs.mkdirSync(skinsDir, { recursive: true });
  }

  // Check if user is authenticated
  function isAuthenticated(req, res, next) {
    if (req.isAuthenticated()) {
      return next();
    }
    res.redirect('/');
  }

  // Steam auth routes
  app.get('/auth/steam', passport.authenticate('steam'));

  app.get('/auth/steam/return',
    passport.authenticate('steam', { failureRedirect: '/' }),
    (req, res) => {
      res.redirect('/');
    }
  );

  // Logout route
  app.get('/auth/logout', (req, res) => {
    req.logout(function(err) {
      if (err) { return next(err); }
      res.redirect('/');
    });
  });

  // User profile route
  app.get('/profile', isAuthenticated, (req, res) => {
    res.sendFile(path.join(__dirname, 'profile.html'));
  });

  // Cases page route
  app.get('/cases', (req, res) => {
    res.sendFile(path.join(__dirname, 'cases.html'));
  });

  // Inventory page route
  app.get('/inventory', isAuthenticated, (req, res) => {
    res.sendFile(path.join(__dirname, 'inventory.html'));
  });

  // API routes
  
  // Get user data
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

  // Get all cases
  app.get('/api/cases', async (req, res) => {
    try {
      const cases = await db.collection('cases').find({}).toArray();
      res.json(cases);
    } catch (error) {
      console.error('Error fetching cases:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // Get cases by year
  app.get('/api/cases/year/:year', async (req, res) => {
    try {
      const { year } = req.params;
      const cases = await db.collection('cases').find({ year }).toArray();
      res.json(cases);
    } catch (error) {
      console.error('Error fetching cases by year:', error);
      res.status(500).json({ error: 'Internal server error' });
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
      
      // Group items by rarity
      const rarities = await db.collection('rarities').find({}).toArray();
      const raritiesMap = {};
      rarities.forEach(rarity => {
        raritiesMap[rarity.id] = rarity;
      });
      
      const itemsByRarity = {};
      items.forEach(item => {
        if (!itemsByRarity[item.rarity]) {
          itemsByRarity[item.rarity] = [];
        }
        itemsByRarity[item.rarity].push(item);
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

  // Open a case
  app.post('/api/cases/open/:caseId', isAuthenticated, async (req, res) => {
    try {
      const { caseId } = req.params;
      const userId = req.user.steamId;
      
      // Find the case
      const caseData = await db.collection('cases').findOne({ id: caseId });
      if (!caseData) {
        return res.status(404).json({ error: 'Case not found' });
      }
      
      // Check if user has enough coins
      const user = await db.collection('users').findOne({ steamId: userId });
      if (user.coins < caseData.price) {
        return res.status(400).json({ error: 'Not enough coins' });
      }
      
      // Get all items from the case
      const items = await db.collection('items').find({ case_id: caseId }).toArray();
      if (items.length === 0) {
        return res.status(404).json({ error: 'No items found in this case' });
      }
      
      // Calculate probabilities based on rarity
      // Rare special: 1%, Covert: 4%, Classified: 10%, Restricted: 20%, Mil-spec: 65%
      const rarityProbabilities = {
        rare_special: 0.01,
        covert: 0.04,
        classified: 0.10,
        restricted: 0.20,
        mil_spec: 0.65,
        industrial: 0, // Included for completeness but not used in cases
        consumer: 0, // Included for completeness but not used in cases
      };
      
      // Determine the rarity based on probability
      const random = Math.random();
      let selectedRarity;
      let cumulativeProbability = 0;
      
      for (const [rarity, probability] of Object.entries(rarityProbabilities)) {
        cumulativeProbability += probability;
        if (random <= cumulativeProbability) {
          selectedRarity = rarity;
          break;
        }
      }
      
      // Filter items by the selected rarity
      const itemsOfSelectedRarity = items.filter(item => item.rarity === selectedRarity);
      
      // If no items of this rarity, fall back to mil-spec
      const availableItems = itemsOfSelectedRarity.length > 0 ? itemsOfSelectedRarity : items.filter(item => item.rarity === 'mil_spec');
      
      // Select a random item from the available items
      const selectedItem = availableItems[Math.floor(Math.random() * availableItems.length)];
      
      // Add the item to the user's inventory and deduct coins
      await db.collection('users').updateOne(
        { steamId: userId },
        { 
          $push: { inventory: selectedItem },
          $inc: { coins: -caseData.price }
        }
      );
      
      // Record the case opening history
      await db.collection('case_openings').insertOne({
        userId,
        caseId,
        itemId: selectedItem.id,
        timestamp: new Date()
      });
      
      res.json({
        success: true,
        item: selectedItem,
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
      
      if (!user || !user.inventory) {
        return res.json({ inventory: [] });
      }
      
      // Get rarities for each item
      const rarities = await db.collection('rarities').find({}).toArray();
      const raritiesMap = {};
      rarities.forEach(rarity => {
        raritiesMap[rarity.id] = rarity;
      });
      
      // Add rarity info to each item
      const inventoryWithRarities = user.inventory.map(item => ({
        ...item,
        rarityInfo: raritiesMap[item.rarity]
      }));
      
      res.json({ 
        inventory: inventoryWithRarities,
        coins: user.coins
      });
    } catch (error) {
      console.error('Error fetching inventory:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // Get user profile data for profile page
  app.get('/api/profile', isAuthenticated, async (req, res) => {
    try {
      const userId = req.user.steamId;
      
      // Get user data
      const user = await db.collection('users').findOne({ steamId: userId });
      
      // Get case opening statistics
      const openings = await db.collection('case_openings').find({ userId }).toArray();
      
      // Count openings by case type
      const caseOpeningStats = {};
      for (const opening of openings) {
        caseOpeningStats[opening.caseId] = (caseOpeningStats[opening.caseId] || 0) + 1;
      }
      
      // Get rarities for inventory display
      const rarities = await db.collection('rarities').find({}).toArray();
      const raritiesMap = {};
      rarities.forEach(rarity => {
        raritiesMap[rarity.id] = rarity;
      });
      
      // Prepare inventory for display
      const inventory = user.inventory || [];
      const inventoryByRarity = {};
      
      inventory.forEach(item => {
        if (!inventoryByRarity[item.rarity]) {
          inventoryByRarity[item.rarity] = [];
        }
        inventoryByRarity[item.rarity].push(item);
      });
      
      res.json({
        user: {
          id: user.steamId,
          displayName: user.displayName,
          photos: user.photos,
          profileUrl: user.profileUrl,
          coins: user.coins,
          lastLogin: user.lastLogin
        },
        stats: {
          totalCasesOpened: openings.length,
          caseOpeningStats
        },
        inventory: {
          total: inventory.length,
          byRarity: inventoryByRarity
        },
        rarities: raritiesMap
      });
    } catch (error) {
      console.error('Error fetching profile data:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // Handle 404
  app.use((req, res) => {
    res.status(404).sendFile(path.join(__dirname, '404.html'));
  });

  // Start server
  app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
  });
}