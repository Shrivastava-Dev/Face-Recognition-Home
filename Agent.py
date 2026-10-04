import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

TESTING_MODE = True

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------- APPLIANCE STATE TRACKING ----------
appliance_state = {
    "light": False,  # False = OFF, True = ON
    "fan": False,
}

# ---------- HARDWARE FUNCTIONS (Now State-Aware) ----------

def turn_on_light():
    """Turns on the light"""
    if appliance_state["light"]:
        return "Light is already on"
    appliance_state["light"] = True
    print("[HARDWARE]: Light turned ON")
    return "Light turned on"

def turn_off_light():
    """Turns off the light"""
    if not appliance_state["light"]:
        return "Light is already off"
    appliance_state["light"] = False
    print("[HARDWARE]: Light turned OFF")
    return "Light turned off"

def turn_on_fan():
    """Turns on the fan"""
    if appliance_state["fan"]:
        return "Fan is already on"
    appliance_state["fan"] = True
    print("[HARDWARE]: Fan turned ON")
    return "Fan turned on"

def turn_off_fan():
    """Turns off the fan"""
    if not appliance_state["fan"]:
        return "Fan is already off"
    appliance_state["fan"] = False
    print("[HARDWARE]: Fan turned OFF")
    return "Fan turned off"

# ---------- SIMPLE RULE-BASED CHECK ----------

def try_simple_match(command):
    command = command.lower()
    
    if "light" in command and "on" in command:
        return turn_on_light()
    if "light" in command and "off" in command:
        return turn_off_light()
    if "fan" in command and "on" in command:
        return turn_on_fan()
    if "fan" in command and "off" in command:
        return turn_off_fan()
    
    return None

# ---------- GEMINI CHAT SETUP ----------

chat = client.chats.create(
    model="gemini-3.5-flash",
    config=types.GenerateContentConfig(
        tools=[turn_on_light, turn_off_light, turn_on_fan, turn_off_fan],
        system_instruction="You are a brief, friendly smart home assistant."
    )
)

# ---------- MAIN FUNCTION ----------

def process_command(command):
    simple_result = try_simple_match(command)
    if simple_result:
        print("[ROUTING] Handled by: RULE-BASED (no API call)")
        return simple_result
    
    if TESTING_MODE:
        print(f"[MOCK MODE] Would send to Gemini: '{command}'")
        return f"(Mock response) I heard you say: {command}"
    
    print("[ROUTING] Handled by: GEMINI API")
    try:
        response = chat.send_message(command)
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Sorry, I'm having trouble right now. Try again in a moment."

# ---------- TEST ----------

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        print(f"Agent: {process_command(user_input)}")