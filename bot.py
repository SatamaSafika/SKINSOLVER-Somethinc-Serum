import os
import re
import random
import discord
from dotenv import load_dotenv
import logging

# ================================
# NOTES
# ================================
# - Bot ini menggunakan user_states (in-memory dict) per user.
#   * State hilang kalau bot di-restart.
#   * Setelah kasih rekomendasi final, state user direset.
#   * Kalau input user nggak cocok regex, bot fallback ke pesan default/reflection.
#
# - Greeting ditangani di on_message untuk menghindari "double response".
# - Token Discord disimpan di file .env dengan nama DISCORD_TOKEN.

# Logging
logging.basicConfig(
    filename="logs/bot.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

# ================================
# Load Token
# ================================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ================================
# State management per user
# ================================
user_states = {}
# Format: { user_id: {"goal": "bright", "focus": "kusam", "step": "goal"} }

def reset_user(user_id):
    if user_id in user_states:
        del user_states[user_id]

def set_state(user_id, **kwargs):
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id].update(kwargs)

def get_state(user_id, key, default=None):
    return user_states.get(user_id, {}).get(key, default)

def handle_greeting(user_id):
    reset_user(user_id)
    set_state(user_id, step="goal")
    return greet_user()

# ================================
# Regex patterns
# ================================
greet_pattern = r"\b(hi|hello|hey|hai|halo)\b"

goal_patterns = {
    "bright": [r"\b(cerah|mencerahkan|bright|glow|glowing)\b"],
    "acne": [r"\b(acne|jerawat|pimple|bruntusan|komedo|breakout|pori)\b"],
    "antiaging": [r"\b(anti[- ]?aging|antiaging|keriput|wrinkle|tua|aging|garis halus|awet muda|kerutan|umur)\b"],
}

focus_patterns = {
    "kusam": r"\b(kusam|dull|pucat|gelap)\b",
    "bekas": r"\b(bekas|scar|mark|bekas jerawat|noda)\b",
    "hyper": r"\b(hyper|flek|dark spot|hiperpigmentasi)\b",
    "jerawat": r"\b(jerawat|acne|pimple|bruntusan|komedo|breakout)\b",
    "cegah": r"\b(cegah|prevent|pencegahan)\b",
    "visible": r"\b(visible|nampak|kelihatan|meradang|parah)\b",
}

type_patterns = {
    "sensitive": r"\b(sensitive|sensitif)\b",
    "normal": r"\b(normal)\b",
    "oily": r"\b(oily|berminyak|minyakan)\b",
}

# ================================
# Reflection kata ganti
# ================================
reflections = {
    "aku": "kamu",
    "saya": "kamu",
    "ku": "mu",
    "punyaku": "punyamu",
    "kamu": "aku",
    "anda": "saya",
    "punyamu": "punyaku",
}

def reflect_sentence(sentence: str) -> str:
    words = sentence.lower().split()
    reflected = [reflections.get(w, w) for w in words]
    return " ".join(reflected)

# ================================
# Greeting
# ================================
def greet_user():
    return (
        "Hai cantik, selamat datang di **SKINSOLVER** 💎\n"
        "Aku ada di sini buat bantu kamu temukan solusi terbaik untuk kulitmu— "
        "mulai dari mencerahkan, mengatasi jerawat, sampai anti-aging ✨.\n\n"
        "Coba ceritakan dulu yuk... goal utama kulitmu apa? 🌸"
    )

# ================================
# Responses
# ================================
responses = {
    "bright": {
        "ask_focus": "Baik, goal kamu mencerahkan kulit ✨. Lebih fokus ke **kusam, bekas jerawat, atau hiperpigmentasi**?",
        "focus_default": "Oke, jadi kamu ingin kulit lebih cerah 🌸. Supaya lebih spesifik, apakah lebih ke **kusam, bekas jerawat, atau hiperpigmentasi**?",
        "kusam": {
            "ask_type": "Kulit kusam ya ✨. Tipe kulitmu lebih ke **sensitive, normal, atau oily**?",
            "sensitive": [
                "Untuk kulit sensitif yang kusam, kamu bisa coba:\n"
                "🌿 5% Niacinamide + Moisture Sabi Beet Serum → cocok untuk kulit kering.\n"
                "💧 Revive Potion 3% Arbutin + Bakuchiol → cocok untuk kulit sedikit berminyak."
            ],
            "normal": ["Kulit normal kusam cocok dengan *10% Niacinamide + Moisture Sabi Beet Serum* 🌟"],
            "oily": ["Kalau kusam + berminyak, coba *Revive Potion 3% Arbutin + Bakuchiol* 💧"],
            "type_default": "Aku paham, tipe kulitmu unik ya 💕. Tapi kalau digeneralisasi, apakah lebih dekat ke **sensitive, normal, atau oily**?"
        },
        "bekas": [
            "Untuk bekas jerawat, *Dark Spot Reducer Ampoule* bisa jadi andalan 🌿",
            "Coba juga *Dark Spot Reducer Ampoule*, diformulasikan khusus untuk bantu samarkan bekas jerawat 🌞",
        ],
        "hyper": {
            "ask_type": "Mengatasi hiperpigmentasi memang butuh perhatian ekstra 🌸. Tipe kulitmu lebih ke **sensitive, normal, atau oily**?",
            "sensitive": ["Kulit sensitif dengan flek bisa lebih cocok pakai C-Riously 24K Gold Essence 💛"],
            "normal": ["Untuk kulit normal, bisa coba Lemonade Waterless Vitamin C + Ferulic + NAG 🍋✨"],
            "oily": ["Kalau kulitmu oily + flek, pas banget cobain Lemonade Waterless Vitamin C + Ferulic + NAG 🍋✨"],
            "type_default": "Oke cantik, kulitmu lebih condong ke **sensitive, normal, atau oily**?"
        },
    },
    "acne": {
        "ask_focus": "Oke, goal kamu mengatasi jerawat 🧴. Mau fokus ke **jerawat aktif, pencegahan, atau jerawat yang terlihat jelas**?",
        "focus_default": "Aku mengerti, tapi biar lebih spesifik 🌸. Apakah mau fokus ke **jerawat aktif, pencegahan, atau jerawat yang terlihat**?",
        "jerawat": ["Kalau jerawat komedoan → 2% BHA Salicylic Acid Liquid Perfector 🧴. Kalau merah/meradang → Bakuchiol Skinpair Oil Serum 🌿"],
        "cegah": ["Untuk pencegahan jerawat, pakai 60% Vita Propolis + Bee Venom Glow Serum 🐝✨ yang kuatkan skin barrier."],
        "visible": ["Jerawat kelihatan? Untuk harian → Hylapore Away Solution 👀✨. Untuk mingguan (1–3x) → AHA BHA Peeling Solution 🧪"],
    },
    "antiaging": {
        "ask_type": "Anti-aging itu investasi jangka panjang 💎. Tipe kulitmu lebih ke **sensitive, normal, atau oily**?",
        "sensitive": ["Untuk kulit sensitif, coba Granactive Snow Retinoid 2% ❄️✨. Aman buat pemula, bantu haluskan garis halus."],
        "normal": ["Kulit normal? Mulai dengan Level 1 Encapsulated Retinoid 💧. Kalau mau dosis tinggi → 1% Pure Retinol + Squalane ✨"],
        "oily": ["Kalau oily, mulai dengan Level 1 Encapsulated Retinoid ✨. Kalau sudah terbiasa → 1% Pure Retinol + Squalane 💧"],
        "type_default": "Aku ingin lebih pasti dulu ya. Tipe kulitmu lebih dekat ke **sensitive, normal, atau oily**?"
    },
}

