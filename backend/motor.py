import os
import threading
from llama_cpp import Llama
from ayarlar import ayarlari_oku
from database.veritabani_islemleri import mesaj_gecmisini_getir, karakter_bilgisi_getir, hafiza_guncelle, mesajlari_sil
from loglama import hata_logla, bilgi_logla


class YapayZekaMotoru:

    def dinamik_hafiza_kontrolu(self, karakter_id):
        # Bu fonksiyon arayuz.py tarafından ayrı bir arka plan thread'inde,
        # "fire and forget" şekilde çağrılıyor (kimse sonucunu beklemiyor).
        # Bu yüzden try/except OLMAZSA burada patlayan bir hata hiçbir yere
        # loglanmadan sessizce kaybolur - konsolda bile görünmeyebilir.
        try:
            # Hangi modelin yüklü olduğunu ayarlardan çekiyoruz
            ayarlar = ayarlari_oku()
            model_adi = ayarlar.get("model_dosya_adi", "").lower()

            # Donanıma göre dinamik sınırları belirliyoruz
            if "14b" in model_adi:
                MAX_MESAJ_SINIRI, OZETLENECEK_SAYI = 80, 40
            elif "7b" in model_adi:
                MAX_MESAJ_SINIRI, OZETLENECEK_SAYI = 40, 20
            else:
                MAX_MESAJ_SINIRI, OZETLENECEK_SAYI = 20, 10

            # Veritabanı ve özetleme işlemleri
            mesajlar = mesaj_gecmisini_getir(karakter_id)
            if len(mesajlar) > MAX_MESAJ_SINIRI:
                eski_mesajlar = mesajlar[:OZETLENECEK_SAYI]
                yeni_mesajlar_metni = "\n".join([f"{m.gonderen}: {m.mesaj_metni}" for m in eski_mesajlar])
                karakter = karakter_bilgisi_getir(karakter_id)
                eski_hafiza = karakter.uzun_donem_hafiza or "Henüz bir geçmiş yok."

                yeni_ozet = self.hafiza_ozeti_olustur(eski_hafiza, yeni_mesajlar_metni)
                hafiza_guncelle(karakter_id, yeni_ozet)
                mesajlari_sil([m.id for m in eski_mesajlar])
        except Exception:
            hata_logla(f"dinamik_hafiza_kontrolu (karakter_id={karakter_id})")

    def __init__(self):
        print("Motor ısınıyor, lütfen bekle...")
        try:
            ayarlar = ayarlari_oku()
            model_yolu = f"./{ayarlar['model_dosya_adi']}"
            cekirdek_sayisi = max(1, os.cpu_count() - 1)
            n_gpu_layers = -1 if ayarlar.get("gpu_kullanimi", False) else 0

            self.llm = Llama(
                model_path=model_yolu, n_ctx=2048, n_gpu_layers=n_gpu_layers, n_batch=512,
                n_threads=cekirdek_sayisi, n_threads_batch=cekirdek_sayisi, use_mlock=False, verbose=False
            )
        except Exception:
            # Motor hiç açılamıyorsa uygulama da açılamaz - bu yüzden burada
            # YUTMUYORUZ, sadece loglayıp tekrar fırlatıyoruz (raise). Böylece
            # hem kalıcı log dosyasına yazılır hem de baslat.py'deki üst
            # seviye hata penceresi kullanıcıya gösterilmeye devam eder.
            hata_logla("YapayZekaMotoru başlatılamadı (model yüklenemedi)")
            raise

        self.kilit = threading.Lock()
        self.bekleme_kilidi = threading.Lock()
        self.bekleyen_istek_sayisi = 0
        print("Motor arayüz bağlantısına hazır!")
        bilgi_logla(f"Motor başarıyla başlatıldı (model: {ayarlar.get('model_dosya_adi', '?')})")

    def yanit_uret_blok(self, sistem_istemi, mesaj_gecmisi, yeni_mesaj, siraya_girdi_callback=None, uretim_basladi_callback=None):
        messages = [{"role": "system", "content": sistem_istemi}]
        for msg in mesaj_gecmisi:
            rol = "user" if msg.gonderen == "Kullanici" else "assistant"
            messages.append({"role": rol, "content": msg.mesaj_metni})
        messages.append({"role": "user", "content": yeni_mesaj})

        with self.bekleme_kilidi:
            self.bekleyen_istek_sayisi += 1
            benim_siram = self.bekleyen_istek_sayisi
        if siraya_girdi_callback: siraya_girdi_callback(benim_siram)

        # NOT: Burada bilinçli olarak try/except YOK - hata burada YUTULMUYOR,
        # çağıran (arayuz.py'deki bot_yaniti_bekle) kendi try/except'inde
        # yakalayıp hem loglayacak hem kullanıcıya "Cevap üretilemedi" gösterecek.
        # İki katmanda da loglarsak aynı hata log dosyasına iki kez yazılırdı.
        try:
            with self.kilit:
                if uretim_basladi_callback: uretim_basladi_callback()
                response = self.llm.create_chat_completion(
                    messages=messages, max_tokens=60, temperature=0.3, stop=["\n\n"], stream=False
                )
        finally:
            with self.bekleme_kilidi: self.bekleyen_istek_sayisi -= 1

        return response["choices"][0]["message"]["content"]

    def hafiza_ozeti_olustur(self, eski_hafiza, yeni_mesajlar_metni):
        """Kilit sistemini bozmadan arka planda hafıza özeti üretir."""
        sistem_istemi = "Sen bir hafıza özetleyicisin. Verilen eski özet ile yeni konuşmaları birleştirip, önemli olayları tek bir kısa paragrafta özetle. Yorum yapma."
        kullanici_istemi = f"[Eski Özet]:\n{eski_hafiza}\n\n[Yeni Konuşmalar]:\n{yeni_mesajlar_metni}\n\nLütfen güncel ve kısa bir özet oluştur."

        with self.kilit:
            response = self.llm.create_chat_completion(
                messages=[{"role": "system", "content": sistem_istemi}, {"role": "user", "content": kullanici_istemi}],
                max_tokens=150, temperature=0.2, stream=False
            )
        return response["choices"][0]["message"]["content"].strip()