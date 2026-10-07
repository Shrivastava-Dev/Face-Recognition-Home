import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR

# ---------- COLOR SCHEME ----------
DARK_BLUE = RGBColor(0x1F, 0x3A, 0x5F)
MID_BLUE = RGBColor(0x2E, 0x5C, 0x8A)
ACCENT_ORANGE = RGBColor(0xE8, 0x7A, 0x1E)
LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x2E, 0x8B, 0x57)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_title_slide(title, subtitle):
    slide = prs.slides.add_slide(blank_layout)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = DARK_BLUE

    title_box = slide.shapes.add_textbox(Inches(1), Inches(2.7), Inches(11.3), Inches(1.5))
    tf = title_box.text_frame
    tf.text = title
    tf.paragraphs[0].font.size = Pt(44)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = WHITE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    sub_box = slide.shapes.add_textbox(Inches(1), Inches(4.2), Inches(11.3), Inches(1))
    tf2 = sub_box.text_frame
    tf2.text = subtitle
    tf2.paragraphs[0].font.size = Pt(20)
    tf2.paragraphs[0].font.color.rgb = ACCENT_ORANGE
    tf2.paragraphs[0].alignment = PP_ALIGN.CENTER
    return slide


def add_section_title(slide, text):
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.3), Inches(0.7))
    tf = title_box.text_frame
    tf.text = text
    tf.paragraphs[0].font.size = Pt(26)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = DARK_BLUE


def add_content_slide(title, bullets):
    slide = prs.slides.add_slide(blank_layout)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE

    title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12), Inches(1))
    tf = title_box.text_frame
    tf.text = title
    tf.paragraphs[0].font.size = Pt(32)
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = DARK_BLUE

    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.25), Inches(3), Pt(4))
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT_ORANGE
    line.line.fill.background()

    body_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.5), Inches(5.5))
    tf_body = body_box.text_frame
    tf_body.word_wrap = True

    for i, (text, level) in enumerate(bullets):
        p = tf_body.paragraphs[0] if i == 0 else tf_body.add_paragraph()
        p.text = text
        p.level = level
        p.font.size = Pt(20 if level == 0 else 16)
        p.font.color.rgb = DARK_BLUE if level == 0 else RGBColor(0x55, 0x55, 0x55)
        p.font.bold = (level == 0)
        p.space_after = Pt(10)
    return slide


def add_flow_box(slide, text, left, top, width, height, color=DARK_BLUE, text_color=WHITE, font_size=13):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = color
    box.line.color.rgb = color
    tf = box.text_frame
    tf.word_wrap = True
    tf.text = text
    for p in tf.paragraphs:
        p.font.size = Pt(font_size)
        p.font.color.rgb = text_color
        p.font.bold = True
        p.alignment = PP_ALIGN.CENTER
    return box


def add_diamond(slide, text, left, top, width, height, color=ACCENT_ORANGE, text_color=DARK_BLUE, font_size=13):
    shape = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.color.rgb = DARK_BLUE
    tf = shape.text_frame
    tf.word_wrap = True
    tf.text = text
    for p in tf.paragraphs:
        p.font.size = Pt(font_size)
        p.font.bold = True
        p.font.color.rgb = text_color
        p.alignment = PP_ALIGN.CENTER
    return shape


def add_arrow_down(slide, left, top, length=Inches(0.3)):
    arrow = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, left, top, Inches(0.3), length)
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = ACCENT_ORANGE
    arrow.line.fill.background()
    return arrow


def add_connector(slide, x1, y1, x2, y2, color=ACCENT_ORANGE, width_pt=2.25):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
    conn.line.color.rgb = color
    conn.line.width = Pt(width_pt)
    return conn


def add_caption(slide, text, left, top, width, height, size=12, color=RGBColor(0x55, 0x55, 0x55)):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.text = text
    tf.paragraphs[0].font.size = Pt(size)
    tf.paragraphs[0].font.italic = True
    tf.paragraphs[0].font.color.rgb = color

# ============================================================
# SLIDE 1: TITLE
# ============================================================
add_title_slide(
    "AI-Powered Smart Home Assistant",
    "Face Recognition  •  Voice Control  •  LLM Integration  •  Raspberry Pi"
)