# Fallback
default_fallbacks = [
    "Maaf, aku belum nangkep maksudnya 😊. Bisa ulangi dengan kata lain?",
    "Aku agak bingung nih ✨. Coba jelasin lagi, misalnya: 'mencerahkan' / 'jerawat' / 'anti-aging'.",
]

# ================================
# Detection helpers
# ================================
def detect_goal(message: str):
    for goal, pats in goal_patterns.items():
        for pat in pats:
            if re.search(pat, message, re.IGNORECASE):
                return goal
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
# Conversation flow
# ================================
def get_response(user_id, message: str):
    state = user_states.get(user_id, {})
    step = state.get("step")

    # STEP 1: Goal
    if step in [None, "goal"]:
        goal = detect_goal(message)
        if goal:
            if goal == "bright":
                set_state(user_id, goal=goal, step="focus")
                return responses["bright"]["ask_focus"]
            if goal == "acne":
                set_state(user_id, goal=goal, step="focus")
                return responses["acne"]["ask_focus"]
            if goal == "antiaging":
                set_state(user_id, goal=goal, step="type")
                return responses["antiaging"]["ask_type"]
        if step == "goal":
            return "Aku ingin lebih jelas dulu ✨. Goal kamu lebih ke **mencerahkan, jerawat, atau anti-aging**?"
        return random.choice(default_fallbacks)

    # STEP 2: Focus
    if step == "focus":
        goal = state.get("goal")
        focus = detect_focus(message)
        if not focus:
            return responses[goal]["focus_default"] if goal in responses else random.choice(default_fallbacks)

        if goal == "bright":
            if focus == "kusam":
                set_state(user_id, goal=goal, focus="kusam", step="type")
                return responses["bright"]["kusam"]["ask_type"]
            elif focus == "bekas":
                reply = random.choice(responses["bright"]["bekas"])
                reset_user(user_id)
                return reply
            elif focus == "hyper":
                set_state(user_id, goal=goal, focus="hyper", step="type")
                return responses["bright"]["hyper"]["ask_type"]

        if goal == "acne":
            if focus in responses["acne"]:
                reply = random.choice(responses["acne"][focus])
                reset_user(user_id)
                return reply
            return responses["acne"]["focus_default"]

    # STEP 3: Type
    if step == "type":
        goal = state.get("goal")
        focus = state.get("focus")
        t = detect_type(message)
        if not t:
            if goal == "bright" and focus in ["kusam", "hyper"]:
                return responses["bright"][focus]["type_default"]
            if goal == "antiaging":
                return responses["antiaging"]["type_default"]
            return "Kulitmu lebih condong ke **sensitive, normal, atau oily**?"
        if goal == "bright" and focus in ["kusam", "hyper"]:
            reply = random.choice(responses["bright"][focus][t])
            reset_user(user_id)
            return reply
        if goal == "antiaging":
            reply = random.choice(responses["antiaging"][t])
            reset_user(user_id)
            return reply

    # Fallback with reflection
    reflected = reflect_sentence(message)
    return f"Oke, jadi {reflected} ya? ✨"

# ================================
# Discord event handlers
# ================================
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    text = message.content.strip()
    if re.search(greet_pattern, text, re.IGNORECASE):
        reset_user(message.author.id)
        set_state(message.author.id, step="goal")
        await message.channel.send(greet_user())
        return
    response = get_response(message.author.id, text)
    if response:
        await message.channel.send(response)

# ================================
# Run bot
# ================================
if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not found.")
    else:
        client.run(TOKEN)
