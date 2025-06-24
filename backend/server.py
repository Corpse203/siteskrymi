from fastapi import FastAPI, HTTPException, Depends, Request, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import json

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration MongoDB
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client.casino_calls_db

# Collections
offers_collection = db.offers
calls_collection = db.calls
clicks_collection = db.clicks
logs_collection = db.logs

# Modèles Pydantic
class OfferBase(BaseModel):
    title: str
    bonus: str
    description: str
    color: str
    logo: str
    link: str
    tags: List[str] = []

class Offer(OfferBase):
    id: str
    clicks: int = 0
    created_at: datetime
    updated_at: datetime

class CallBase(BaseModel):
    slot: str
    username: str

class Call(CallBase):
    id: str
    created_at: datetime

class LoginRequest(BaseModel):
    password: str

class ClickData(BaseModel):
    offer_id: str
    user_ip: str

# Fonctions utilitaires
def get_current_user(admin: Optional[str] = Cookie(None)):
    return admin == "true"

def convert_objectid_to_str(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

# Initialisation des données par défaut
async def init_default_offers():
    if offers_collection.count_documents({}) == 0:
        default_offers = [
            {
                "id": str(uuid.uuid4()),
                "title": "Betify",
                "bonus": "100% offert + 30 Free Spins (en Raw Money)",
                "description": "Jusqu'à 20% de cashback tout les lundi !",
                "color": "linear-gradient(to right, #00c851, #007e33)",
                "logo": "https://images.pexels.com/photos/6990180/pexels-photo-6990180.jpeg?auto=compress&cs=tinysrgb&w=100&h=100&dpr=1",
                "link": "https://bit.ly/BetifySkrymi",
                "tags": ["Crypto", "CB", "VIP Rank"],
                "clicks": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Winningz",
                "bonus": "CODE : WZMEGA - 200% de bonus jusqu'à 20 000€",
                "description": "200 Free Spins offerts (50 par jour pendant 4 jours) + Jusqu'à 20% de cashback",
                "color": "linear-gradient(to right, #3a86ff, #e63946)",
                "logo": "https://images.pexels.com/photos/6990348/pexels-photo-6990348.jpeg?auto=compress&cs=tinysrgb&w=100&h=100&dpr=1",
                "link": "https://bit.ly/SkrymiWinningz",
                "tags": ["Crypto", "CB", "Retrait en 1h", "VIP Rank"],
                "clicks": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Samba Slots",
                "bonus": "200% de BONUS jusqu'à 5'000€",
                "description": "10% de CASHBACK INSTANTANÉ dès la création de votre compte + 50 Freespins",
                "color": "linear-gradient(to right, #fcd34d, #fbbf24)",
                "logo": "https://images.unsplash.com/photo-1550496635-97c10f749275?w=100&h=100&fit=crop",
                "link": "https://bit.ly/SkrymiSamba",
                "tags": ["Crypto", "CB", "Retrait en 1h"],
                "clicks": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "BetBlast",
                "bonus": "200% jusqu'à 7500€",
                "description": "50 Free Spins sur Wanted Dead or a Wild",
                "color": "linear-gradient(to right, #007e33, #808080)",
                "logo": "https://images.unsplash.com/photo-1605317068450-d6878f5c8dbb?w=100&h=100&fit=crop",
                "link": "https://bit.ly/SkrymiBetblast",
                "tags": ["Crypto", "CB", "Retrait en 1h", "VIP Rank"],
                "clicks": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Fast Slots",
                "bonus": "200% de BONUS jusqu'à 5'000€",
                "description": "10% de CASHBACK INSTANTANÉ dès la création de votre compte + 50 Freespins",
                "color": "linear-gradient(to right, #7f00ff, #e100ff)",
                "logo": "https://images.unsplash.com/photo-1583512603834-01a3a1e56241?w=100&h=100&fit=crop",
                "link": "https://bit.ly/FastSkrymi",
                "tags": ["Crypto", "CB", "Retrait en 1h"],
                "clicks": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Golden Panda",
                "bonus": "200% de BONUS jusqu'à 5'000€",
                "description": "10% de CASHBACK INSTANTANÉ dès la création de votre compte + 50 Freespins",
                "color": "linear-gradient(to right, #d4af37, #ffd700)",
                "logo": "https://images.pexels.com/photos/6990180/pexels-photo-6990180.jpeg?auto=compress&cs=tinysrgb&w=100&h=100&dpr=1",
                "link": "https://bit.ly/SkrymiGolden",
                "tags": ["Crypto", "CB", "Retrait en 1h"],
                "clicks": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            },
            {
                "id": str(uuid.uuid4()),
                "title": "X7Casino",
                "bonus": "500%",
                "description": "50 Free Spins sur Big Bass Bonanza + 10% Cashback chaque lundi",
                "color": "linear-gradient(to right, #e63946, #3a86ff)",
                "logo": "https://images.pexels.com/photos/6990348/pexels-photo-6990348.jpeg?auto=compress&cs=tinysrgb&w=100&h=100&dpr=1",
                "link": "http://bit.ly/SkrymiX7",
                "tags": ["Crypto", "CB"],
                "clicks": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        offers_collection.insert_many(default_offers)

@app.on_event("startup")
async def startup_event():
    await init_default_offers()

# Routes Offres Casino
@app.get("/api/offers", response_model=List[dict])
async def get_offers():
    offers = list(offers_collection.find())
    return [convert_objectid_to_str(offer) for offer in offers]

@app.post("/api/offers", response_model=dict)
async def create_offer(offer: OfferBase, is_admin: bool = Depends(get_current_user)):
    if not is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    offer_data = offer.dict()
    offer_data["id"] = str(uuid.uuid4())
    offer_data["clicks"] = 0
    offer_data["created_at"] = datetime.now()
    offer_data["updated_at"] = datetime.now()
    
    result = offers_collection.insert_one(offer_data)
    offer_data["_id"] = result.inserted_id
    return convert_objectid_to_str(offer_data)

@app.put("/api/offers/{offer_id}", response_model=dict)
async def update_offer(offer_id: str, offer: OfferBase, is_admin: bool = Depends(get_current_user)):
    if not is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    offer_data = offer.dict()
    offer_data["updated_at"] = datetime.now()
    
    result = offers_collection.update_one({"id": offer_id}, {"$set": offer_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    updated_offer = offers_collection.find_one({"id": offer_id})
    return convert_objectid_to_str(updated_offer)

@app.delete("/api/offers/{offer_id}")
async def delete_offer(offer_id: str, is_admin: bool = Depends(get_current_user)):
    if not is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    result = offers_collection.delete_one({"id": offer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    return {"message": "Offer deleted successfully"}

# Routes Calls
@app.get("/api/calls")
async def get_calls():
    calls = list(calls_collection.find().sort("created_at", 1))
    calls_data = [convert_objectid_to_str(call) for call in calls]
    return {"calls": [{"slot": call["slot"], "user": call["username"]} for call in calls_data]}

@app.post("/api/calls")
async def create_call(call: CallBase, request: Request):
    call_data = call.dict()
    call_data["id"] = str(uuid.uuid4())
    call_data["created_at"] = datetime.now()
    
    # Log pour analytics
    log_data = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(),
        "ip": request.client.host,
        "slot": call.slot,
        "username": call.username,
        "action": "call_created"
    }
    logs_collection.insert_one(log_data)
    
    result = calls_collection.insert_one(call_data)
    return {"success": True, "message": "Call ajouté avec succès"}

@app.delete("/api/calls/{call_index}")
async def delete_call(call_index: int, is_admin: bool = Depends(get_current_user)):
    if not is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    calls = list(calls_collection.find().sort("created_at", 1))
    if call_index < 0 or call_index >= len(calls):
        raise HTTPException(status_code=400, detail="Index invalide")
    
    call_to_delete = calls[call_index]
    calls_collection.delete_one({"_id": call_to_delete["_id"]})
    return {"success": True}

@app.post("/api/calls/reset")
async def reset_calls(is_admin: bool = Depends(get_current_user)):
    if not is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    calls_collection.delete_many({})
    return {"success": True}

@app.post("/api/calls/reorder")
async def reorder_calls(new_order: List[dict], is_admin: bool = Depends(get_current_user)):
    if not is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Vider la collection et réinsérer dans le nouvel ordre
    calls_collection.delete_many({})
    for call_data in new_order:
        new_call = {
            "id": str(uuid.uuid4()),
            "slot": call_data["slot"],
            "username": call_data["user"],
            "created_at": datetime.now()
        }
        calls_collection.insert_one(new_call)
    
    return {"success": True}

# Routes Tracking
@app.post("/api/click")
async def track_click(click_data: ClickData, request: Request):
    # Vérifier que l'offre existe
    offer = offers_collection.find_one({"id": click_data.offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Incrémenter le compteur de clics
    offers_collection.update_one(
        {"id": click_data.offer_id},
        {"$inc": {"clicks": 1}}
    )
    
    # Enregistrer le clic
    click_record = {
        "id": str(uuid.uuid4()),
        "offer_id": click_data.offer_id,
        "user_ip": request.client.host,
        "timestamp": datetime.now()
    }
    clicks_collection.insert_one(click_record)
    
    return {"success": True}

@app.get("/api/analytics")
async def get_analytics(is_admin: bool = Depends(get_current_user)):
    if not is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Statistiques des offres
    offers = list(offers_collection.find())
    offers_stats = [
        {
            "title": offer["title"],
            "clicks": offer.get("clicks", 0),
            "id": offer["id"]
        }
        for offer in offers
    ]
    
    # Statistiques globales
    total_clicks = sum(offer.get("clicks", 0) for offer in offers)
    total_calls = calls_collection.count_documents({})
    
    return {
        "offers_stats": offers_stats,
        "total_clicks": total_clicks,
        "total_calls": total_calls
    }

# Routes Authentification
@app.post("/api/login")
async def login(login_request: LoginRequest):
    # Mot de passe admin (à externaliser en variable d'environnement)
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    if login_request.password == ADMIN_PASSWORD:
        response = JSONResponse({"success": True})
        response.set_cookie(
            key="admin",
            value="true",
            httponly=False,
            samesite="lax",
            secure=False
        )
        return response
    else:
        raise HTTPException(status_code=401, detail="Bad password")

@app.post("/api/logout")
async def logout():
    response = JSONResponse({"success": True})
    response.delete_cookie("admin")
    return response

@app.get("/api/logs")
async def get_logs(is_admin: bool = Depends(get_current_user)):
    if not is_admin:
        raise HTTPException(status_code=403, detail="Non autorisé")
    
    logs = list(logs_collection.find().sort("timestamp", -1).limit(100))
    return [convert_objectid_to_str(log) for log in logs]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)