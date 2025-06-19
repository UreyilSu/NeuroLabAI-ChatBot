import requests
from bs4 import BeautifulSoup
import os
from flask import Flask, request, jsonify, render_template
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# ChatterBot nesnesi oluştur
chatbot = ChatBot('NeuroLabBot')

# Basit eğitim verisi ile eğit
trainer = ListTrainer(chatbot)
trainer.train([
    "merhaba",  
    "Merhaba! Size nasıl yardımcı olabilirim?",
    "nasılsın",
    "İyiyim, teşekkürler! Sen nasılsın?",
    "teşekkür ederim",
    "Rica ederim!",
    "okul nerede?",
    "İstanbul Medeniyet Üniversitesi, Üsküdar'da bulunmaktadır.",
    "çalışma saatleri nedir?",
    "Okulun çalışma saatleri 08:30 - 17:30 arasındadır."
])

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app = Flask(__name__, template_folder=template_dir)

def get_duyurular():
    url = "https://www.medeniyet.edu.tr/tr/duyurular"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    duyurular = []
    for item in soup.select("div.media-body a"):
        baslik = item.select_one("div.content-img p")
        link = item["href"]
        if baslik:
            tam_link = f"https://www.medeniyet.edu.tr{link}"
            duyurular.append(f"{baslik.get_text(strip=True)}\nDaha fazla: {tam_link}")
    return duyurular

def get_haberler():
    url = "https://www.medeniyet.edu.tr/tr/haberler"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    haberler = []
    for card in soup.select("div.media-wrapper a"):
        baslik = card.select_one("h5.title")
        link = card["href"]
        if baslik:
            tam_link = f"https://www.medeniyet.edu.tr{link}"
            haberler.append(f"{baslik.get_text(strip=True)}\nDaha fazla: {tam_link}")
    return haberler

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/hakkinda")
def hakkinda():
    return "Bu bir okul chatbot uygulamasıdır."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mesaj = data.get("message", "").lower()

    # ChatterBot'a basit sohbeti denetlet
    response = chatbot.get_response(mesaj)
    if float(response.confidence) > 0.5:
        cevap = str(response)
    else:
        if "sınav" in mesaj:
            cevap = "Sınavlar 17 Haziran haftasında başlıyor."
        elif "duyuru" in mesaj:
            try:
                duyurular = get_duyurular()
                if duyurular:
                    cevap = "Güncel duyurulardan bazıları:\n\n" + "\n\n".join(duyurular[:5])
                else:
                    cevap = "Hiç duyuru bulunamadı."
            except Exception as e:
                cevap = f"Duyurular alınamadı: {e}"
        elif "haber" in mesaj:
            try:
                haberler = get_haberler()
                if haberler:
                    cevap = "Güncel haberlerden bazıları:\n\n" + "\n\n".join(haberler[:5])
                else:
                    cevap = "Hiç haber bulunamadı."
            except Exception as e:
                cevap = f"Haberler alınamadı: {e}"
        elif any(kelime in mesaj for kelime in ["medeniyet", "etkinlik"]):
            try:
                r = requests.get("https://etkinlikler.medeniyet.edu.tr/Takvim/JSON-Liste/", headers={"User-Agent": "Mozilla/5.0"})
                data = r.json()
                if data:
                    ilk_uc = data[:3]
                    cevap = "Güncel etkinliklerden bazıları:\n\n"
                    for etkinlik in ilk_uc:
                        ad = etkinlik.get("Etkinlik", "Etkinlik adı yok")
                        tarih = etkinlik.get("BaslamaTarihi", "Tarih yok")
                        yer = etkinlik.get("Yer", "")
                        cevap += f"- {ad} ({tarih}) {yer}\n\n"
                else:
                    cevap = "Hiç etkinlik bulunamadı."
            except Exception as e:
                cevap = f"Etkinlik verileri alınamadı: {e}"
        else:
            cevap = "Bu konuda henüz bilgim yok."

    return jsonify({"answer": cevap})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)