import json
import os
import glob
import sys
from pathlib import Path

# 1. AYAR DOSYASININ YERİ APPDATA OLMALI (Yazma izni duvarını aşmak için)
if sys.platform.startswith("win"):
    ayar_klasoru = Path(os.getenv("APPDATA", ".")) / "YapayZekaSohbetBotu"
else:
    ayar_klasoru = Path.home() / ".yapayzekasohbetbotu"

ayar_klasoru.mkdir(parents=True, exist_ok=True)
AYARLAR_DOSYASI = ayar_klasoru / "ayarlar.json"

def ayarlari_oku():
    # 2. GÜVENLİK AĞI: Dosya APPDATA'da yoksa dinamik olarak yarat!
    if not os.path.exists(AYARLAR_DOSYASI):
        # Modeli exe'nin bulunduğu Program Files klasöründe (yanında) ara
        mevcut_modeller = glob.glob("*.gguf")
        dinamik_model_adi = mevcut_modeller[0] if mevcut_modeller else ""

        varsayilan_ayarlar = {
            "model_dosya_adi": dinamik_model_adi, 
            "gpu_kullanimi": False
        }
        
        with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(varsayilan_ayarlar, f, indent=4, ensure_ascii=False)
            
    # 3. Dosyayı güvenle oku
    with open(AYARLAR_DOSYASI, "r", encoding="utf-8") as f:
        ayarlar = json.load(f)
        
    # 4. Model dosyası fiziksel olarak exe'nin yanında var mı kontrol et
    model_dosyasi = ayarlar.get("model_dosya_adi", "")
    if not os.path.exists(model_dosyasi):
        raise FileNotFoundError(f"Kritik Hata: Ayarlar dosyası mevcut ancak '{model_dosyasi}' bulunamadı!\n\nModel dosyası silinmiş veya taşınmış olabilir. Lütfen programı yeniden kurun.")
        
    return ayarlar