# ============================================================
# SLIDE 2: PROBLEM / MOTIVATION
# ============================================================
add_content_slide("Why This Project?", [
    ("Goal: Build a hands-on AI + Embedded Systems project combining multiple real-world technologies", 0),
    ("Combines Computer Vision, Speech AI, and Large Language Models in one working system", 1),
    ("Designed for real deployment on edge hardware (Raspberry Pi 4), not just a laptop demo", 1),
    ("", 0),
    ("What it does:", 0),
    ("Recognizes faces at the door and greets people by name", 1),
    ("Registers new/unknown visitors automatically via voice", 1),
    ("Responds to a wake word (\"Hey Jarvis\") like Alexa/Google Home", 1),
    ("Controls smart home appliances (lights, fans) via natural speech", 1),
])

# ============================================================
# SLIDE 3: HIGH-LEVEL ARCHITECTURE (Quick Overview)
# ============================================================
slide = prs.slides.add_slide(blank_layout)
add_section_title(slide, "High-Level Architecture (Overview)")

add_flow_box(slide, "INPUT LAYER\nUSB Camera + Microphone", Inches(0.8), Inches(1.4), Inches(11.5), Inches(0.8), DARK_BLUE)
add_arrow_down(slide, Inches(6.4), Inches(2.25))
add_flow_box(slide, "PROCESSING LAYER\nOpenCV (Detection) • face_recognition (Identity) • openWakeWord • Speech Recognition",
             Inches(0.8), Inches(2.65), Inches(11.5), Inches(0.9), MID_BLUE)
add_arrow_down(slide, Inches(6.4), Inches(3.6))
add_flow_box(slide, "INTELLIGENCE LAYER\nRule-Based Fast Path  +  Google Gemini API (Function Calling)",
             Inches(0.8), Inches(4.0), Inches(11.5), Inches(0.8), ACCENT_ORANGE, DARK_BLUE)
add_arrow_down(slide, Inches(6.4), Inches(4.85))
add_flow_box(slide, "OUTPUT LAYER\ngTTS (Text-to-Speech)  •  Hardware Control (Lights / Fans)",
             Inches(0.8), Inches(5.25), Inches(11.5), Inches(0.8), GREEN)
add_arrow_down(slide, Inches(6.4), Inches(6.1))
add_flow_box(slide, "DEPLOYMENT TARGET: Raspberry Pi 4 (8GB RAM)",
             Inches(0.8), Inches(6.5), Inches(11.5), Inches(0.6), DARK_BLUE)

# ============================================================
# SLIDE 4: DETAILED DIAGRAM — SENSING & CONCURRENCY
# ============================================================
slide = prs.slides.add_slide(blank_layout)
add_section_title(slide, "Detailed Block Diagram — Sensing & Concurrency")

add_flow_box(slide, "USB CAMERA\n(Video Frames)", Inches(0.5), Inches(1.1), Inches(5.8), Inches(0.5), DARK_BLUE, WHITE, 13)
add_flow_box(slide, "MICROPHONE\n(Audio Stream)", Inches(7.0), Inches(1.1), Inches(5.8), Inches(0.5), DARK_BLUE, WHITE, 13)

add_arrow_down(slide, Inches(3.25), Inches(1.65), Inches(0.22))
add_arrow_down(slide, Inches(9.75), Inches(1.65), Inches(0.22))

add_flow_box(slide, "PROCESS 1 (independent OS process)\nface_recognition_process()", Inches(0.5), Inches(1.92), Inches(5.8), Inches(0.5), MID_BLUE, WHITE, 12)
add_flow_box(slide, "PROCESS 2 (independent OS process)\nwake_word_process()", Inches(7.0), Inches(1.92), Inches(5.8), Inches(0.5), MID_BLUE, WHITE, 12)

left_steps = [
    "OpenCV DNN: detect_faces_dnn()\nLocate face coordinates in frame",
    "face_recognition:\nGenerate 128-d face encoding",
    "compare_faces() vs\nknown_faces.pkl database",
    "Known -> Greet (TTS) + log_event()\nUnknown -> Voice registration flow",
]
right_steps = [
    "read_amplified_chunk()\nAdaptive gain - prevents clipping",
    "openWakeWord model.predict()\nReturns confidence score 0.0-1.0",
    "Score > 0.3 (single hit) OR\n> 0.2 twice consecutively?",
    "TRIGGERED -> set pause_event\nHand off to run_command_listening()",
]

