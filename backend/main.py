import os
import uuid
import random
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
import secrets
import json

# Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "csreforge")
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))

# Initialize FastAPI app
app = FastAPI(title="CSReforge API", description="Backend API for CS:GO skin economy system")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

# Model definitions
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class SkinBase(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    weapon: str
    rarity: str
    image_url: str
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SkinCreate(BaseModel):
    name: str
    weapon: str
    rarity: str
    image_url: str

class Skin(SkinBase):
    pass

class CaseItemBase(BaseModel):
    skin_id: PyObjectId = Field(..., alias="skin_id")
    drop_chance: float
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CaseItem(CaseItemBase):
    pass

class CaseBase(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    price: int
    image_url: str
    items: List[CaseItem] = []
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CaseCreate(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    items: List[CaseItem] = []

class Case(CaseBase):
    pass

class UserSkinBase(BaseModel):
    skin_id: str
    obtained_at: datetime = Field(default_factory=datetime.utcnow)
    equipped: bool = False
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class UserSkin(UserSkinBase):
    pass

class UserBase(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    steam_id: str = Field(..., description="Steam ID of the user")
    name: str
    avatar: str
    points: int = 0
    inventory: List[UserSkin] = []
    cases_opened: int = 0
    join_date: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(BaseModel):
    steam_id: str
    name: str
    avatar: str

class User(UserBase):
    pass

class PointsTransaction(BaseModel):
    user_id: str
    amount: int
    reason: str
    
class CaseOpenRequest(BaseModel):
    user_id: str
    case_id: str

class CaseOpenResult(BaseModel):
    success: bool
    skin: Optional[Skin] = None
    message: str = ""
    points_remaining: int = 0

# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # In a real app, validate the token and retrieve user
    # For demo, we'll just check if the token is valid
    user = await db.users.find_one({"_id": ObjectId(token)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# API Routes
@app.get("/")
async def root():
    return {"message": "Welcome to CSReforge API"}

# User routes
@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"steam_id": user.steam_id})
    if existing_user:
        # Update existing user
        await db.users.update_one(
            {"steam_id": user.steam_id},
            {"$set": {"name": user.name, "avatar": user.avatar}}
        )
        updated_user = await db.users.find_one({"steam_id": user.steam_id})
        return updated_user
    
    # Create new user
    new_user = User(
        steam_id=user.steam_id,
        name=user.name,
        avatar=user.avatar,
        points=500,  # Starting points
        inventory=[],
        cases_opened=0,
        join_date=datetime.utcnow()
    )
    result = await db.users.insert_one(new_user.dict(by_alias=True))
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return created_user

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    if len(user_id) == 24:  # MongoDB ObjectId
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    else:  # Steam ID
        user = await db.users.find_one({"steam_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/{user_id}/inventory", response_model=List[Skin])
async def get_user_inventory(user_id: str):
    # Get user
    if len(user_id) == 24:  # MongoDB ObjectId
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    else:  # Steam ID
        user = await db.users.find_one({"steam_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all skins in user's inventory
    inventory = []
    for item in user.get("inventory", []):
        skin = await db.skins.find_one({"_id": ObjectId(item["skin_id"])})
        if skin:
            skin["equipped"] = item.get("equipped", False)
            skin["obtained_at"] = item.get("obtained_at", datetime.utcnow())
            inventory.append(skin)
    
    return inventory

@app.post("/users/points/add")
async def add_points(transaction: PointsTransaction):
    # Add points to user
    if ObjectId.is_valid(transaction.user_id):
        result = await db.users.update_one(
            {"_id": ObjectId(transaction.user_id)},
            {"$inc": {"points": transaction.amount}}
        )
    else:
        result = await db.users.update_one(
            {"steam_id": transaction.user_id},
            {"$inc": {"points": transaction.amount}}
        )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return updated user
    if ObjectId.is_valid(transaction.user_id):
        user = await db.users.find_one({"_id": ObjectId(transaction.user_id)})
    else:
        user = await db.users.find_one({"steam_id": transaction.user_id})
    
    return {
        "success": True,
        "points": user["points"],
        "transaction": {
            "amount": transaction.amount,
            "reason": transaction.reason,
            "timestamp": datetime.utcnow()
        }
    }

# Case routes
@app.post("/cases/", response_model=Case)
async def create_case(case: CaseCreate):
    # Create new case
    new_case = case.dict(by_alias=True)
    result = await db.cases.insert_one(new_case)
    created_case = await db.cases.find_one({"_id": result.inserted_id})
    return created_case

@app.get("/cases/", response_model=List[Case])
async def get_cases():
    cases = await db.cases.find().to_list(length=100)
    return cases

@app.get("/cases/{case_id}", response_model=Case)
async def get_case(case_id: str):
    case = await db.cases.find_one({"_id": ObjectId(case_id)})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.post("/cases/open", response_model=CaseOpenResult)
async def open_case(request: CaseOpenRequest):
    # Get user and case
    user = None
    if ObjectId.is_valid(request.user_id):
        user = await db.users.find_one({"_id": ObjectId(request.user_id)})
    else:
        user = await db.users.find_one({"steam_id": request.user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    case = await db.cases.find_one({"_id": ObjectId(request.case_id)})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check if user has enough points
    if user["points"] < case["price"]:
        return CaseOpenResult(
            success=False,
            message="Not enough points",
            points_remaining=user["points"]
        )
    
    # Deduct points
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$inc": {"points": -case["price"], "cases_opened": 1}}
    )
    
    # Determine dropped item
    skin = await determine_dropped_skin(case)
    if not skin:
        raise HTTPException(status_code=500, detail="Failed to determine dropped skin")
    
    # Add skin to user's inventory
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$push": {"inventory": {
            "skin_id": str(skin["_id"]),
            "obtained_at": datetime.utcnow(),
            "equipped": False
        }}}
    )
    
    # Get updated points
    updated_user = await db.users.find_one({"_id": user["_id"]})
    
    return CaseOpenResult(
        success=True,
        skin=skin,
        message="Case opened successfully",
        points_remaining=updated_user["points"]
    )

# Skin routes
@app.post("/skins/", response_model=Skin)
async def create_skin(skin: SkinCreate):
    # Create new skin
    new_skin = skin.dict(by_alias=True)
    result = await db.skins.insert_one(new_skin)
    created_skin = await db.skins.find_one({"_id": result.inserted_id})
    return created_skin

@app.get("/skins/", response_model=List[Skin])
async def get_skins():
    skins = await db.skins.find().to_list(length=100)
    return skins

@app.get("/skins/{skin_id}", response_model=Skin)
async def get_skin(skin_id: str):
    skin = await db.skins.find_one({"_id": ObjectId(skin_id)})
    if not skin:
        raise HTTPException(status_code=404, detail="Skin not found")
    return skin

@app.post("/skins/equip")
async def equip_skin(user_id: str, skin_id: str):
    # Get user
    if ObjectId.is_valid(user_id):
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    else:
        user = await db.users.find_one({"steam_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has the skin
    has_skin = False
    for item in user.get("inventory", []):
        if item["skin_id"] == skin_id:
            has_skin = True
            break
    
    if not has_skin:
        raise HTTPException(status_code=404, detail="Skin not found in user's inventory")
    
    # Get skin details to determine weapon type
    skin = await db.skins.find_one({"_id": ObjectId(skin_id)})
    if not skin:
        raise HTTPException(status_code=404, detail="Skin not found in database")
    
    # Unequip any currently equipped skin of the same weapon type
    inventory = user.get("inventory", [])
    for i, item in enumerate(inventory):
        existing_skin = await db.skins.find_one({"_id": ObjectId(item["skin_id"])})
        if existing_skin and existing_skin["weapon"] == skin["weapon"] and item.get("equipped", False):
            inventory[i]["equipped"] = False
    
    # Equip the new skin
    for i, item in enumerate(inventory):
        if item["skin_id"] == skin_id:
            inventory[i]["equipped"] = True
    
    # Update user inventory
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"inventory": inventory}}
    )
    
    return {"success": True, "message": "Skin equipped successfully"}

@app.post("/skins/craft")
async def craft_skin(user_id: str, skin_ids: List[str]):
    # Get user
    if ObjectId.is_valid(user_id):
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    else:
        user = await db.users.find_one({"steam_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has all the skins
    for skin_id in skin_ids:
        has_skin = False
        for item in user.get("inventory", []):
            if item["skin_id"] == skin_id:
                has_skin = True
                break
        
        if not has_skin:
            raise HTTPException(status_code=404, detail=f"Skin {skin_id} not found in user's inventory")
    
    # Check if all skins have the same rarity
    skins = []
    for skin_id in skin_ids:
        skin = await db.skins.find_one({"_id": ObjectId(skin_id)})
        if not skin:
            raise HTTPException(status_code=404, detail=f"Skin {skin_id} not found in database")
        skins.append(skin)
    
    rarity = skins[0]["rarity"]
    for skin in skins:
        if skin["rarity"] != rarity:
            raise HTTPException(status_code=400, detail="All skins must have the same rarity")
    
    # Calculate next rarity level
    rarity_levels = ["common", "uncommon", "rare", "mythical", "legendary", "ancient", "exotic"]
    if rarity == "exotic":
        raise HTTPException(status_code=400, detail="Cannot craft from exotic rarity skins")
    
    rarity_index = rarity_levels.index(rarity)
    next_rarity = rarity_levels[rarity_index + 1]
    
    # Get all skins of next rarity
    next_rarity_skins = await db.skins.find({"rarity": next_rarity}).to_list(length=100)
    if not next_rarity_skins:
        raise HTTPException(status_code=400, detail=f"No skins available of {next_rarity} rarity")
    
    # Randomly select a skin
    crafted_skin = random.choice(next_rarity_skins)
    
    # Remove the used skins from user's inventory
    inventory = [item for item in user.get("inventory", []) if item["skin_id"] not in skin_ids]
    
    # Add the new skin to user's inventory
    inventory.append({
        "skin_id": str(crafted_skin["_id"]),
        "obtained_at": datetime.utcnow(),
        "equipped": False
    })
    
    # Update user inventory
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"inventory": inventory}}
    )
    
    return {
        "success": True,
        "message": "Skin crafted successfully",
        "crafted_skin": crafted_skin
    }

# Helper functions
async def determine_dropped_skin(case):
    # Get all skins IDs from the case
    skin_ids = [item["skin_id"] for item in case.get("items", [])]
    
    # If the case has drop chances defined
    drop_chances = {}
    total_chance = 0
    
    for item in case.get("items", []):
        if "drop_chance" in item:
            drop_chances[str(item["skin_id"])] = item["drop_chance"]
            total_chance += item["drop_chance"]
    
    # If drop chances don't add up to 100%, normalize them
    if abs(total_chance - 100) > 0.01:
        for skin_id in drop_chances:
            drop_chances[skin_id] = (drop_chances[skin_id] / total_chance) * 100
    
    # Select a skin based on drop chances
    if drop_chances:
        rand = random.uniform(0, 100)
        cumulative = 0
        selected_skin_id = None
        
        for skin_id, chance in drop_chances.items():
            cumulative += chance
            if rand <= cumulative:
                selected_skin_id = skin_id
                break
        
        if selected_skin_id:
            return await db.skins.find_one({"_id": ObjectId(selected_skin_id)})
    
    # Fallback: select a random skin
    if skin_ids:
        random_skin_id = random.choice(skin_ids)
        return await db.skins.find_one({"_id": random_skin_id})
    
    # If no skins in the case, select a random skin from the database
    return await db.skins.find_one({})

# Steam authentication routes (simplified for demo)
@app.get("/auth/steam/return")
async def steam_auth_return(request: Request):
    # In a real app, this would validate the Steam authentication
    # For demo, we'll simulate a successful login
    
    # Get parameters from query string
    params = dict(request.query_params)
    
    # Simulate Steam auth response
    steam_id = params.get("openid.claimed_id", "").split("/")[-1]
    
    if not steam_id:
        raise HTTPException(status_code=400, detail="Invalid Steam authentication")
    
    # In a real app, you would fetch user info from Steam API
    # For demo, create a user with mock data
    user = await db.users.find_one({"steam_id": steam_id})
    
    if not user:
        # Create new user
        new_user = User(
            steam_id=steam_id,
            name=f"Player_{steam_id[-5:]}",
            avatar="https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg",
            points=500,  # Starting points
            inventory=[],
            cases_opened=0,
            join_date=datetime.utcnow()
        )
        result = await db.users.insert_one(new_user.dict(by_alias=True))
        user = await db.users.find_one({"_id": result.inserted_id})
    
    # Return user data with token
    return {
        "success": True,
        "user": user,
        "token": str(user["_id"])
    }

# Mount static files (for frontend)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)