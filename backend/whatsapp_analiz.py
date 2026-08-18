import re
import threading

_SATIR_DESENI = re.compile(r'^\[?(\d{1,2}[./]\d{1,2}[./]\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*(?:[AP]M)?\]?\s*[-–]?\s*([^:]+):\s?(.*)$')
_SISTEM_ANAHTAR_KELIMELER = ("medya dahil edilmedi", "<media omitted>", "bu mesaj silindi", "güvenlik numarası değişti", "grup simgesini değiştirdi", "grubu oluşturdu")



def whatsapp_analizini_arkaplanda_baslat(dosya_yolu, hedef_kisi_adi, basari_callback, hata_callback):
    """Arayüzü kilitlemeden analiz yapar ve sonucu arayüze (callback ile) iletir."""
    def gorev():
        try:
            mesajlar = whatsapp_disa_aktarimini_oku(dosya_yolu, hedef_kisi_adi)
            if not mesajlar:
                hata_callback(f"'{hedef_kisi_adi}' bulunamadı veya mesaj okunamadı.")
                return
            
            uslup_ozeti, ornekler = uslup_profili_olustur(mesajlar)
            basari_callback(hedef_kisi_adi, uslup_ozeti, ornekler, len(mesajlar))
        except Exception as hata:
            hata_callback(str(hata))
            
    # İşlemi arka planda başlatıyoruz
    threading.Thread(target=gorev, daemon=True).start()

def whatsapp_disa_aktarimini_oku(dosya_yolu, hedef_kisi_adi):
    mesajlar, su_anki_mesaj, su_anki_gonderen = [], None, None
    with open(dosya_yolu, "r", encoding="utf-8-sig", errors="ignore") as f:
        for ham_satir in f:
            satir = ham_satir.rstrip("\n")
            if not satir.strip(): continue
            eslesme = _SATIR_DESENI.match(satir)
            if eslesme:
                if su_anki_mesaj is not None and su_anki_gonderen == hedef_kisi_adi: mesajlar.append(su_anki_mesaj.strip())
                _, _, gonderen, icerik = eslesme.groups()
                gonderen = gonderen.strip()
                if any(k.lower() in icerik.lower() for k in _SISTEM_ANAHTAR_KELIMELER):
                    su_anki_mesaj, su_anki_gonderen = None, None
                    continue
                su_anki_gonderen, su_anki_mesaj = gonderen, icerik
            else:
                if su_anki_mesaj is not None: su_anki_mesaj += " " + satir.strip()
        if su_anki_mesaj is not None and su_anki_gonderen == hedef_kisi_adi: mesajlar.append(su_anki_mesaj.strip())
    return [m for m in mesajlar if m]

def uslup_profili_olustur(mesajlar, ornek_sayisi=20):
    if not mesajlar: return None, []
    toplam = len(mesajlar)
    ort_uzunluk = sum(len(m) for m in mesajlar) / toplam
    emoji_deseni = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF]")
    emoji_orani = sum(1 for m in mesajlar if emoji_deseni.search(m)) / toplam
    kisa_mesaj_orani = sum(1 for m in mesajlar if len(m) <= 15) / toplam
    buyuk_harf_orani = sum(1 for m in mesajlar if m.isupper() and len(m) > 3) / toplam

    ozellikler = []
    if ort_uzunluk < 20: ozellikler.append("çok kısa ve öz mesajlar yazar")
    elif ort_uzunluk < 50: ozellikler.append("orta uzunlukta, sohbet diliyle mesajlar yazar")
    else: ozellikler.append("uzun ve detaylı mesajlar yazmayı sever")

    if emoji_orani > 0.3: ozellikler.append("sık sık emoji kullanır")
    elif emoji_orani < 0.05: ozellikler.append("neredeyse hiç emoji kullanmaz")
    if kisa_mesaj_orani > 0.4: ozellikler.append('çoğu zaman tek kelimelik yanıtlar verir')
    if buyuk_harf_orani > 0.05: ozellikler.append("bazen tamamen büyük harfle vurgu yapar")

    uslup_ozeti = "Bu kişinin gerçek WhatsApp tarzı: " + "; ".join(ozellikler) + "."
    adim = max(1, toplam // ornek_sayisi)
    ornekler = [m for m in mesajlar[::adim] if len(m) < 200][:ornek_sayisi]
    return uslup_ozeti, ornekler