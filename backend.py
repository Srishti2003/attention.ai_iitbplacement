from fastapi import FastAPI, HTTPException
from transformers import pipeline
from pydantic import BaseModel
import requests
from neo4j_db import Neo4jMemory

# Initialize FastAPI app
app = FastAPI()

# Initialize Neo4j connection with error handling during app startup
neo4j_memory = None

@app.on_event("startup")
async def startup_event():
    global neo4j_memory
    try:
        neo4j_memory = Neo4jMemory("bolt://localhost:7687", "neo4j", "Attention.ai")
        print("Neo4j connected successfully.")
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}")

# Pydantic model for incoming user message
class UserMessage(BaseModel):
    user_id: str
    message: str

# Function to generate itinerary based on user preferences
def generate_itinerary(city: str, interests: list, budget: int):
    base_itinerary = [
        {"name": "Colosseum", "time": "9:00 AM", "transport": "Walk", "category": "historical", "cost": 50},
        {"name": "Roman Forum", "time": "11:00 AM", "transport": "Walk", "category": "historical", "cost": 40},
        {"name": "Piazza Navona - Food spots", "time": "1:00 PM", "transport": "Public transport", "category": "food", "cost": 30},
        {"name": "Pantheon", "time": "3:00 PM", "transport": "Walk", "category": "historical", "cost": 20},
        {"name": "Trevi Fountain", "time": "5:00 PM", "transport": "Walk", "category": "relaxation", "cost": 0},
    ]

    # Filter itinerary by interests and budget
    filtered_itinerary = [item for item in base_itinerary if item['category'] in interests]
    if budget < 50:
        return {"itinerary": [item for item in filtered_itinerary if item['cost'] <= 20]}
    elif budget < 100:
        return {"itinerary": filtered_itinerary[:3]}
    else:
        return {"itinerary": filtered_itinerary}

@app.post("/chat")
async def chat_endpoint(request: UserMessage):
    
    user_input = request.message.lower()
    user_id = request.user_id

    # Check Neo4j connection
    if not neo4j_memory:
        raise HTTPException(status_code=500, detail="Neo4j service is unavailable.")

    preferences = neo4j_memory.retrieve_preferences(user_id)

    MODEL_ENDPOINT_URL = "http://localhost:8000/generate_response"

    # Handle different user inputs
    if "plan a trip" in user_input:
        bot_reply = "Great! What day are you planning for, and what time do you want to start and end your day?"
    elif "interests" in user_input:
        bot_reply = "Could you tell me your interests? Options include historical sites, food experiences, and relaxation spots."
    elif "budget" in user_input:
        bot_reply = "What's your budget for the day?"
    elif "itinerary" in user_input:
        if preferences:
            itinerary = generate_itinerary(
                city="Rome",
                interests=preferences.get("interests", ["historical", "food", "relaxation"]),
                budget=preferences.get("budget", 100)
            )
            bot_reply = "Here's your customized itinerary:\n" + "\n".join(
                [f"{item['name']} at {item['time']} ({item['transport']})" for item in itinerary["itinerary"]]
            )
        else:
            bot_reply = "Could not find your preferences. Please tell me your interests and budget first."
    else:
        try:
            # Call external model service for general inquiries
            response = requests.post(MODEL_ENDPOINT_URL, json={"user_input": request.message})
            response.raise_for_status()
            bot_reply = response.json().get("reply", "Sorry, I couldn't understand.")
        except requests.RequestException:
            bot_reply = "Error: Model service unavailable."

    return {"reply": bot_reply}

@app.get("/get_itinerary")
async def get_itinerary_endpoint(user_id: str):
    if not neo4j_memory:
        raise HTTPException(status_code=500, detail="Neo4j service is unavailable.")

    preferences = neo4j_memory.retrieve_preferences(user_id)

    if preferences:
        itinerary = generate_itinerary(
            city="Rome",
            interests=preferences.get("interests", ["historical", "food", "relaxation"]),
            budget=preferences.get("budget", 100)
        )
        return {"itinerary": itinerary["itinerary"]}
    else:
        raise HTTPException(status_code=404, detail="User preferences not found.")
