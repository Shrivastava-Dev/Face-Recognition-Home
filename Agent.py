import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from rag_system import HomeRAGSystem
from logger import load_logs

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------- RAG SYSTEM INITIALIZATION ----------

rag_system = HomeRAGSystem()
rag_system.build_index_from_logs(load_logs())

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

# ---------- RAG TOOL FUNCTION ----------

def query_home_history(question: str) -> str:
    """
    Use this function when the user asks about PAST events, history, 
    or questions like 'who came home', 'when did someone arrive', 
    'who registered recently', etc.
    """
    results = rag_system.retrieve_relevant_logs(question, k=3, max_distance=1.5)
    if not results:
        return "No relevant historical records found for that question."
    
    context = "\n".join([text for text, dist in results])
    return f"Relevant historical records:\n{context}"

# ---------- SIMPLE RULE-BASED CHECK (Instant, No API) ----------

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
        tools=[turn_on_light, turn_off_light, turn_on_fan, turn_off_fan, query_home_history],
        system_instruction="""You are a brief, friendly smart home assistant. 
        Use query_home_history when asked about past events, who visited, 
        or registration history. Keep responses conversational and concise."""
    )
)

# ---------- MAIN FUNCTION ----------

def process_command(command):
    simple_result = try_simple_match(command)
    if simple_result:
        return simple_result
    
    try:
        response = chat.send_message(command)
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Sorry, I'm having trouble right now. Try again in a moment."

# ---------- TEST ----------

if __name__ == "__main__":
    print(process_command("turn on the light"))
    print(process_command("who came home today?"))
    print(process_command("did anyone new register?"))