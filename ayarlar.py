import json
import os

AYARLAR_DOSYASI = "ayarlar.json"

def ayarlari_oku():
    if os.path.exists(AYARLAR_DOSYASI):
        with open(AYARLAR_DOSYASI, "r", encoding="utf-8") as f:
            ayarlar = json.load(f)
            
        model_dosyasi = ayarlar.get("model_dosya_adi", "")
        if not os.path.exists(model_dosyasi):
            # sys.exit(1) YERİNE HATA FIRLATIYORUZ!
            raise FileNotFoundError(f"Kritik Hata: Ayarlar dosyası mevcut ancak '{model_dosyasi}' bulunamadı!\n\nModel dosyası silinmiş veya taşınmış olabilir. Lütfen programı yeniden kurun.")
            
        return ayarlar
        
    # sys.exit(1) YERİNE HATA FIRLATIYORUZ!
    raise FileNotFoundError("Kritik Hata: 'ayarlar.json' dosyası bulunamadı!\n\nLütfen programı onarın veya yeniden kurun.")