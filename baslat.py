import sys
import tkinter as tk
import tkinter.messagebox as messagebox

try:
    from frontend.arayuz import YapayZekaUygulamasi

    if __name__ == "__main__":
        uygulama = YapayZekaUygulamasi()
        uygulama.mainloop()

except Exception as hata:
    # Eğer uygulamanın herhangi bir yerinde (örneğin ayarlar okunurken) hata çıkarsa buraya düşer.
    # Bu artık SADECE mesaj kutusuna değil, kalıcı log dosyasına da tam
    # stack trace ile yazılıyor - kullanıcı ekran görüntüsü yerine
    # hatalar.log dosyasını gönderebilir, teşhis çok daha kolay olur.
    try:
        from loglama import hata_logla, LOG_DOSYA_YOLU
        hata_logla("Uygulama açılışta çöktü (baslat.py)")
        log_yolu_notu = f"\n\nDetaylar için log dosyası:\n{LOG_DOSYA_YOLU}"
    except Exception:
        # loglama.py'nin kendisi bile import edilemiyorsa (çok nadir, örn.
        # proje klasörü bozuksa) en azından orijinal hatayı göstermeye devam et.
        log_yolu_notu = ""

    # Görünmez bir ana pencere oluştur (sadece hata kutusu görünsün diye)
    root = tk.Tk()
    root.withdraw() 
    
    # Ekrana Windows'un orijinal "Çarpı" ikonlu hata mesajını bas!
    messagebox.showerror("Sistem Hatası - AI Sohbet Botu", str(hata) + log_yolu_notu)
    
    # Kullanıcı "Tamam"a bastıktan sonra programı güvenlice kapat
    sys.exit(1)