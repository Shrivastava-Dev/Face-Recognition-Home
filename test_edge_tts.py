import edge_tts
import asyncio
import playsound

VOICE = "en-IN-PrabhatNeural"

async def main():
    text = "Hey there! Welcome to Aditya's home! Great to see you!"
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save("test_output.mp3")

asyncio.run(main())
playsound.playsound("test_output.mp3")