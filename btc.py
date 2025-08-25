import requests
import smtplib
import matplotlib.pyplot as plt 
from datetime import datetime
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
import json
import random
import os 
import hashlib






USERS_FILE =  "users.json"
CURRENT_USER_EMAIL = ""

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users): 
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)
def get_user_balance(email):
    users = load_users()
    return users.get(email, {}).get("balance", 0.0)

def add_user_balance(email, amount):
    users = load_users()
    if email not in users:
        users[email] = {"password": "", "balance": 0.0}
    users[email]["balance"] = users[email].get("balance", 0.0) + amount
    save_users(users)

def bitcoin_fiyati_goster():
    try:
        url = "https://blockchain.info/ticker"
        response = requests.get(url)
        data = response.json()
        btc_usd = data["USD"]["last"]
        btc_try = data["TRY"]["last"]
        print(f"\n🔹 BTC/USD: ${btc_usd}")
        print(f"🔹 BTC/TRY: ₺{btc_try}")
    except:
        print("⚠️ Bitcoin fiyatı alınamadı. Lütfen bağlantınızı kontrol edin.")

def cüzdan_bakiyesi_goster():
    address = input("📩 Bitcoin cüzdan adresini girin: ")
    try:
        url = f"https://blockchain.info/rawaddr/{address}"
        response = requests.get(url)
        data = response.json()
        balance_btc = data["final_balance"] / 1e8
        print(f"🔸 Cüzdan Bakiyesi: {balance_btc} BTC")
    except:
        print("⚠️ Cüzdan bakiyesi alınamadı. Adresi kontrol edin.")

