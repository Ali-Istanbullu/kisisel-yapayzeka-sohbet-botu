# --- SİSTEM YAPILANDIRMA AYARLARI ---

# GELİŞTİRİCİ MODU: 
# Kendi bilgisayarında kod yazarken ve test ederken True kalsın (Hafif 3B Modeli kullanır).
# Projeyi .exe yapıp GitHub'a yüklemeden hemen önce bunu False yap (Güçlü 7B Modeli devreye girer).
GELISTIRICI_MODU = True

if GELISTIRICI_MODU:
    MODEL_DOSYA_ADI = "qwen2.5-3b-instruct-q4_k_m.gguf"
    # Gerekirse ileride otomatik indirme fonksiyonu yazmak için linkleri de burada tutuyoruz
    MODEL_INDIRME_LINKI = "https://huggingface.co/RagnarokChan/Qwen2.5-3B-Instruct-Q4_K_M-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
else:
    MODEL_DOSYA_ADI = "qwen2.5-7b-instruct-q4_k_m.gguf"
    MODEL_INDIRME_LINKI = "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf"