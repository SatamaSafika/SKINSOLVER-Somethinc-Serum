import os
from dotenv import load_dotenv
import discord
import re
import random

# Load Token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ================================
# State management per user
# ================================
user_states = {}  
# Format state: { user_id: {"phase": "bright", "step": "focus"} }

# ================================
# Regex patterns
# ================================

phase_patterns = {
    "greet": [r"\b(hi|hello|hey|halo|hai|morning|afternoon|evening)\b"],
    "bright": [r"\b(cerah|mencerahkan|bright|glow)\b"],
    "acne": [r"\b(acne|jerawat|pimple|bruntusan|komedo|breakout|pori)\b"],
    "antiaging": [r"\b(antiaging|keriput|wrinkle|tua|aging|garis halus|awet muda|kerutan|umur)\b"],
}

focus_patterns = {
    "kusam": r"\b(kusam|dull|pucat|gelap)\b",
    "bekas": r"\b(bekas|scar|mark)\b",
    "hyper": r"\b(hyper|flek|dark spot|hiperpigmentasi)\b",
    "jerawat": r"\b(jerawat|acne|pimple|bruntusan|komedo|breakout)\b",
    "cegah": r"\b(cegah|prevent|pencegahan)\b",
    "visible": r"\b(visible|nampak|kelihatan)\b",
}

type_patterns = {
    "sensitive": r"\b(sensitive|sensitif)\b",
    "normal": r"\b(normal)\b",
    "oily": r"\b(oily|berminyak|minyakan)\b",
}

# ================================
# Responses
# ================================

responses = {
    "greet": {
        "default": [
            "Hai cantik! ✨ Apa kabar hari ini?",
            "Halo! Senang ketemu kamu 🤗",
        ],
        "next": "Kamu mau serum untuk apa nih? Percayakan samaku, aku pasti bisa beri kamu jawabannya",
    },
    "bright": {
        "ask_focus": "Mau fokus mencerahkan bagian wajah yang mana nih, beauty? ",
        "kusam": {
            "ask_type": "Oke, kulit kusam ya. Tapi sebelum itu aku mau tanya lagi dong, tipe kulit kamu apa? ",
            "sensitive": ["Gunakan *5% Niacinamide + Moisture Sabi Beet Serum* jika kulit kamu normal-to-dry atau *Revive Potion 3% Arbutin Bakuchiol* jika kulit kamu normal-to-oily 🌸"],
            "normal": ["Kulit normal bisa pakai *10% Niacinamide + Moisture Sabi Beet Serum* ya cantik 🌟"],
            "oily": ["Coba produk *Revive Potion 3% Arbutin Bakuchiol* kami, beauty 😉"],
        },
        "bekas": [
            "Untuk bekas jerawat, gunakan Dark Spot Reducer Ampoule kami ya beb 🌿",
            "Kamu bisa cobain Ampoule kami yang namanya Dark Spot Reducer ya cantik  🌞",
        ],
        "hyper": {
            "ask_type": "Oke, kamu mau mengatasi hiperpigmentasi ya. Sebelum itu, tipe kulit kamu apa?",
            "sensitive": ["Pakai serum anti-spot yang diformulasikan untuk kulit sensitif 🌸"],
            "normal": ["Gunakan retinol atau AHA untuk mengurangi hiperpigmentasi 🌟"],
            "oily": ["Kulit berminyak cocok dengan azelaic acid atau niacinamide 💧"],
        },
    },
    "acne": {
        "ask_focus": "Acne itu terkadang disebabkan masalah pori, tetapi acne dan pori-pori itu kadang berbeda cara perawatannya. Kamu mau mulai dari yang mana dulu?",
        "jerawat": ["Gunakan salicylic acid atau benzoyl peroxide untuk jerawat aktif 🧴"],
        "cegah": ["Rajin double cleansing dan pakai sunscreen bisa mencegah jerawat 🌞"],
        "visible": ["Produk spot treatment bisa membantu jerawat yang terlihat 👀"],
    },
    "antiaging": {
        "ask_type": "Cantik itu tidak lekang oleh waktu, beauty. Tapi untuk menjaga kulit tetap muda dan sehat, aku ignin tau nih tipe kulitmu apa",
        "sensitive": ["Gunakan retinol low concentration atau bakuchiol 🌿"],
        "normal": ["Kulit normal bisa mencoba retinol + moisturizer yang kaya nutrisi 💧"],
        "oily": ["Produk ringan dengan retinol/peptide cocok untuk kulit berminyak ✨"],
    },
}

