import asyncio
import json
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection details
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "csreforge")

# Initialize MongoDB client
client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

# Sample skins data
SKINS = [
    # Knives (Exotic)
    {"name": "Fade", "weapon": "Butterfly Knife", "rarity": "exotic", "image_url": "/images/skins/butterfly-fade.png"},
    {"name": "Doppler", "weapon": "Karambit", "rarity": "exotic", "image_url": "/images/skins/karambit-doppler.png"},
    {"name": "Marble Fade", "weapon": "M9 Bayonet", "rarity": "exotic", "image_url": "/images/skins/m9-marblefade.png"},
    {"name": "Tiger Tooth", "weapon": "Butterfly Knife", "rarity": "exotic", "image_url": "/images/skins/butterfly-tigertooth.png"},
    {"name": "Lore", "weapon": "Karambit", "rarity": "exotic", "image_url": "/images/skins/karambit-lore.png"},
    {"name": "Crimson Web", "weapon": "M9 Bayonet", "rarity": "exotic", "image_url": "/images/skins/m9-crimsonweb.png"},
    
    # Ancient Tier
    {"name": "Dragon Lore", "weapon": "AWP", "rarity": "ancient", "image_url": "/images/skins/awp-dragonlore.png"},
    {"name": "Asiimov", "weapon": "M4A4", "rarity": "ancient", "image_url": "/images/skins/m4a4-asiimov.png"},
    {"name": "Fire Serpent", "weapon": "AK-47", "rarity": "ancient", "image_url": "/images/skins/ak47-fireserpent.png"},
    {"name": "Howl", "weapon": "M4A4", "rarity": "ancient", "image_url": "/images/skins/m4a4-howl.png"},
    {"name": "Gungnir", "weapon": "AWP", "rarity": "ancient", "image_url": "/images/skins/awp-gungnir.png"},
    
    # Legendary Tier
    {"name": "Neo-Noir", "weapon": "USP-S", "rarity": "legendary", "image_url": "/images/skins/usp-neonoir.png"},
    {"name": "Hyper Beast", "weapon": "AWP", "rarity": "legendary", "image_url": "/images/skins/awp-hyperbeast.png"},
    {"name": "Printstream", "weapon": "Desert Eagle", "rarity": "legendary", "image_url": "/images/skins/deagle-printstream.png"},
    {"name": "Asiimov", "weapon": "AWP", "rarity": "legendary", "image_url": "/images/skins/awp-asiimov.png"},
    {"name": "Bloodsport", "weapon": "AK-47", "rarity": "legendary", "image_url": "/images/skins/ak47-bloodsport.png"},
    {"name": "Hyper Beast", "weapon": "M4A1-S", "rarity": "legendary", "image_url": "/images/skins/m4a1s-hyperbeast.png"},
    {"name": "Ocean Drive", "weapon": "Glock-18", "rarity": "legendary", "image_url": "/images/skins/glock-oceandrive.png"},
    
    # Mythical Tier
    {"name": "Bullet Rain", "weapon": "M4A4", "rarity": "mythical", "image_url": "/images/skins/m4a4-bulletrain.png"},
    {"name": "Redline", "weapon": "AK-47", "rarity": "mythical", "image_url": "/images/skins/ak47-redline.png"},
    {"name": "Neon Rider", "weapon": "MAC-10", "rarity": "mythical", "image_url": "/images/skins/mac10-neonrider.png"},
    {"name": "Water Elemental", "weapon": "Glock-18", "rarity": "mythical", "image_url": "/images/skins/glock-waterelemental.png"},
    {"name": "Asiimov", "weapon": "P90", "rarity": "mythical", "image_url": "/images/skins/p90-asiimov.png"},
    
    # Rare Tier
    {"name": "Decimator", "weapon": "M4A1-S", "rarity": "rare", "image_url": "/images/skins/m4a1s-decimator.png"},
    {"name": "Cyrex", "weapon": "M4A1-S", "rarity": "rare", "image_url": "/images/skins/m4a1s-cyrex.png"},
    {"name": "Frontside Misty", "weapon": "AK-47", "rarity": "rare", "image_url": "/images/skins/ak47-frontsidemisty.png"},
    {"name": "Atomic Alloy", "weapon": "M4A1-S", "rarity": "rare", "image_url": "/images/skins/m4a1s-atomicalloy.png"},
    {"name": "Copper Galaxy", "weapon": "Desert Eagle", "rarity": "rare", "image_url": "/images/skins/deagle-coppergalaxy.png"},
    {"name": "Conspiracy", "weapon": "USP-S", "rarity": "rare", "image_url": "/images/skins/usp-conspiracy.png"},
    
    # Uncommon Tier
    {"name": "Phobos", "weapon": "M4A1-S", "rarity": "uncommon", "image_url": "/images/skins/m4a1s-phobos.png"},
    {"name": "Worm God", "weapon": "AWP", "rarity": "uncommon", "image_url": "/images/skins/awp-wormgod.png"},
    {"name": "Wing Shot", "weapon": "USP-S", "rarity": "uncommon", "image_url": "/images/skins/usp-wingshot.png"},
    {"name": "Eco", "weapon": "Galil AR", "rarity": "uncommon", "image_url": "/images/skins/galil-eco.png"},
    {"name": "Evil Daimyo", "weapon": "M4A4", "rarity": "uncommon", "image_url": "/images/skins/m4a4-evildaimyo.png"},
    {"name": "Torque", "weapon": "SSG 08", "rarity": "uncommon", "image_url": "/images/skins/ssg08-torque.png"},
    
    # Common Tier
    {"name": "Urban Hazard", "weapon": "MP7", "rarity": "common", "image_url": "/images/skins/mp7-urbanhazard.png"},
    {"name": "Elite Build", "weapon": "AK-47", "rarity": "common", "image_url": "/images/skins/ak47-elitebuild.png"},
    {"name": "Basilisk", "weapon": "USP-S", "rarity": "common", "image_url": "/images/skins/usp-basilisk.png"},
]

