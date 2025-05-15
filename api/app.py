from flask import Flask, jsonify, request, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import random
import math
import os
import re
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../assets', static_url_path='/assets')
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')
CORS(app)

# Custom JSON encoder to handle ObjectId and datetime
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder

# MongoDB connection
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
mongo_db = os.getenv('MONGO_DB', 'csgo_cases_db')

client = MongoClient(mongo_uri)
db = client[mongo_db]

# Steam API settings
STEAM_API_KEY = os.getenv('STEAM_API_KEY', '')
STEAM_OPENID_URL = 'https://steamcommunity.com/openid/login'

# Helper function to convert MongoDB document to JSON serializable
def serialize_doc(doc):
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == '_id' and isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = [serialize_doc(item) for item in value]
            else:
                result[key] = value
        return result
    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    else:
        return doc

# Serve static files
@app.route('/')
def index():
    return send_from_directory('../', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../', path)

# Прямая реализация Steam авторизации без библиотеки openid
@app.route('/api/login')
def login():
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': request.url_root + 'api/auth',
        'openid.realm': request.url_root,
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
    }
    auth_url = STEAM_OPENID_URL + '?' + '&'.join([f'{key}={value}' for key, value in params.items()])
    return redirect(auth_url)

@app.route('/api/auth')
def auth():
    if 'openid.signed' not in request.args:
        return 'Authentication failed.', 400
    
    # Получаем Steam ID из ответа
    match = re.search(r'steamcommunity.com/openid/id/(.*?)$', request.args.get('openid.claimed_id', ''))
    if not match:
        return 'Could not get Steam ID.', 400
    
    steam_id = match.group(1)
    
    # Получение информации о пользователе
    user_info = get_steam_user_info(steam_id)
    
    if user_info:
        # Сохраняем информацию о пользователе в сессии
        session['steam_id'] = steam_id
        session['steam_username'] = user_info['personaname']
        session['steam_avatar'] = user_info['avatar']
        
        # Проверяем, существует ли пользователь в БД
        user = db.users.find_one({"steam_id": steam_id})
        
        if user:
            # Обновляем существующего пользователя
            db.users.update_one(
                {"steam_id": steam_id},
                {"$set": {
                    "username": user_info['personaname'],
                    "avatar": user_info['avatar'],
                    "last_login": datetime.now()
                }}
            )
        else:
            # Создаем нового пользователя
            db.users.insert_one({
                "steam_id": steam_id,
                "username": user_info['personaname'],
                "avatar": user_info['avatar'],
                "balance": 100.0,  # Начальный баланс
                "inventory": [],
                "created_at": datetime.now(),
                "last_login": datetime.now()
            })
        
        return redirect('/pages/profile.html')
    
    return 'Authentication failed. <a href="/api/login">Try again</a>', 400

