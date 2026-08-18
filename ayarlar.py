import json
import os
import sys

AYARLAR_DOSYASI = "ayarlar.json"

def ayarlari_oku():
    if os.path.exists(AYARLAR_DOSYASI):
        with open(AYARLAR_DOSYASI, "r", encoding="utf-8") as f:
            ayarlar = json.load(f)
            
        # KRİTİK GÜVENLİK AĞI: Ayarlar var ama model dosyası silinmiş mi?
        model_dosyasi = ayarlar.get("model_dosya_adi", "")
        if not os.path.exists(model_dosyasi):
            print(f"KRİTİK HATA: Ayarlar dosyası mevcut ancak '{model_dosyasi}' bulunamadı!")
            print("Model dosyası silinmiş veya eski bir sürüm kalıntısı var.")
            print("Lütfen programı Setup dosyası üzerinden yeniden kurun.")
            sys.exit(1) # Çökmeyi engeller, güvenlice kapatır
            
        return ayarlar
        
    # Adam Program Files'a girip ayarlar dosyasını eliyle sildiyse:
    print("KRİTİK HATA: 'ayarlar.json' dosyası bulunamadı veya silinmiş!")
    print("Lütfen programı onarın veya yeniden kurun.")
    sys.exit(1)