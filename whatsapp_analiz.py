import re

# WhatsApp'ın iki yaygın dışa aktarım formatını da yakalar:
#   Android: "12.05.23, 14:23 - Ahmet: Selam"
#   iOS:     "[12.05.23, 14:23:01] Ahmet: Selam"
_SATIR_DESENI = re.compile(
    r'^\[?(\d{1,2}[./]\d{1,2}[./]\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*(?:[AP]M)?\]?\s*[-–]?\s*([^:]+):\s?(.*)$'
)

# Bunlar gerçek bir mesaj değil, WhatsApp'ın sistem/otomatik satırlarıdır - hariç tutulur
_SISTEM_ANAHTAR_KELIMELER = (
    "medya dahil edilmedi", "<media omitted>", "bu mesaj silindi",
    "this message was deleted", "güvenlik numarası değişti",
    "security code changed", "grup simgesini değiştirdi",
    "grubu oluşturdu", "sohbeti şifreledi", "changed the subject",
    "missed voice call", "missed video call", "kaçırılan sesli arama",
    "kaçırılan görüntülü arama",
)


def whatsapp_disa_aktarimini_oku(dosya_yolu, hedef_kisi_adi):
    """
    WhatsApp'ın 'Sohbeti Dışa Aktar' (.txt) dosyasını okur ve SADECE
    hedef_kisi_adi tarafından yazılmış mesajları liste olarak döner.
    hedef_kisi_adi, WhatsApp'ta kayıtlı görünen isimle BİREBİR eşleşmelidir.
    """
    mesajlar = []
    su_anki_mesaj = None
    su_anki_gonderen = None

    with open(dosya_yolu, "r", encoding="utf-8-sig", errors="ignore") as f:
        for ham_satir in f:
            satir = ham_satir.rstrip("\n")
            if not satir.strip():
                continue

            eslesme = _SATIR_DESENI.match(satir)
            if eslesme:
                # Yeni bir mesaj başlıyor -> öncekini kaydet (eğer hedef kişiye aitse)
                if su_anki_mesaj is not None and su_anki_gonderen == hedef_kisi_adi:
                    mesajlar.append(su_anki_mesaj.strip())

                _, _, gonderen, icerik = eslesme.groups()
                gonderen = gonderen.strip()

                if any(k.lower() in icerik.lower() for k in _SISTEM_ANAHTAR_KELIMELER):
                    su_anki_mesaj = None
                    su_anki_gonderen = None
                    continue

                su_anki_gonderen = gonderen
                su_anki_mesaj = icerik
            else:
                # Zaman damgası yok -> bu satır önceki (çok satırlı) mesajın devamıdır
                if su_anki_mesaj is not None:
                    su_anki_mesaj += " " + satir.strip()

        if su_anki_mesaj is not None and su_anki_gonderen == hedef_kisi_adi:
            mesajlar.append(su_anki_mesaj.strip())

    return [m for m in mesajlar if m]


def uslup_profili_olustur(mesajlar, ornek_sayisi=20):
    """
    Ham mesaj listesinden modelin bağlam penceresini şişirmeyecek kısa bir
    üslup özeti + temsili örnek mesajlar üretir. Bu metin, sistem promptuna
    eklenerek karaktere o kişinin gerçek yazışma tarzını kazandırır.
    """
    if not mesajlar:
        return None

    toplam = len(mesajlar)
    ort_uzunluk = sum(len(m) for m in mesajlar) / toplam

    emoji_deseni = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF]")
    emoji_orani = sum(1 for m in mesajlar if emoji_deseni.search(m)) / toplam
    kisa_mesaj_orani = sum(1 for m in mesajlar if len(m) <= 15) / toplam
    buyuk_harf_orani = sum(1 for m in mesajlar if m.isupper() and len(m) > 3) / toplam

    ozellikler = []
    if ort_uzunluk < 20:
        ozellikler.append("çok kısa ve öz mesajlar yazar")
    elif ort_uzunluk < 50:
        ozellikler.append("orta uzunlukta, sohbet diliyle mesajlar yazar")
    else:
        ozellikler.append("uzun ve detaylı mesajlar yazmayı sever")

    if emoji_orani > 0.3:
        ozellikler.append("sık sık emoji kullanır")
    elif emoji_orani < 0.05:
        ozellikler.append("neredeyse hiç emoji kullanmaz")

    if kisa_mesaj_orani > 0.4:
        ozellikler.append('çoğu zaman tek kelimelik veya çok kısa yanıtlar verir ("tmm", "ok", "aynen" gibi)')

    if buyuk_harf_orani > 0.05:
        ozellikler.append("bazen tamamen büyük harfle vurgu yapar")

    uslup_ozeti = "Bu kişinin gerçek WhatsApp yazışma tarzı: " + "; ".join(ozellikler) + "."

    # Temsili örnekler: baştan sona eşit aralıklarla seç (çeşitlilik için),
    # çok uzun mesajları (aşırı token maliyeti) örnek listesine almıyoruz.
    adim = max(1, toplam // ornek_sayisi)
    adaylar = mesajlar[::adim]
    ornekler = [m for m in adaylar if len(m) < 200][:ornek_sayisi]

    ornek_blogu = "\n".join(f'- "{m}"' for m in ornekler)

    return (
        f"{uslup_ozeti}\n\n"
        f"Gerçek mesajlarından örnekler (dil, kısalık ve tonu birebir bu şekilde taklit et):\n"
        f"{ornek_blogu}"
    )