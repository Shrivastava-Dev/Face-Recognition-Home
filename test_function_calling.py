import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------- DEFINE YOUR TOOLS (FUNCTIONS) ----------

def turn_on_light():
    """Turns on the home light"""
    print("[HARDWARE]: Light turned ON")
    return "Light has been turned on successfully"

def turn_off_light():
    """Turns off the home light"""
    print("[HARDWARE]: Light turned OFF")
    return "Light has been turned off successfully"

def turn_on_fan():
    """Turns on the home fan"""
    print("[HARDWARE]: Fan turned ON")
    return "Fan has been turned on successfully"

def turn_off_fan():
    """Turns off the home fan"""
    print("[HARDWARE]: Fan turned OFF")
    return "Fan has been turned off successfully"

# ---------- SET UP CHAT WITH TOOLS ----------

chat = client.chats.create(
    model="gemini-3.5-flash",
    config=types.GenerateContentConfig(
        tools=[turn_on_light, turn_off_light, turn_on_fan, turn_off_fan],
        system_instruction="You are a helpful smart home assistant. Keep responses brief and friendly."
    )
)

# ---------- TEST IT ----------

def chat_with_agent(message):
    response = chat.send_message(message)
    return response.text

# Test cases
print(chat_with_agent("It's getting dark in here"))
print("---")
print(chat_with_agent("I'm feeling hot"))
print("---")
print(chat_with_agent("What's the capital of France?"))