import os
import threading
from llama_cpp import Llama
from ayarlar import MODEL_DOSYA_ADI

class YapayZekaMotoru:
    def __init__(self, model_yolu=f"./{MODEL_DOSYA_ADI}", n_gpu_layers=0):
        print("Motor ısınıyor, lütfen bekle...")
        cekirdek_sayisi = max(1, os.cpu_count() - 1)
        self.llm = Llama(
            model_path=model_yolu,
            n_ctx=2048,          # 40 mesajlık geçmiş + kısa promptlar için 4096 gereksiz, RAM'i rahatlatır
            n_gpu_layers=n_gpu_layers,  # Ekran kartı yok -> 0 (CPU'da bunu -1 yapmak fayda sağlamaz)
            n_batch=512,
            n_threads=cekirdek_sayisi,        # Cevap üretim (generation) thread sayısı
            n_threads_batch=cekirdek_sayisi,  # Prompt işleme (batch) thread sayısı - bunu ayarlamamak yavaşlatır
            use_mlock=False,     # RAM azsa True disk swap'ını önler ama RAM azsa açılışta hataya da yol açabilir
            verbose=False
        )
        # KRİTİK: llama.cpp'nin tek bir Llama nesnesi aynı anda yalnızca
        # 1 generation işlemini güvenle kaldırabilir. İki thread aynı anda
        # create_chat_completion çağırırsa KV-cache bozulur ve program
        # segfault ile aniden kapanır. Bu kilit tüm çağrıları sıraya sokar.
        # NOT: 2-4 çekirdekli bir CPU'da gerçek paralel üretim zaten anlamsız
        # olurdu (ikisi de aynı sınırlı çekirdekleri paylaşıp ikisi de yavaşlardı),
        # o yüzden sıralı (queued) işlem burada hem güvenlik hem performans
        # açısından doğru tasarım tercihidir.
        self.kilit = threading.Lock()
        self.bekleme_kilidi = threading.Lock()
        self.bekleyen_istek_sayisi = 0
        print("Motor arayüz bağlantısına hazır!")

    # İSMİNİ VE MANTIĞINI ARAYÜZE UYGUN OLARAK "BLOK" YAPTIK
    def yanit_uret_blok(self, sistem_istemi, mesaj_gecmisi, yeni_mesaj,
                         siraya_girdi_callback=None, uretim_basladi_callback=None):
        """
        Daktilo efektini iptal eder. Model arka planda cümlenin tamamını 
        üretip bitirene kadar bekler ve tek bir blok (string) olarak arayüze yollar.

        siraya_girdi_callback(sira_no): Bu istek kaç numaralı sırada bekliyor bildirir.
        uretim_basladi_callback(): Model gerçekten üretime başladığı an tetiklenir.
        Bu ikisi arayüzün "Sırada: 2. sırada" / "Yazıyor..." göstergesini
        doğru anda güncelleyebilmesi için var.
        """
        messages = [{"role": "system", "content": sistem_istemi}]
        
        for msg in mesaj_gecmisi:
            rol = "user" if msg.gonderen == "Kullanici" else "assistant"
            messages.append({"role": rol, "content": msg.mesaj_metni})
            
        messages.append({"role": "user", "content": yeni_mesaj})

        with self.bekleme_kilidi:
            self.bekleyen_istek_sayisi += 1
            benim_siram = self.bekleyen_istek_sayisi
        if siraya_girdi_callback:
            siraya_girdi_callback(benim_siram)

        try:
            # Aynı anda sadece 1 sohbet üretim yapabilir, diğerleri burada güvenle bekler.
            # Arayüz thread'i bu kilide takılmaz, çünkü kilit sadece worker thread'lerde.
            with self.kilit:
                if uretim_basladi_callback:
                    uretim_basladi_callback()
                response = self.llm.create_chat_completion(
                    messages=messages,
                    max_tokens=60,   # Sert üst sınır: WhatsApp mesajı gibi kısa (150 -> 60)
                    temperature=0.3,
                    stop=["\n\n"],   # Model paragraf araları ile uzamaya çalışırsa burada keser
                    stream=False
                )
        finally:
            with self.bekleme_kilidi:
                self.bekleyen_istek_sayisi -= 1

        return response["choices"][0]["message"]["content"]