def get_steam_user_info(steam_id):
    # Получение информации о пользователе через Steam API
    if not STEAM_API_KEY:
        # Если нет API ключа, возвращаем заглушку
        return {
            'personaname': f'User_{steam_id[-5:]}',
            'avatar': 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb.jpg'
        }
        
    response = requests.get(
        f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/',
        params={
            'key': STEAM_API_KEY,
            'steamids': steam_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['response']['players']:
            return data['response']['players'][0]
    
    return None

@app.route('/api/logout')
def logout():
    session.pop('steam_id', None)
    session.pop('steam_username', None)
    session.pop('steam_avatar', None)
    session.pop('scanned_item', None)  # Очищаем информацию о просканированном предмете
    return redirect('/pages/profile.html')

# API routes
@app.route('/api/cases')
def get_cases():
    cases = list(db.cases.find())
    return jsonify([serialize_doc(case) for case in cases])

@app.route('/api/case/<case_id>')
def get_case(case_id):
    try:
        case = db.cases.find_one({"_id": ObjectId(case_id)})
        if not case:
            return jsonify({"error": "Case not found"}), 404
            
        skins = list(db.skins.find({"case_id": ObjectId(case_id)}))
        
        return jsonify({
            "case": serialize_doc(case),
            "skins": [serialize_doc(skin) for skin in skins]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/inventory')
def get_inventory():
    if 'steam_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    try:
        user = db.users.find_one({"steam_id": session['steam_id']})
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        inventory = []
        
        for item in user.get('inventory', []):
            skin = db.skins.find_one({"_id": ObjectId(item['skin_id'])})
            if skin:
                inventory_item = {
                    "_id": str(item['_id']),
                    "skin": serialize_doc(skin),
                    "float": item['float'],
                    "obtained_at": item['obtained_at']
                }
                inventory.append(inventory_item)
                
        return jsonify(inventory)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/scan-case/<case_id>', methods=['POST'])
def scan_case(case_id):
    """Endpoint for X-Ray scanner - determines the item without claiming it but charges a fee"""
    if 'steam_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    try:
        # Get user
        user = db.users.find_one({"steam_id": session['steam_id']})
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        # Get case
        case = db.cases.find_one({"_id": ObjectId(case_id)})
        if not case:
            return jsonify({"error": "Case not found"}), 404
        
        # Calculate scanning fee (5% of case price, minimum 10 RC)
        scan_fee = max(case['price'] * 0.05, 10)
        scan_fee = round(scan_fee, 2)  # Round to 2 decimal places
        
        # Check if user has enough balance for scanning
        if user['balance'] < scan_fee:
            return jsonify({"error": f"Недостаточно средств для сканирования. Необходимо: {scan_fee} RC"}), 400
            
        # Deduct scan fee from user balance
        db.users.update_one(
            {"_id": user['_id']},
            {"$inc": {"balance": -scan_fee}}
        )
            
        # Get skins for this case
        skins = list(db.skins.find({"case_id": ObjectId(case_id)}))
        
        if not skins:
            return jsonify({"error": "No skins found for this case"}), 404
            
        # Determine the won item using weighted random selection based on rarity
        rarities = {
            "Consumer Grade": 0.7980,
            "Industrial Grade": 0.1598,
            "Mil-Spec": 0.0320,
            "Restricted": 0.0064,
            "Classified": 0.0032,
            "Covert": 0.0064,
            "Exceedingly Rare": 0.0026
        }
        
        # Group skins by rarity
        skins_by_rarity = {}
        for skin in skins:
            rarity = skin['quality']['title']
            if rarity not in skins_by_rarity:
                skins_by_rarity[rarity] = []
            skins_by_rarity[rarity].append(skin)
        
        # Pick a rarity based on probabilities
        rarity_roll = random.random()
        cumulative_prob = 0
        chosen_rarity = list(rarities.keys())[-1]  # Default to rarest
        
        for rarity, prob in rarities.items():
            cumulative_prob += prob
            if rarity_roll <= cumulative_prob and rarity in skins_by_rarity:
                chosen_rarity = rarity
                break
                
        # Pick a random skin from chosen rarity
        if chosen_rarity in skins_by_rarity and skins_by_rarity[chosen_rarity]:
            won_skin = random.choice(skins_by_rarity[chosen_rarity])
        else:
            # Fallback to a random skin if rarity not present
            won_skin = random.choice(skins)
            
        # Generate a random float value for the skin
        min_float = won_skin['min_float']
        max_float = won_skin['max_float']
        item_float = round(random.uniform(min_float, max_float), 6)
        
        # Store the scanned item in session for later retrieval
        session['scanned_item'] = {
            'skin_id': str(won_skin['_id']),
            'case_id': str(case_id),
            'float': item_float
        }
        
        # Get updated user balance
        updated_user = db.users.find_one({"_id": user['_id']})
        
        return jsonify({
            "wonItem": serialize_doc(won_skin),
            "float": item_float,
            "scan_fee": scan_fee,
            "new_balance": updated_user['balance']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/claim-scanned-case/<case_id>', methods=['POST'])
def claim_scanned_case(case_id):
    """Endpoint to claim an X-Ray scanned item"""
    if 'steam_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    if 'scanned_item' not in session:
        return jsonify({"error": "No scanned item found"}), 400
        
    scanned_item = session['scanned_item']
    
    # Verify this is the correct case
    if scanned_item['case_id'] != case_id:
        return jsonify({"error": "Case mismatch"}), 400
        
    try:
        # Get user
        user = db.users.find_one({"steam_id": session['steam_id']})
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        # Get case
        case = db.cases.find_one({"_id": ObjectId(case_id)})
        if not case:
            return jsonify({"error": "Case not found"}), 404
            
        # Check if user has enough balance
        if user['balance'] < case['price']:
            return jsonify({"error": "Insufficient balance"}), 400
            
        # Get the skin
        won_skin = db.skins.find_one({"_id": ObjectId(scanned_item['skin_id'])})
        if not won_skin:
            return jsonify({"error": "Item not found"}), 404
            
        # Use the saved float value
        item_float = scanned_item['float']
        
        # Deduct case price from user balance
        db.users.update_one(
            {"_id": user['_id']},
            {"$inc": {"balance": -case['price']}}
        )
        
        # Add item to user's inventory
        inventory_item_id = ObjectId()
        
        db.users.update_one(
            {"_id": user['_id']},
            {"$push": {
                "inventory": {
                    "_id": inventory_item_id,
                    "skin_id": won_skin['_id'],
                    "float": item_float,
                    "obtained_at": datetime.now()
                }
            }}
        )
        
        # Clear the scanned item from session
        session.pop('scanned_item', None)
        
        return jsonify({
            "success": True,
            "wonItem": serialize_doc(won_skin),
            "float": item_float
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/discard-case', methods=['POST'])
def discard_case():
    """Clean up session data after discarding a case"""
    if 'steam_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    # Clear the scanned item
    session.pop('scanned_item', None)
    
    return jsonify({"success": True})

@app.route('/api/sell-item/<item_id>', methods=['POST'])
def sell_item(item_id):
    if 'steam_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    try:
        # Get user
        user = db.users.find_one({"steam_id": session['steam_id']})
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        # Find the item in user's inventory
        inventory_item = None
        for item in user.get('inventory', []):
            if str(item['_id']) == item_id:
                inventory_item = item
                break
                
        if not inventory_item:
            return jsonify({"error": "Item not found in inventory"}), 404
            
        # Get the skin details
        skin = db.skins.find_one({"_id": inventory_item['skin_id']})
        if not skin:
            return jsonify({"error": "Skin not found"}), 404
            
        # Calculate sell price (90% of market value)
        sell_price = skin['price'] * 0.9
        
        # Remove item from inventory and add balance
        db.users.update_one(
            {"_id": user['_id']},
            {
                "$pull": {"inventory": {"_id": ObjectId(item_id)}},
                "$inc": {"balance": sell_price}
            }
        )
        
        # Get updated user balance
        updated_user = db.users.find_one({"_id": user['_id']})
        
        return jsonify({
            "success": True,
            "sold_for": sell_price,
            "new_balance": updated_user['balance']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user')
def get_user():
    if 'steam_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    try:
        user = db.users.find_one({"steam_id": session['steam_id']})
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        # Don't return inventory here to keep response small
        user_data = serialize_doc({
            "steam_id": user['steam_id'],
            "username": user['username'],
            "avatar": user['avatar'],
            "balance": user['balance'],
            "inventory_count": len(user.get('inventory', [])),
            "created_at": user['created_at'],
            "last_login": user['last_login']
        })
        
        return jsonify(user_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/add-funds', methods=['POST'])
def add_funds():
    if 'steam_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    try:
        data = request.json
        amount = float(data.get('amount', 0))
        
        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400
            
        # In a real app, you would process payment here
        
        # Update user balance
        db.users.update_one(
            {"steam_id": session['steam_id']},
            {"$inc": {"balance": amount}}
        )
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)