y = Inches(2.52)
step_h = Inches(0.58)
gap = Inches(0.1)
for i in range(4):
    color = DARK_BLUE if i % 2 == 0 else MID_BLUE
    add_flow_box(slide, left_steps[i], Inches(0.5), y, Inches(5.8), step_h, color, WHITE, 11)
    add_flow_box(slide, right_steps[i], Inches(7.0), y, Inches(5.8), step_h, color, WHITE, 11)
    if i < 3:
        add_arrow_down(slide, Inches(3.25), y + step_h, Inches(0.12))
        add_arrow_down(slide, Inches(9.75), y + step_h, Inches(0.12))
    y = y + step_h + gap

add_connector(slide, Inches(3.25), y, Inches(3.25), y + Inches(0.1), DARK_BLUE)
add_connector(slide, Inches(9.75), y, Inches(9.75), y + Inches(0.1), DARK_BLUE)

add_flow_box(slide,
    "SHARED MULTIPROCESSING OBJECTS  (created once in main(), passed to BOTH processes as arguments)\n"
    "pause_event (mp.Event)   |   stop_event (mp.Event)   |   audio_lock (mp.Lock)",
    Inches(0.5), y + Inches(0.1), Inches(12.3), Inches(0.75), ACCENT_ORANGE, DARK_BLUE, 12)

note_y = y + Inches(1.0)
add_caption(slide,
    "Note: True parallel execution via multiprocessing (separate memory per process) - avoids Python's GIL contention "
    "that caused earlier wake-word reliability issues when using threading instead.",
    Inches(0.5), note_y, Inches(12.3), Inches(0.5), 12)

# ============================================================
# SLIDE 5: DETAILED DIAGRAM — COMMAND PROCESSING LOGIC
# ============================================================
slide = prs.slides.add_slide(blank_layout)
add_section_title(slide, "Detailed Block Diagram — Command Processing Logic")

add_flow_box(slide, "Wake word triggered -> run_command_listening()", Inches(0.5), Inches(1.05), Inches(12.3), Inches(0.5), DARK_BLUE, WHITE, 14)
add_arrow_down(slide, Inches(6.65), Inches(1.58), Inches(0.2))

add_flow_box(slide, "Google Speech-to-Text API:  Audio -> Text Command", Inches(0.5), Inches(1.82), Inches(12.3), Inches(0.5), MID_BLUE, WHITE, 14)
add_arrow_down(slide, Inches(6.65), Inches(2.35), Inches(0.2))

add_diamond(slide, "Rule-based match?\n(try_simple_match)", Inches(4.95), Inches(2.6), Inches(3.4), Inches(1.0), ACCENT_ORANGE, DARK_BLUE, 13)

add_connector(slide, Inches(5.5), Inches(3.6), Inches(3.3), Inches(3.9), DARK_BLUE)
add_connector(slide, Inches(7.8), Inches(3.6), Inches(10.0), Inches(3.9), DARK_BLUE)

add_flow_box(slide, "YES -> Execute Python function directly\n(turn_on_light / turn_off_fan / etc.)\nInstant - zero API calls",
             Inches(0.5), Inches(3.9), Inches(5.6), Inches(0.65), GREEN, WHITE, 12)
add_flow_box(slide, "NO -> chat.send_message(command)\nGoogle Gemini API (gemini-3.5-flash)",
             Inches(7.2), Inches(3.9), Inches(5.6), Inches(0.6), ACCENT_ORANGE, DARK_BLUE, 12)

add_arrow_down(slide, Inches(3.3), Inches(4.6), Inches(0.15))
add_flow_box(slide, "appliance_state dict checked\n(skip action if already ON/OFF)",
             Inches(0.5), Inches(4.8), Inches(5.6), Inches(0.55), DARK_BLUE, WHITE, 12)

right_sub = [
    "Gemini analyzes command + available tools list",
    "SDK auto-executes the matching Python function",
    "Gemini formulates final natural-language reply",
]
ry = Inches(4.55)
for step in right_sub:
    add_arrow_down(slide, Inches(10.0), ry - Inches(0.15), Inches(0.12))
    add_flow_box(slide, step, Inches(7.2), ry, Inches(5.6), Inches(0.5), MID_BLUE, WHITE, 11)
    ry = ry + Inches(0.58)

add_connector(slide, Inches(3.3), Inches(5.35), Inches(5.5), Inches(6.2), DARK_BLUE)
add_connector(slide, Inches(10.0), ry, Inches(8.5), Inches(6.2), DARK_BLUE)