# ================================
# Detection functions
# ================================

def detect_phase(message: str):
    for phase, patterns in phase_patterns.items():
        for pat in patterns:
            if re.search(pat, message, re.IGNORECASE):
                return phase
    return None

def detect_focus(message: str):
    for focus, pat in focus_patterns.items():
        if re.search(pat, message, re.IGNORECASE):
            return focus
    return None

def detect_type(message: str):
    for t, pat in type_patterns.items():
        if re.search(pat, message, re.IGNORECASE):
            return t
    return None

# ================================
# Conversation handler
# ================================
def get_response(user_id, message: str):
    state = user_states.get(user_id, {})

    # STEP 1: Greet
    if not state:
        phase = detect_phase(message)
        if phase == "greet":
            user_states[user_id] = {"step": "phase"}
            return random.choice(responses["greet"]["default"]) + "\n" + responses["greet"]["next"]
        return None

    # STEP 2: Detect Phase after greeting
    if state.get("step") == "phase":
        phase = detect_phase(message)
        if phase in ["bright", "acne", "antiaging"]:
            user_states[user_id] = {"phase": phase, "step": "focus"}
            if phase == "bright":
                return responses["bright"]["ask_focus"]
            elif phase == "acne":
                return responses["acne"]["ask_focus"]
            elif phase == "antiaging":
                return responses["antiaging"]["ask_type"]
        return "Coba ceritakan, kamu ingin skincare untuk mencerahkan, jerawat, atau anti aging? 😊"

    # STEP 3: Focus / Type
    phase = state.get("phase")
    if state.get("step") == "focus":
        if phase == "bright":
            focus = detect_focus(message)
            if focus == "kusam":
                user_states[user_id] = {"phase": phase, "focus": "kusam", "step": "type"}

                return responses["bright"]["kusam"]["ask_type"]
            
            elif focus == "bekas":
                user_states[user_id] = {}
                return random.choice(responses["bright"]["bekas"])
            elif focus == "hyper":
                user_states[user_id] = {"phase": phase, "focus": "hyper", "step": "type"}
                return responses["bright"]["hyper"]["ask_type"]

        elif phase == "acne":
            focus = detect_focus(message)
            if focus in responses["acne"]:
                user_states[user_id] = {}
                return random.choice(responses["acne"][focus])

        elif phase == "antiaging":
            t = detect_type(message)
            if t and t in responses["antiaging"]:
                user_states[user_id] = {}
                return random.choice(responses["antiaging"][t])
            else:
                user_states[user_id] = {"phase": phase, "step": "type"}
                return responses["antiaging"]["ask_type"]

    if state.get("step") == "type":
        phase = state.get("phase")
        focus = state.get("focus")
        t = detect_type(message)
        if not t:
            return "Tipe kulit kamu sensitive, normal, atau oily ya? 😊"

        # Bright - kusam/hyper
        if phase == "bright" and focus in ["kusam", "hyper"]:
            if t in responses["bright"][focus]:
                user_states[user_id] = {}
                return random.choice(responses["bright"][focus][t])

        # Antiaging
        if phase == "antiaging":
            if t in responses["antiaging"]:
                user_states[user_id] = {}
                return random.choice(responses["antiaging"][t])

    return None

# ================================
# Discord Events
# ================================

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    response = get_response(message.author.id, message.content)
    if response:
        await message.channel.send(response)

client.run(TOKEN)