# Sample cases data
CASES = [
    {
        "name": "Premium Case",
        "description": "The best case with the rarest skins. Try your luck!",
        "price": 1500,
        "image_url": "/images/cases/premium-case.png",
        "items": [
            # Items will be populated with skin IDs after skins are inserted
        ]
    },
    {
        "name": "Standard Case",
        "description": "A balanced case with good chances for quality skins.",
        "price": 800,
        "image_url": "/images/cases/standard-case.png",
        "items": []
    },
    {
        "name": "Knife Case",
        "description": "Exclusive knife skins case with high value items.",
        "price": 3000,
        "image_url": "/images/cases/knife-case.png",
        "items": []
    },
    {
        "name": "Starter Case",
        "description": "Perfect for beginners. Affordable and contains good starter skins.",
        "price": 300,
        "image_url": "/images/cases/starter-case.png",
        "items": []
    }
]

# Case items mapping
CASE_ITEMS_MAPPING = {
    "Premium Case": [
        {"weapon": "AWP", "name": "Dragon Lore", "drop_chance": 0.5},
        {"weapon": "M4A4", "name": "Howl", "drop_chance": 0.5},
        {"weapon": "Butterfly Knife", "name": "Fade", "drop_chance": 1.0},
        {"weapon": "M4A4", "name": "Asiimov", "drop_chance": 3.0},
        {"weapon": "AK-47", "name": "Fire Serpent", "drop_chance": 5.0},
        {"weapon": "AWP", "name": "Hyper Beast", "drop_chance": 7.0},
        {"weapon": "Desert Eagle", "name": "Printstream", "drop_chance": 8.0},
        {"weapon": "M4A4", "name": "Bullet Rain", "drop_chance": 15.0},
        {"weapon": "AK-47", "name": "Redline", "drop_chance": 20.0},
        {"weapon": "M4A1-S", "name": "Decimator", "drop_chance": 20.0},
        {"weapon": "M4A1-S", "name": "Cyrex", "drop_chance": 20.0},
    ],
    "Standard Case": [
        {"weapon": "AWP", "name": "Asiimov", "drop_chance": 2.0},
        {"weapon": "AK-47", "name": "Bloodsport", "drop_chance": 5.0},
        {"weapon": "M4A1-S", "name": "Cyrex", "drop_chance": 8.0},
        {"weapon": "M4A1-S", "name": "Hyper Beast", "drop_chance": 10.0},
        {"weapon": "MAC-10", "name": "Neon Rider", "drop_chance": 12.0},
        {"weapon": "Glock-18", "name": "Ocean Drive", "drop_chance": 12.0},
        {"weapon": "USP-S", "name": "Neo-Noir", "drop_chance": 13.0},
        {"weapon": "Glock-18", "name": "Water Elemental", "drop_chance": 13.0},
        {"weapon": "AK-47", "name": "Frontside Misty", "drop_chance": 15.0},
        {"weapon": "M4A1-S", "name": "Phobos", "drop_chance": 5.0},
        {"weapon": "AWP", "name": "Worm God", "drop_chance": 5.0},
    ],
    "Knife Case": [
        {"weapon": "Butterfly Knife", "name": "Fade", "drop_chance": 10.0},
        {"weapon": "Karambit", "name": "Doppler", "drop_chance": 10.0},
        {"weapon": "M9 Bayonet", "name": "Marble Fade", "drop_chance": 10.0},
        {"weapon": "Butterfly Knife", "name": "Tiger Tooth", "drop_chance": 10.0},
        {"weapon": "Karambit", "name": "Lore", "drop_chance": 10.0},
        {"weapon": "M9 Bayonet", "name": "Crimson Web", "drop_chance": 10.0},
        {"weapon": "AWP", "name": "Dragon Lore", "drop_chance": 10.0},
        {"weapon": "M4A4", "name": "Howl", "drop_chance": 10.0},
        {"weapon": "AWP", "name": "Gungnir", "drop_chance": 10.0},
        {"weapon": "AK-47", "name": "Fire Serpent", "drop_chance": 10.0},
    ],
    "Starter Case": [
        {"weapon": "P90", "name": "Asiimov", "drop_chance": 5.0},
        {"weapon": "M4A1-S", "name": "Phobos", "drop_chance": 10.0},
        {"weapon": "AWP", "name": "Worm God", "drop_chance": 10.0},
        {"weapon": "USP-S", "name": "Wing Shot", "drop_chance": 10.0},
        {"weapon": "Galil AR", "name": "Eco", "drop_chance": 10.0},
        {"weapon": "M4A4", "name": "Evil Daimyo", "drop_chance": 10.0},
        {"weapon": "SSG 08", "name": "Torque", "drop_chance": 10.0},
        {"weapon": "Desert Eagle", "name": "Copper Galaxy", "drop_chance": 5.0},
        {"weapon": "USP-S", "name": "Conspiracy", "drop_chance": 5.0},
        {"weapon": "MP7", "name": "Urban Hazard", "drop_chance": 15.0},
        {"weapon": "AK-47", "name": "Elite Build", "drop_chance": 5.0},
        {"weapon": "USP-S", "name": "Basilisk", "drop_chance": 5.0},
    ]
}

async def seed_database():
    print("Starting database seeding...")
    
    # Clear existing collections
    await db.skins.delete_many({})
    await db.cases.delete_many({})
    
    # Insert skins
    print("Inserting skins...")
    skin_map = {}  # For tracking skin IDs by weapon and name
    
    for skin in SKINS:
        result = await db.skins.insert_one(skin)
        key = f"{skin['weapon']}|{skin['name']}"
        skin_map[key] = result.inserted_id
    
    print(f"Inserted {len(SKINS)} skins")
    
    # Insert cases with items
    print("Inserting cases...")
    for case in CASES:
        case_name = case["name"]
        case_items = []
        
        if case_name in CASE_ITEMS_MAPPING:
            for item in CASE_ITEMS_MAPPING[case_name]:
                key = f"{item['weapon']}|{item['name']}"
                if key in skin_map:
                    case_items.append({
                        "skin_id": skin_map[key],
                        "drop_chance": item["drop_chance"]
                    })
        
        case["items"] = case_items
        await db.cases.insert_one(case)
    
    print(f"Inserted {len(CASES)} cases")
    print("Database seeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_database())