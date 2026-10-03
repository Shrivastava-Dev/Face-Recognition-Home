import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# ---------- HARDWARE FUNCTIONS ----------

def turn_on_light():
    """Turns on the light"""
    print("[HARDWARE]: Light turned ON")
    return "Light turned on"

def turn_off_light():
    """Turns off the light"""
    print("[HARDWARE]: Light turned OFF")
    return "Light turned off"

def turn_on_fan():
    """Turns on the fan"""
    print("[HARDWARE]: Fan turned ON")
    return "Fan turned on"

def turn_off_fan():
    """Turns off the fan"""
    print("[HARDWARE]: Fan turned OFF")
    return "Fan turned off"

# ---------- SIMPLE RULE-BASED CHECK (Instant, No API) ----------

def try_simple_match(command):
    command = command.lower()
    
    if "light" in command and ("on" in command):
        return turn_on_light()
    if "light" in command and "off" in command:
        return turn_off_light()
    if "fan" in command and "on" in command:
        return turn_on_fan()
    if "fan" in command and "off" in command:
        return turn_off_fan()
    
    return None  # No simple match, will try Gemini next

# ---------- GEMINI CHAT SETUP ----------

chat = client.chats.create(
    model="gemini-3.5-flash",
    config=types.GenerateContentConfig(
        tools=[turn_on_light, turn_off_light, turn_on_fan, turn_off_fan],
        system_instruction="You are a brief, friendly smart home assistant."
    )
)

# ---------- MAIN FUNCTION (This is What You'll Call) ----------

def process_command(command):
    # Try instant matching first
    simple_result = try_simple_match(command)
    if simple_result:
        return simple_result
    
    # Otherwise, ask Gemini
    try:
        response = chat.send_message(command)
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Sorry, I'm having trouble right now. Try again in a moment."
    
    
if __name__ == "__main__":
    print(process_command("turn on the light"))
    print(process_command("it's dark in here"))
    print(process_command("fan off"))