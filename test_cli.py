# test_cli.py
from bot import get_response, user_states

def run_cli():
    print("Selamat datang di SKINSOLVER CLI")
    print("Ketik 'exit' untuk keluar.\n")

    user_id = 1  # simulasi ID user

    while True:
        msg = input("Kamu: ")
        if msg.lower() in ["exit", "quit"]:
            print("Bot: Makasih ya udah ngobrol sama SKINSOLVER 💖")
            break

        response = get_response(user_id, msg)
        if response:
            print(f"Bot: {response}")
        else:
            print("Bot: Hm, aku kurang paham maksud kamu😅")

if __name__ == "__main__":
    run_cli()