add_flow_box(slide, "response_text ready -> returned to main.py's speak()",
             Inches(3.0), Inches(6.25), Inches(7.3), Inches(0.55), DARK_BLUE, WHITE, 13)

add_caption(slide,
    "Note: TESTING_MODE flag in Agent.py mocks Gemini responses during development, preserving the free-tier quota (20 requests/day).",
    Inches(0.5), Inches(6.95), Inches(12.3), Inches(0.4), 11)

# ============================================================
# SLIDE 6: DETAILED DIAGRAM — OUTPUT & PERSISTENCE
# ============================================================
slide = prs.slides.add_slide(blank_layout)
add_section_title(slide, "Detailed Block Diagram — Output & Persistence")

add_flow_box(slide, "response_text received in main.py", Inches(0.5), Inches(1.05), Inches(12.3), Inches(0.5), DARK_BLUE, WHITE, 14)
add_arrow_down(slide, Inches(6.65), Inches(1.58), Inches(0.2))

add_flow_box(slide, "speak(response_text, audio_lock)", Inches(0.5), Inches(1.82), Inches(12.3), Inches(0.5), MID_BLUE, WHITE, 14)
add_arrow_down(slide, Inches(3.25), Inches(2.35), Inches(0.2))
add_arrow_down(slide, Inches(9.75), Inches(2.35), Inches(0.2))

add_flow_box(slide, "gTTS: text -> .mp3 file\n(requires internet connection)", Inches(0.5), Inches(2.6), Inches(5.8), Inches(0.6), ACCENT_ORANGE, DARK_BLUE, 12)
add_flow_box(slide, "audio_lock.acquire()\nPrevents overlap with other process", Inches(7.0), Inches(2.6), Inches(5.8), Inches(0.6), ACCENT_ORANGE, DARK_BLUE, 12)

add_arrow_down(slide, Inches(6.4), Inches(3.3), Inches(0.2))
add_flow_box(slide, "playsound: plays .mp3 through speaker -> temp file deleted after",
             Inches(0.5), Inches(3.55), Inches(12.3), Inches(0.55), DARK_BLUE, WHITE, 13)

add_arrow_down(slide, Inches(3.25), Inches(4.15), Inches(0.2))
add_arrow_down(slide, Inches(9.75), Inches(4.15), Inches(0.2))

add_flow_box(slide, "log_event()\n-> activity_log.json\n(timestamp, event_type, name)", Inches(0.5), Inches(4.4), Inches(5.8), Inches(0.65), MID_BLUE, WHITE, 12)
add_flow_box(slide, "save_database()\n-> known_faces.pkl\n(only on NEW registration)", Inches(7.0), Inches(4.4), Inches(5.8), Inches(0.65), MID_BLUE, WHITE, 12)

add_arrow_down(slide, Inches(3.25), Inches(5.1), Inches(0.2))
add_arrow_down(slide, Inches(9.75), Inches(5.1), Inches(0.2))

add_flow_box(slide, "pause_event.clear()  ->  face recognition process resumes",
             Inches(0.5), Inches(5.35), Inches(12.3), Inches(0.5), GREEN, WHITE, 13)
add_arrow_down(slide, Inches(6.65), Inches(5.9), Inches(0.2))

add_flow_box(slide, "System returns to IDLE  /  continuous monitoring state",
             Inches(0.5), Inches(6.15), Inches(12.3), Inches(0.5), DARK_BLUE, WHITE, 13)

add_caption(slide,
    "Note: Hardware functions (turn_on_light, etc.) execute IMMEDIATELY when decided - either rule-based or via Gemini "
    "function-calling - BEFORE this output stage. Currently simulated via print(); Arduino integration planned next.",
    Inches(0.5), Inches(6.8), Inches(12.3), Inches(0.5), 11)

# ============================================================
# SLIDE 7: HYBRID AI ARCHITECTURE
# ============================================================
add_content_slide("Hybrid AI Architecture (Key Design Decision)", [
    ("Problem: LLM API calls are slower, cost money, and have rate limits", 0),
    ("Solution: Two-tier command processing system", 0),
    ("", 0),
    ("Tier 1 — Rule-Based Matching (instant, free, offline)", 0),
    ("Handles common exact phrases: \"turn on light\", \"turn off fan\"", 1),
    ("Zero API calls, millisecond response time", 1),
    ("", 0),
    ("Tier 2 — Gemini LLM with Function Calling (fallback)", 0),
    ("Handles natural/ambiguous language: \"it's dark in here\"", 1),
    ("AI decides which function to call, executes real actions", 1),
    ("", 0),
    ("Result: Fast AND intelligent, while preserving API quota", 0),
])

