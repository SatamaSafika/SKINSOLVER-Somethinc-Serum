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
# Regex patterns
# ================================

phase_patterns = {
    "greet": [r"\b(hi|hello|hey|halo|hai|morning|afternoon|evening)\b"],
    "bright": [r"\b(cerah|bright|glow|kusam|bekas|hyper)\b"],
    "acne": [r"\b(acne|jerawat|cegah|pencegahan|visible)\b"],
    "antiaging": [r"\b(antiaging|keriput|wrinkle|tua|aging)\b"],
}

focus_patterns = {
    "kusam": r"\b(kusam|dull)\b",
    "bekas": r"\b(bekas|scar|mark)\b",
    "hyper": r"\b(hyper|flek|dark spot|hiperpigmentasi)\b",
    "jerawat": r"\b(jerawat|acne|pimple)\b",
    "cegah": r"\b(cegah|prevent|pencegahan)\b",
    "visible": r"\b(visible|nampak|kelihatan)\b",
}

type_patterns = {
    "sensitive": r"\b(sensitive|sensitif)\b",
    "normal": r"\b(normal)\b",
    "oily": r"\b(oily|berminyak)\b",
}

# ================================
# Responses
# ================================

responses = {
    "greet": {
        "default": [
            "Hai cantik! ✨ Apa kabar hari ini?",
            "Halo! Mau konsultasi skincare apa nih?",
        ]
    },
    "bright": {
        "kusam": {
            "sensitive": ["Gunakan serum vitamin C lembut untuk kulit sensitif ✨"],
            "normal": ["Kulit normal bisa pakai exfoliant ringan untuk mencerahkan 🌟"],
            "oily": ["Coba produk oil control + brightening, seperti niacinamide 😉"],
        },
        "bekas": [
            "Untuk bekas jerawat, gunakan serum dengan kandungan AHA/BHA atau retinol 🌿",
            "Niacinamide + sunscreen adalah kombinasi bagus untuk memudarkan bekas jerawat 🌞",
        ],
        "hyper": {
            "sensitive": ["Pakai serum anti-spot yang diformulasikan untuk kulit sensitif 🌸"],
            "normal": ["Gunakan retinol atau AHA untuk mengurangi hiperpigmentasi 🌟"],
            "oily": ["Kulit berminyak cocok dengan azelaic acid atau niacinamide 💧"],
        },
    },
    "acne": {
        "jerawat": ["Gunakan salicylic acid atau benzoyl peroxide untuk jerawat aktif 🧴"],
        "cegah": ["Rajin double cleansing dan pakai sunscreen bisa mencegah jerawat 🌞"],
        "visible": ["Produk spot treatment bisa membantu jerawat yang terlihat 👀"],
    },
    "antiaging": {
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

def get_response(message: str):
    phase = detect_phase(message)
    if not phase:
        return None

    # Phase greet → langsung balas default
    if phase == "greet":
        return random.choice(responses["greet"]["default"])

    # Phase bright
    if phase == "bright":
        focus = detect_focus(message)
        if focus == "kusam":
            t = detect_type(message)
            if t and t in responses["bright"]["kusam"]:
                return random.choice(responses["bright"]["kusam"][t])
            return None
        elif focus == "bekas":
            return random.choice(responses["bright"]["bekas"])
        elif focus == "hyper":
            t = detect_type(message)
            if t and t in responses["bright"]["hyper"]:
                return random.choice(responses["bright"]["hyper"][t])
            return None

    # Phase acne
    if phase == "acne":
        focus = detect_focus(message)
        if focus and focus in responses["acne"]:
            return random.choice(responses["acne"][focus])

    # Phase antiaging
    if phase == "antiaging":
        t = detect_type(message)
        if t and t in responses["antiaging"]:
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
    
    response = get_response(message.content)
    if response:
        await message.channel.send(response)

client.run(TOKEN)