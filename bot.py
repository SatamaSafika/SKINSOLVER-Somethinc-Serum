import os
import re
import random
import discord
from dotenv import load_dotenv
import logging

# ================================
# NOTES
# ================================
# - This bot uses `user_states` (in-memory dict) per user.
#   * All state is lost when the bot process is restarted (run ulang).
#   * After the bot gives a final recommendation, the user's state is reset.
#   * If user input doesn't match expected regex at any step, a default fallback message is returned.
#
# - Greeting is handled in on_message to avoid "double responses" / race conditions:
#   when user says "hai", the bot immediately replies greeting and returns (no other handlers run).
#
# - Put your DISCORD_TOKEN into a .env file or environment variable named DISCORD_TOKEN.


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
    """Remove stored state for a user (called after final recommendation or when greeting)."""
    if user_id in user_states:
        del user_states[user_id]

def set_state(user_id, **kwargs):
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id].update(kwargs)

def get_state(user_id, key, default=None):
    return user_states.get(user_id, {}).get(key, default)

def handle_greeting(user_id):
    """Fungsi untuk test greeting tanpa harus pakai Discord event."""
    reset_user(user_id)
    set_state(user_id, step="goal")
    return greet_user()


# ================================
# Regex patterns (flexible, bilingual)
# ================================
greet_pattern = r"\b(hi|hello|hey|hai|halo)\b"

goal_patterns = {
    "bright": [r"\b(cerah|mencerahkan|bright|glow|glowing)\b"],
    "acne": [r"\b(acne|jerawat|pimple|bruntusan|komedo|breakout|pori)\b"],
    "antiaging": [r"\b(anti[- ]?aging|antiaging|keriput|wrinkle|tua|aging|garis halus|awet muda|kerutan|umur)\b"],
}