def bitcoin_grafigi_goster():
    try:
        url = "https://api.blockchain.info/charts/market-price?timespan=30days&format=json"
        response = requests.get(url)
        data = response.json()

        x = [datetime.fromtimestamp(point['x']) for point in data['values']]
        y = [point['y'] for point in data['values']]

        plt.plot(x, y)
        plt.title("Bitcoin USD Fiyatı (Son 30 Gün)")
        plt.xlabel("Tarih")
        plt.ylabel("Fiyat (USD)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except:
        print("⚠️ Grafik alınamadı. Lütfen bağlantınızı kontrol edin.")


def give_advice():
    try:
        # 1. Get current price
        ticker_url = "https://blockchain.info/ticker"
        current_data = requests.get(ticker_url).json()
        current_price = current_data["USD"]["last"]

        # 2. Get 7-days-ago price (daily average)
        history_url = "https://api.blockchain.info/charts/market-price?timespan=7days&rollingAverage=24hours&format=json"
        history_data = requests.get(history_url).json()
        first_price = history_data["values"][0]["y"]

        # 3. Calculate change
        percent_change = ((current_price - first_price) / first_price) * 100

        # 4. Print info
        print(f"\n7 days ago bitcoin price: ${first_price:.2f}")
        print(f"Currently bitcoin: ${current_price:.2f}")
        print(f"Change: {percent_change:.2f}%")

        # 5. Determine advice
        advice = ""
        if percent_change > 7:
            advice = "Price is rising rapidly. This rise may be followed by a decline."
        elif percent_change > 3:
            advice = "Trend follows up. Nonetheless, it's best to be careful."
        elif percent_change > -3:
            advice = "The market is trading sideways. Uncertainty prevails."
        elif percent_change > -7: 
            advice = "The price decline continues, there may be a buying opportunity."
        else:
            advice = "The price dropped rapidly, dropping may continue. Stay safe and be careful."

        print(f"Advice: {advice}")

        # 6. Prepare email content
        subject = "Daily Bitcoin Advice"
        body = f"""Hello,

7 days ago bitcoin price: ${first_price:.2f}
Currently bitcoin: ${current_price:.2f}
Change: {percent_change:.2f}%

Advice: {advice}

Stay informed!
"""
        # Send the email
        send_mail(subject, body, to_email, from_email, app_password)

    except Exception as e:
        print("No advice received. Check your internet connection.")
        print("ERROR:", e)


def send_mail(subject, body, to_email, from_email, app_password):
    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # SMTP sunucusuna bağlan
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Güvenli bağlantı başlat
        server.login(from_email, app_password)

        # Mail gönder
        server.send_message(msg)
        server.quit()



        print("✅ Mail başarıyla gönderildi.")
        return True

    except smtplib.SMTPAuthenticationError:
        print("Authantication error. Check the app password.")
        return False
    except Exception as e:
        print("Error occured while send mail.")    
        return False


               
from_email = "tarikkeskinofficial@gmail.com"
app_password = "mkmw qeiq aiml wkak"
to_email = "ktarikemre@hotmail.com"
subject = "Daily Bitcoin Advices"
body = "Bugün Bitcoin fiyatını takip etmeyi unutma! 📈"

def price_alert():
    try:
        target_price = float(input("🔔 Set your target BTC price in USD: "))
        print("📡 Fetching current BTC price...")

        url = "https://blockchain.info/ticker"
        response = requests.get(url)
        data = response.json()

        current_price = data["USD"]["last"]
        print(f"📊 Current BTC Price: ${current_price}")

        if current_price <= target_price:
            print("🚨 Alert: BTC price has dropped below your target!")

            subject = "📉 Bitcoin Price Alert"
            body = f"Alert! Bitcoin price has fallen to ${current_price}, which is below your target of ${target_price}."
            send_mail(subject, body, to_email, from_email, app_password)
        else:
            print("✅ BTC price is still above your target. No alert triggered.")

    except ValueError:
        print("❗ Invalid number format. Please enter a valid number.")
    except Exception as e:
        print("⚠️ Error occurred while checking price or sending mail.")
        print("Detail:", e)


def sign_in():
    global CURRENT_USER_EMAIL
    users = load_users()
    print("\n🔑 --- Sign In ---")
    email = input("E-mail: ").strip()
    if email not in users:
        print("⚠️ Bu e-mail kayıtlı değil. Kayıt ekranına yönlendiriliyorsunuz.")
        sign_up()
        return False

    password = input("Password: ").strip()
    if users[email]["password"] == password:
        print("✅ Giriş başarılı. Hoş geldiniz!")
        CURRENT_USER_EMAIL = email
        return True
    else:
        print("❌ Şifre hatalı.")
        return False



def sign_up():
    users = load_users()
    print("\n📩 --- Sign Up ---")
    email = input("E-mail: ").strip()
    if email in users:
        print("⚠️ Bu e-mail zaten kayıtlı. Lütfen giriş yapın.")
        

    password = input("Password: ").strip()

    # 6 haneli doğrulama kodu üret
    verification_code = str(random.randint(100000, 999999))

    # Kodu e-posta ile gönder
    subject = "Verification Code"
    body = f"Your verification code is: {verification_code}"
    if send_mail(subject, body, email, from_email, app_password):
        print(f"✅ Doğrulama kodu {email} adresine gönderildi.")
    else:
        print("⚠️ Doğrulama kodu gönderilemedi. Kayıt iptal edildi.")
        
        

    # Kullanıcıdan kodu alma
    entered_code = input("Enter the 6-digit verification code: ").strip()
    if entered_code == verification_code:
        users[email] = {"password": password, "balance": 0.0}
        save_users(users)
        print("✅ Kayıt başarılı! Giriş yapabilirsiniz.")
    else:
        print("❌ Yanlış doğrulama kodu. Kayıt başarısız.")
          
        
def ana_menu():
    while True:
        print("\n🔷 BLOCKCHAIN CONSOLE APP 🔷")
        print("1 - Show Bitcoin Price")
        print("2 - Show Wallet Balance")
        print("3 - Bitcoin Graphic (30 Days)")
        print("4 - Get an advice (last 7 days analysis for data)")
        print("5 - Set and Check Price Alert (BTC/USD)")
        print("6 - Mine Bitcoin Game")
        print("0 - Exit")

        selection = input("Please enter an option: ")

        if selection== "1":
            bitcoin_fiyati_goster()
        elif selection== "2":
            cüzdan_bakiyesi_goster()
        elif selection== "3":
            bitcoin_grafigi_goster()
        elif selection== "4":
            give_advice()
        elif selection== "5":
            price_alert()    
        elif selection == "6":
            from mining_game import mine_bitcoin_game
            mine_bitcoin_game(get_user_balance, add_user_balance, CURRENT_USER_EMAIL)    
        elif selection== "0":
            print("Exiting...")
            time.sleep(1)
            break
        else:
            print("❗ Invalid selection. Please enter between 0-5.")

# Programı başlat

def sign_in_up():
    while True:
        print("1 - Sign In")
        print("2 - Sign Up")
        print("0 - Exit")
        # print("📂 Çalışma dizini:", os.getcwd())  # Programın çalıştırıldığı klasör
        # print("📄 users.json tam yolu:", os.path.abspath(USERS_FILE))  # Dosyanın tam yolu
        # print("📦 Dosya mevcut mu? ->", os.path.exists(USERS_FILE))
        
        selection = input("Please enter the option: ")

        if selection == "1":
            if sign_in():
                ana_menu()
        elif selection == "2":
            sign_up()
        elif selection == "0":
            print("Exiting...")
            time.sleep(1)
            break
        else:
            print("❗ Invalid selection. Please enter between 0-2.")

sign_in_up()