import os
import threading
from llama_cpp import Llama
from ayarlar import ayarlari_oku

class YapayZekaMotoru:
    def __init__(self):
        print("Motor ısınıyor, lütfen bekle...")
        ayarlar = ayarlari_oku()
        model_yolu = f"./{ayarlar['model_dosya_adi']}"
        cekirdek_sayisi = max(1, os.cpu_count() - 1)
        n_gpu_layers = -1 if ayarlar.get("gpu_kullanimi", False) else 0

        self.llm = Llama(
            model_path=model_yolu, n_ctx=2048, n_gpu_layers=n_gpu_layers, n_batch=512,
            n_threads=cekirdek_sayisi, n_threads_batch=cekirdek_sayisi, use_mlock=False, verbose=False
        )
        self.kilit = threading.Lock()
        self.bekleme_kilidi = threading.Lock()
        self.bekleyen_istek_sayisi = 0
        print("Motor arayüz bağlantısına hazır!")

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