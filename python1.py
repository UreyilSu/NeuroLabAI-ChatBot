
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup

def mail_gonder(urun, fiyat):
    gonderen = "ureyilsusevval@gmail.com"
    alici = "ureyilsusevval@gmail.com"
    konu = "Fiyat Duyurusu 📉"
    mesaj = f"{urun}\n\nFiyat 33.000 TL altına düştü! Şu anki fiyat: {fiyat} TL"

    msg = MIMEText(mesaj)
    msg["Subject"] = konu
    msg["From"] = gonderen
    msg["To"] = alici

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gonderen, "fzuvbnqrttejipoz")
            server.send_message(msg)
            print("Mail gönderildi.")
    except Exception as e:
        print("Mail gönderilemedi:", e)

url = "https://www.amazon.com.tr/Apple-MacBook-depolama-ayd%C4%B1nlatmal%C4%B1-FaceTime/dp/B0DLHMLFZL/ref=sr_1_1_sspa?__mk_tr_TR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=L66GOCUZCCZF&dib=eyJ2IjoiMSJ9.nyu_5QdP1LleagJlvTPjfwkwfq54xyosH6_Nn4-TSJM5cWYM3fNvz-W7fiUDyO7vw-BIj8fESAZ6uL-oLe3Z-IG-sGUWj6LyyvpD4CRamurUFrn8-i7bNSD-veVO9XkQZMjok6E5Hzbsagqr8UtlIwCOpr94Fo4nLTQu0nYXW-TA-BA73j8amzzmjUr7DmaGbxyI8SdiYHZ1jzKF-EDv0MzxWzl8p2p6cUC94eCdHmlyMgun-NelIAZXCusnJefX7I0p1_OQPl4n_8tzd8RCaZBqGqwaR18mqfuWCuSVCfc.tpFAb9GxauH0dTFyC34LV2KK_308Jf-v5UrXe3_LTuw&dib_tag=se&keywords=macbook%2Bair%2Bm2&qid=1749659199&sprefix=macbook%2Bair%2Bm%2Caps%2C187&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"}

sayfa = requests.get(url, headers = headers)
icerik = BeautifulSoup(sayfa.content, "html.parser")

urunAdi = icerik.find(id= "productTitle").get_text().strip()
print("Ürün Adı:", urunAdi)

fiyat = icerik.find("span", class_="a-price-whole")
if fiyat:
    fiyat_str = fiyat.get_text().strip()

    fiyat_kusurat = icerik.find("span", class_="a-price-fraction")
    if fiyat_kusurat:
        fiyat_str += fiyat_kusurat.get_text().strip()
    
    fiyat_int = int(fiyat_str.replace(".", "").replace(",", ""))
    fiyat_kisa = fiyat_int // 100  # Son iki sıfırı atmak için bölme işlemi
    print("Fiyat (int, son iki sıfır atıldı):", fiyat_kisa)

    if fiyat_kisa < 33000:
        print("Fiyat 33.000 TL'nin altına düştü!")
        mail_gonder(urunAdi, fiyat_kisa)
    else:
        print("Henüz indirime girmemiştir.")
else:
    print("Fiyat bulunamadı.")

# Bu scripti 24 saatte bir çalıştırmak için cron (Linux/Mac) veya Task Scheduler (Windows) kullanabilirsiniz.