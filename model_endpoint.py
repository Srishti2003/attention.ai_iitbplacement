from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

class UserInput(BaseModel):
    user_input: str

# Use a conversational model, BlenderBot for instance
chatbot_pipeline = pipeline("text2text-generation", model="facebook/blenderbot-400M-distill")

@app.post("/generate_response")
async def generate_response(request: UserInput):
    user_input = request.user_input
    response = chatbot_pipeline(user_input, max_length=50, num_return_sequences=1)
    bot_reply = response[0]["generated_text"]
    return {"reply": bot_reply}