focus_patterns = {
    # bright branch
    "kusam": r"\b(kusam|dull|pucat|gelap)\b",
    "bekas": r"\b(bekas|scar|mark|bekas jerawat|noda)\b",
    "hyper": r"\b(hyper|flek|dark spot|hiperpigmentasi|hiperpigmentasi)\b",
    # acne branch
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
# Responses (interactive style)
# ================================
responses = {
    "bright": {
        "ask_focus": "Baik, goal kamu mencerahkan kulit ✨. Lebih fokus ke **kusam, bekas jerawat, atau hiperpigmentasi**?",
        "focus_default": "Oke, jadi kamu ingin kulit lebih cerah 🌸. Supaya lebih spesifik, apakah lebih ke **kusam, bekas jerawat, atau hiperpigmentasi**?",
        "kusam": {
            "ask_type": "Kulit kusam ya ✨. Biar aku bisa kasih rekomendasi tepat, tipe kulitmu lebih ke **sensitive, normal, atau oily**?",
            "sensitive": [
                    "Untuk kulit sensitif yang kusam, kamu bisa coba:\n"
                    "🌿 5% Niacinamide + Moisture Sabi Beet Serum → cocok untuk kulit kering.\n"
                    "💧 Revive Potion 3% Arbutin + Bakuchiol → cocok untuk kulit sedikit berminyak.\n"
                    "Pilih sesuai kondisi kulitmu ya!"
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
            "sensitive": ["Kulit sensitif dengan flek bisa lebih cocok pakai C-Riously 24K Gold Essence 💛 Formula lembutnya bantu samarin flek tanpa bikin kulit iritasi, plus kasih efek cerah sehat dari 24K Gold."],
            "normal": ["Untuk kulit normal, bisa coba Lemonade Waterless Vitamin C + Ferulic + NAG 🍋✨ Kandungan vitamin C-nya bantu samarin flek, cerahkan kulit, dan jaga tekstur tetap sehat."],
            "oily": ["Kalau kulitmu oily + flek, pas banget cobain Lemonade Waterless Vitamin C + Ferulic + NAG 🍋✨ Bantu samarin noda hitam, cerahin kulit, sekaligus jaga produksi minyak tetap seimbang."],
            "type_default": "Oke cantik, biar lebih tepat aku perlu tahu dulu... kulitmu lebih condong ke **sensitive, normal, atau oily**?"
        },
    },
    "acne": {
        "ask_focus": "Oke, goal kamu mengatasi jerawat 🧴. Mau fokus ke **jerawat aktif, pencegahan, atau jerawat yang terlihat jelas**?",
        "focus_default": "Aku mengerti, tapi biar lebih spesifik 🌸. Apakah mau fokus ke **jerawat aktif, pencegahan, atau jerawat yang terlihat**?",
        "jerawat": ["Kalau jerawatnya tipe komedoan, cocok banget pakai 2% BHA Salicylic Acid Liquid Perfector 🧴 yang bantu bersihin pori dan kontrol minyak. Tapi kalau jerawatnya lebih merah/meradang, coba Bakuchiol Skinpair Oil Serum 🌿 karena lembut, calming, dan bantu redakan kemerahan."],
        "cegah": ["Untuk pencegahan jerawat, bisa pakai 60% Vita Propolis + Bee Venom Glow Serum 🐝✨ yang bantu kuatkan skin barrier sekaligus bikin kulit lebih sehat dan glowing."],
        "visible": ["Kalau jerawatnya kelihatan, untuk perawatan harian bisa pakai Hylapore Away Solution 👀✨ biar lebih cepat kalem. Kalau mau treatment mingguan 1–3x, bisa coba AHA BHA Peeling Solution 🧪 buat eksfoliasi dan samarin noda."],
    },
    "antiaging": {
        "ask_type": "Anti-aging itu investasi jangka panjang untuk kulitmu 💎. Tipe kulitmu lebih ke **sensitive, normal, atau oily**?",
        "sensitive": ["Untuk kulit sensitif kamu bisa pakai Granactive Snow Retinoid 2% ❄️✨. Formula lembutnya aman buat pemula, bantu haluskan garis halus tanpa bikin kulit gampang iritasi."],
        "normal": ["Kalau kulitmu normal, bisa mulai dengan Level 1 Encapsulated Retinoid 💧 yang lembut untuk pemula. Kalau sudah terbiasa dan mau dosis lebih tinggi, cobain 1% Pure Retinol + Squalane ✨ buat hasil anti-aging yang lebih maksimal."],
        "oily": ["Kalau kulitmu oily, bisa mulai dengan Level 1 Encapsulated Retinoid ✨ yang ringan & aman buat pemula. Kalau sudah terbiasa dan mau dosis lebih tinggi, cobain 1% Pure Retinol + Squalane 💧 buat hasil anti-aging lebih maksimal."],
        "type_default": "Okey, aku ingin lebih pasti dulu ya. Tipe kulitmu lebih dekat ke **sensitive, normal, atau oily**?"
    },
}

# Default fallback messages (randomized)
default_fallbacks = [
    "Maaf, aku belum nangkep maksudnya 😊. Kamu bisa ulangi dengan kata lain?",
    "Aku agak bingung nih ✨. Coba jelasin lagi, misalnya: 'mencerahkan' / 'jerawat' / 'anti-aging'.",
    "Coba pilih salah satu: **mencerahkan**, **jerawat**, atau **anti-aging** ✨"
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
# Conversation flow (no greeting handling here)
# ================================
def get_response(user_id, message: str):
    """
    Core state-driven response generator.
    Greeting is handled in on_message to avoid double-responses.
    """
    state = user_states.get(user_id, {})
    step = state.get("step")

    # --- STEP 1: Goal ---
    if step in [None, "goal"]:
        # If user_state absent, we still allow direct goal input (user typed "bright" without greeting)
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
        # didn't detect goal
        if step == "goal":
            # user was expected to answer goal but didn't
            return "Aku ingin lebih jelas dulu ✨. Goal kamu lebih ke **mencerahkan, jerawat, atau anti-aging**?"
        # No state & no goal: ask to greet or give goal (default fallback)
        return random.choice(default_fallbacks)

    # --- STEP 2: Focus ---
    if step == "focus":
        goal = state.get("goal")
        focus = detect_focus(message)

        if not focus:
            # fallback prompts specific to goal
            if goal == "bright":
                return responses["bright"]["focus_default"]
            if goal == "acne":
                return responses["acne"]["focus_default"]
            return random.choice(default_fallbacks)

        # handle bright focus
        if goal == "bright":
            if focus == "kusam":
                set_state(user_id, goal=goal, focus="kusam", step="type")
                return responses["bright"]["kusam"]["ask_type"]
            elif focus == "bekas":
                # final recommendation -> reset
                reply = random.choice(responses["bright"]["bekas"])
                reset_user(user_id)
                return reply
            elif focus == "hyper":
                set_state(user_id, goal=goal, focus="hyper", step="type")
                return responses["bright"]["hyper"]["ask_type"]
            else:
                return responses["bright"]["focus_default"]

        # handle acne focus: all acne focus lead to immediate recommendation
        if goal == "acne":
            # if detected one of jerawat/cegah/visible
            if focus in ["jerawat", "cegah", "visible"]:
                reply_list = responses["acne"].get(focus)
                reply = random.choice(reply_list) if reply_list else responses["acne"]["focus_default"]
                reset_user(user_id)
                return reply
            else:
                return responses["acne"]["focus_default"]

    # --- STEP 3: Type ---
    if step == "type":
        goal = state.get("goal")
        focus = state.get("focus")  # may be None for antiaging
        t = detect_type(message)

        if not t:
            # type missing; prompt accordingly
            if goal == "bright" and focus in ["kusam", "hyper"]:
                return responses["bright"][focus]["type_default"]
            if goal == "antiaging":
                return responses["antiaging"]["type_default"]
            return "Oke, aku ingin tahu lebih jelas 🌸. Kulitmu lebih condong ke **sensitive, normal, atau oily**?"

        # if we got a type
        if goal == "bright" and focus in ["kusam", "hyper"]:
            # pick a recommendation based on type
            reply_list = responses["bright"][focus].get(t)
            reply = random.choice(reply_list) if reply_list else responses["bright"][focus]["type_default"]
            reset_user(user_id)
            return reply

        if goal == "antiaging":
            reply_list = responses["antiaging"].get(t)
            reply = random.choice(reply_list) if reply_list else responses["antiaging"]["type_default"]
            reset_user(user_id)
            return reply

    # Fallback (should not usually reach here)
    return random.choice(default_fallbacks)

# ================================
# Discord event handlers
# ================================
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    # ignore bot's own messages
    if message.author == client.user:
        return

    text = message.content.strip()

    # 1) Greeting handler at top-level: reset and greet (stop further processing)
    if re.search(greet_pattern, text, re.IGNORECASE):
        # clear any previous state for a clean start
        reset_user(message.author.id)
        # set to waiting for goal (so next user message is treated as goal answer)
        set_state(message.author.id, step="goal")
        await message.channel.send(greet_user())
        return  # important: do not continue to get_response for this message

    # 2) Normal flow
    response = get_response(message.author.id, text)
    if response:
        await message.channel.send(response)

# ================================
# Run bot (hanya kalau main)
# ================================
if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not found. Put it in your environment or .env file.")
    else:
        client.run(TOKEN)