# ============================================================
# SLIDE 8: TECH STACK
# ============================================================
add_content_slide("Technology Stack", [
    ("Computer Vision:  OpenCV (DNN detection)  •  face_recognition / dlib (identity)", 0),
    ("Speech:  openWakeWord (wake detection)  •  SpeechRecognition (STT)  •  gTTS (TTS)", 0),
    ("AI / LLM:  Google Gemini API  •  Function Calling / Tool Use", 0),
    ("RAG (prototype):  sentence-transformers  •  FAISS vector search", 0),
    ("Concurrency:  Python multiprocessing (true parallel execution)", 0),
    ("Data:  pickle (face DB persistence)  •  JSON (activity logging)", 0),
    ("Security:  python-dotenv (API key management)  •  .gitignore practices", 0),
    ("Hardware:  Raspberry Pi 4 (8GB)  •  USB Camera  •  Microphone  •  Arduino (planned)", 0),
])

# ============================================================
# SLIDE 9: CHALLENGES SOLVED
# ============================================================
add_content_slide("Key Technical Challenges Solved", [
    ("NumPy 2.x vs OpenCV compatibility conflict -> pinned numpy==1.26.4", 0),
    ("Wake-word unreliability -> root cause: GIL contention + USB bandwidth sharing", 0),
    ("Fixed via multiprocessing architecture + separate microphone device", 1),
    ("Distance limitation (~3m) -> implemented adaptive audio gain (prevents clipping)", 0),
    ("Audio collision race condition -> shared multiprocessing Lock across processes", 0),
    ("API quota exhaustion (20/day free tier) -> built mock-testing mode for development", 0),
    ("Corporate VPN blocking external services -> identified & documented as constraint", 0),
])

# ============================================================
# SLIDE 10: ENGINEERING PRACTICES
# ============================================================
add_content_slide("Engineering Practices Followed", [
    ("Version control with Git/GitHub — proper commit history throughout development", 0),
    ("Secrets management — API keys via .env, never hardcoded or exposed", 0),
    ("Graceful degradation — system works even if AI/TTS temporarily unavailable", 0),
    ("State management — appliances track ON/OFF state, avoid redundant actions", 0),
    ("Alexa-style UX — retry logic for misunderstood commands, timeout handling", 0),
    ("Resource-conscious design — frame-skipping, thread limiting for edge deployment", 0),
])

# ============================================================
# SLIDE 11: CURRENT STATUS
# ============================================================
add_content_slide("Current Status", [
    ("COMPLETE — Face detection & recognition with persistent database", 0),
    ("COMPLETE — Voice-based new user registration", 0),
    ("COMPLETE — Wake word detection (reliable at 3m+ range)", 0),
    ("COMPLETE — Gemini AI agent with function calling", 0),
    ("COMPLETE — Hybrid rule-based + LLM command routing", 0),
    ("COMPLETE — Multiprocessing architecture for reliability", 0),
    ("IN PROGRESS — Arduino integration for physical hardware control", 0),
    ("PLANNED — Final deployment & testing on Raspberry Pi 4", 0),
])

# ============================================================
# SLIDE 12: FUTURE ENHANCEMENTS
# ============================================================
add_content_slide("Future Enhancements", [
    ("Re-activate RAG system for \"ask about home history\" queries", 0),
    ("Offline STT/TTS fallback (Vosk / pyttsx3) for internet-outage resilience", 0),
    ("ReSpeaker far-field microphone array for improved range on Pi", 0),
    ("Multi-command conversation mode (follow-up questions without re-waking)", 0),
    ("Mobile app / web dashboard for remote monitoring", 0),
])

# ============================================================
# SLIDE 13: THANK YOU
# ============================================================
add_title_slide("Thank You", "Questions & Discussion")

# ---------- SAVE ----------
output_file = "Smart_Home_Assistant_Project.pptx"
prs.save(output_file)
print(f"Presentation saved as: {output_file}")
print(f"Full path: {os.path.abspath(output_file)}")