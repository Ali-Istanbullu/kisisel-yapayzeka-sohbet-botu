import json
import os
import glob

AYARLAR_DOSYASI = "ayarlar.json"

def ayarlari_oku():
    # 1. GÜVENLİK AĞI: Dosya yoksa DİNAMİK olarak yarat!
    if not os.path.exists(AYARLAR_DOSYASI):
        # Klasördeki .gguf uzantılı modeli otomatik bul
        mevcut_modeller = glob.glob("*.gguf")
        
        # Eğer klasörde bir gguf dosyası bulursa onun adını al, bulamazsa boş bırak
        dinamik_model_adi = mevcut_modeller[0] if mevcut_modeller else ""

        varsayilan_ayarlar = {
            "model_dosya_adi": dinamik_model_adi, 
            "gpu_kullanimi": False
        }
        
        with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(varsayilan_ayarlar, f, indent=4, ensure_ascii=False)
            
    # 2. Dosyayı güvenle oku
    with open(AYARLAR_DOSYASI, "r", encoding="utf-8") as f:
        ayarlar = json.load(f)
        
    # 3. Model dosyası fiziksel olarak var mı kontrol et
    model_dosyasi = ayarlar.get("model_dosya_adi", "")
    if not os.path.exists(model_dosyasi):
        raise FileNotFoundError(f"Kritik Hata: Ayarlar dosyası mevcut ancak '{model_dosyasi}' bulunamadı!\n\nModel dosyası silinmiş veya taşınmış olabilir. Lütfen programı yeniden kurun.")
        
    return ayarlar