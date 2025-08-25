import hashlib
import time

def _render_progress(attempt, total, start_ts):
    width = 30
    ratio = min(1.0, attempt / max(1, total))
    filled = int(ratio * width)
    bar = "█" * filled + "─" * (width - filled)
    elapsed = time.time() - start_ts
    hashrate = attempt / elapsed if elapsed > 0 else 0.0
    print(f"\r⛏️  [{bar}] {ratio*100:5.1f}% | {attempt}/{total} | {hashrate:,.0f} H/s", end="", flush=True)

def _mine_once(message, goal_prefix, max_attempts=200_000):
    nonce = 0
    start_ts = time.time()
    for attempt in range(1, max_attempts + 1):
        data = f"{message}{nonce}".encode()
        h = hashlib.sha256(data).hexdigest()
        if h.startswith(goal_prefix):
            elapsed = time.time() - start_ts
            _render_progress(attempt, max_attempts, start_ts)
            print()
            return True, nonce, h, attempt, elapsed
        nonce += 1
        if attempt % 1000 == 0 or attempt == max_attempts:
            _render_progress(attempt, max_attempts, start_ts)
    elapsed = time.time() - start_ts
    print()
    return False, None, None, max_attempts, elapsed

def _calculate_reward_btc(difficulty, attempts, elapsed_s):
    base = 0.000003 * (1.4 ** max(0, difficulty - 1))
    effort_factor = min(3.0, 0.75 + attempts / 120_000 + elapsed_s / 40_000)
    reward = base * effort_factor
    return round(min(reward, 0.0015), 8)

def mine_bitcoin_game(get_user_balance, add_user_balance, current_user_email):
    if not current_user_email:
        print("🔒 Önce giriş yapmalısınız (Sign In).")
        return

    print("\n💸💵 WELCOME TO MINING GAME 🤑💸💵")
    print("Not: Bu bir simülasyondur; gerçek PoW değildir.")

    while True:
        print("\n📌 MENU (Mining)")
        print("1 - Start New Round")
        print("2 - Show Local Wallet Balance")
        print("0 - Exit Mining")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("👋 Exiting mining...")
            break
        elif choice == "2":
            bal = get_user_balance(current_user_email)
            print(f"💰 Local Wallet Balance: {bal:.8f} BTC")
            continue
        elif choice != "1":
            print("❗ Geçersiz seçim.")
            continue

        sender_message = input("\nEnter message (any text): ")
        try:
            difficulty_level = int(input("Enter difficulty (number of leading zeros, e.g. 3–6): "))
            if difficulty_level < 1:
                difficulty_level = 1
        except:
            difficulty_level = 3

        goal = "0" * difficulty_level
        max_attempts = 200_000 + (difficulty_level - 1) * 150_000

        print(f"\n🎯 Target: hash starts with '{goal}'")
        print(f"🔁 Attempts planned: ~{max_attempts:,}")
        print("⏳ Mining... (Ctrl+C ile turu geçebilirsiniz)")

        try:
            found, nonce, h, attempts, elapsed = _mine_once(sender_message, goal, max_attempts)
        except KeyboardInterrupt:
            print("\n⏹️ Turu manuel olarak durdurdunuz.")
            found, nonce, h, attempts, elapsed = False, None, None, 0, 0.0

        if found:
            print(f"✅ Block found!")
            print(f"   Nonce : {nonce}")
            print(f"   Hash  : {h}")
            print(f"   Tries : {attempts:,} | Time: {elapsed:.2f}s")
            reward_btc = _calculate_reward_btc(difficulty_level, attempts, elapsed)
            add_user_balance(current_user_email, reward_btc)
            new_bal = get_user_balance(current_user_email)
            print(f"🎁 Reward: +{reward_btc:.8f} BTC")
            print(f"💼 New Local Balance: {new_bal:.8f} BTC")
        else:
            print(f"❌ Hedefe uyan hash bulunamadı. (Deneme: {attempts:,}, Süre: {elapsed:.2f}s)")
            consolation = round(0.25 * _calculate_reward_btc(difficulty_level, attempts, elapsed), 8)
            add_user_balance(current_user_email, consolation)
            new_bal = get_user_balance(current_user_email)
            print(f"🙂 Teselli ödülü: +{consolation:.8f} BTC")
            print(f"💼 New Local Balance: {new_bal:.8f} BTC")
