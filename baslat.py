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
    
    # Görünmez bir ana pencere oluştur (sadece hata kutusu görünsün diye)
    root = tk.Tk()
    root.withdraw() 
    
    # Ekrana Windows'un orijinal "Çarpı" ikonlu hata mesajını bas!
    messagebox.showerror("Sistem Hatası - AI Sohbet Botu", str(hata))
    
    # Kullanıcı "Tamam"a bastıktan sonra programı güvenlice kapat
    sys.exit(1)