import customtkinter as ctk
from tkinter import filedialog
import threading
from veritabani_islemleri import (
    kullanici_profilini_getir, 
    kullanici_profili_kaydet_veya_guncelle,
    mesaj_ekle_ve_buda,
    mesaj_gecmisini_getir,
    tum_karakterleri_getir,
    karakter_bilgisi_getir,
    karakter_ekle
)
from whatsapp_analiz import whatsapp_disa_aktarimini_oku, uslup_profili_olustur


# Motorumuzu dahil ediyoruz
from motor import YapayZekaMotoru

# Her ilişki rolünün küçük modele NET davranışsal talimat vermesi için açıklama tablosu.
# Sadece "Sevgilisin" demek yetmiyor; model bunun ne anlama geldiğini bilmeli.
ROL_ACIKLAMALARI = {
    "Arkadaş": (
        "Kullanıcının yakın, samimi ve güvenilir bir arkadaşısın. Rahat, sıcak, "
        "esprili ve destekleyici konuşursun. Aranızda hiçbir romantik şey yoktur, "
        "saf bir dostluk ilişkisi vardır."
    ),
    "Sevgili": (
        "Kullanıcının romantik partneri, sevgilisisin. Bunu her mesajında hatırla. "
        "Ona karşı sevgi dolu, şefkatli, flörtöz ve duygusal bağ kuran bir üslupla "
        "konuşursun; onu özlediğini ve önemsediğini hissettirirsin. Karakterinin "
        "kişiliğine uygun bir dozda sevgi ifadeleri kullanabilirsin."
    ),
    "Mentor": (
        "Kullanıcının tecrübeli, bilge bir rehberisin. Yol gösterir, öğüt verirsin; "
        "sabırlı, olgun ve teşvik edici bir üslupla konuşursun."
    ),
    "Asistan": (
        "Kullanıcının kişisel asistanısın. Net, yardımsever ve verimli konuşursun; "
        "işlerini kolaylaştırmaya odaklanırsın, gereksiz laf kalabalığı yapmazsın."
    ),
}


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class YapayZekaUygulamasi(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI WhatsApp Klonu")
        self.geometry("1000x700")
        self.minsize(900, 600)

        self.aktif_frame = None
        
        # Yapay Zeka motorunu program açıldığında 1 kere belleğe yüklüyoruz
        self.yz_motoru = YapayZekaMotoru()

        self.baslangic_yonlendirmesi()

    def frame_degistir(self, yeni_frame_sinifi):
        if self.aktif_frame is not None:
            self.aktif_frame.destroy()
        self.aktif_frame = yeni_frame_sinifi(self)
        self.aktif_frame.pack(fill="both", expand=True)

    def baslangic_yonlendirmesi(self):
        kullanici = kullanici_profilini_getir()
        if kullanici is None:
            self.frame_degistir(ProfilOlusturmaEkrani)
        else:
            self.frame_degistir(AnaMenuEkrani)

# --- AĞACIN KÖKÜ: PROFİL EKRANI ---
class ProfilOlusturmaEkrani(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.merkez_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.merkez_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.merkez_frame, text="Profilini Oluştur", font=("Helvetica", 24, "bold")).pack(pady=20)
        self.isim_entry = ctk.CTkEntry(self.merkez_frame, placeholder_text="Adınız ve Soyadınız", width=250, height=40)
        self.isim_entry.pack(pady=10)
        
        self.cinsiyet_combo = ctk.CTkComboBox(self.merkez_frame, values=["Erkek", "Kadın"], width=250, height=40, state="readonly")
        self.cinsiyet_combo.set("Cinsiyet Seçiniz")
        self.cinsiyet_combo.pack(pady=10)

        ctk.CTkButton(self.merkez_frame, text="Kaydet ve Başla", height=40, width=250, command=self.kaydet).pack(pady=20)
        self.uyari_label = ctk.CTkLabel(self.merkez_frame, text="", text_color="red")
        self.uyari_label.pack()

    def kaydet(self):
        ad_soyad = self.isim_entry.get().strip()
        cinsiyet = self.cinsiyet_combo.get()
        if not ad_soyad or cinsiyet == "Cinsiyet Seçiniz":
            self.uyari_label.configure(text="Lütfen tüm alanları doldurun!")
            return
        kullanici_profili_kaydet_veya_guncelle(ad_soyad, cinsiyet)
        self.master.frame_degistir(AnaMenuEkrani)

# --- WHATSAPP WEB TASARIMI: ANA MENÜ ---
class AnaMenuEkrani(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.secili_karakter_id = None
        self.kullanici = kullanici_profilini_getir()
        self.karakter_durumlari = {}  # {karakter_id: (taban_isim, durum_metni)} -> her sohbetin kendi durumu

        # Ekranı ikiye bölüyoruz (Grid sistemi)
        self.grid_columnconfigure(0, weight=1) # Sol menü (%25)
        self.grid_columnconfigure(1, weight=3) # Sağ sohbet (%75)
        self.grid_rowconfigure(0, weight=1)

        # 1. SOL PANEL (Kişiler Listesi)
        self.sol_panel = ctk.CTkFrame(self, corner_radius=0)
        self.sol_panel.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sol_panel, text="Kişiler", font=("Helvetica", 20, "bold")).pack(pady=15)
        
        # Karakter Ekleme Butonu
        ctk.CTkButton(self.sol_panel, text="+ Yeni Karakter", command=self.yeni_karakter_ekle_popup).pack(pady=10, padx=20, fill="x")

        self.kisiler_listesi = ctk.CTkScrollableFrame(self.sol_panel, fg_color="transparent")
        self.kisiler_listesi.pack(fill="both", expand=True, padx=10, pady=10)
        self.karakterleri_listele()

        # 2. SAĞ PANEL (Sohbet Ekranı)
        self.sag_panel = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray85", "gray17"))
        self.sag_panel.grid(row=0, column=1, sticky="nsew")
        
        self.sag_panel.grid_rowconfigure(1, weight=1)
        self.sag_panel.grid_columnconfigure(0, weight=1)

        # Sağ Üst: Karakter İsmi Başlığı
        self.sohbet_baslik = ctk.CTkLabel(self.sag_panel, text="Sohbet etmek için soldan bir kişi seçin", font=("Helvetica", 18, "bold"), anchor="w")
        self.sohbet_baslik.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Orta: Mesajların Aktığı Yer
        self.mesaj_alani = ctk.CTkScrollableFrame(self.sag_panel, fg_color="transparent")
        self.mesaj_alani.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # Alt: Mesaj Yazma Yeri (Entry + Buton)
        self.girdi_alani = ctk.CTkFrame(self.sag_panel, fg_color="transparent")
        self.girdi_alani.grid(row=2, column=0, sticky="ew", padx=20, pady=15)
        self.girdi_alani.grid_columnconfigure(0, weight=1)

        self.mesaj_kutusu = ctk.CTkEntry(self.girdi_alani, placeholder_text="Bir mesaj yazın...", height=40)
        self.mesaj_kutusu.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.mesaj_kutusu.bind("<Return>", lambda event: self.mesaj_gonder()) # Enter tuşu ile gönder

        self.gonder_buton = ctk.CTkButton(self.girdi_alani, text="Gönder", width=80, height=40, command=self.mesaj_gonder)
        self.gonder_buton.grid(row=0, column=1)
        

    def karakterleri_listele(self):
        """Veritabanındaki karakterleri sol menüye buton olarak dizer"""
        karakterler = tum_karakterleri_getir() # Veriyi temiz bir şekilde köprüden aldık

        for k in karakterler:
            btn = ctk.CTkButton(self.kisiler_listesi, text=k.isim, fg_color=("gray75", "gray25"), 
                                text_color=("black", "white"), anchor="w",
                                command=lambda id=k.id, ad=k.isim: self.sohbeti_yukle(id, ad))
            btn.pack(fill="x", pady=2)

    def sohbeti_yukle(self, karakter_id, karakter_adi):
        # Kilidi tamamen kaldırdık, kullanıcı istediği an istediği yere tıklayabilir!
        self.secili_karakter_id = karakter_id

        # Bu karakterin arka planda devam eden bir isteği varsa (Sırada/Yazıyor),
        # başlığı plain isimle değil, doğru durumla göster.
        if karakter_id in self.karakter_durumlari:
            _, durum = self.karakter_durumlari[karakter_id]
            self.sohbet_baslik.configure(text=f"{karakter_adi}{durum}")
        else:
            self.sohbet_baslik.configure(text=karakter_adi)

        for widget in self.mesaj_alani.winfo_children():
            widget.destroy()

        gecmis_mesajlar = mesaj_gecmisini_getir(karakter_id)
        for msg in gecmis_mesajlar:
            self.mesaj_balonu_ciz(msg.mesaj_metni, msg.gonderen)
            
    def mesaj_balonu_ciz(self, metin, gonderen):
        """WhatsApp tarzı sağa/sola yaslı mesaj balonları oluşturur"""
        kutu = ctk.CTkFrame(self.mesaj_alani, fg_color="transparent")
        kutu.pack(fill="x", pady=5)
        
        if gonderen == "Kullanici":
            # Kullanıcı mesajı yeşil ve sağda
            renk = "#005C4B" # WhatsApp koyu yeşili
            hizalama = "e"
        else:
            # Bot mesajı gri ve solda
            renk = ("gray75", "gray20")
            hizalama = "w"

        balon = ctk.CTkLabel(kutu, text=metin, fg_color=renk, text_color="white", 
                             corner_radius=10, padx=15, pady=10, wraplength=400, justify="left")
        balon.pack(side="right" if hizalama == "e" else "left")

    def _durum_guncelle(self, karakter_id, taban_isim, durum_metni):
        """Bir karakterin (Sırada/Yazıyor) durumunu kaydeder ve, kullanıcı
        şu an o sohbeti görüntülüyorsa, başlığı ana thread'de günceller."""
        if durum_metni:
            self.karakter_durumlari[karakter_id] = (taban_isim, durum_metni)
        else:
            self.karakter_durumlari.pop(karakter_id, None)

        if karakter_id == self.secili_karakter_id:
            metin = f"{taban_isim}{durum_metni}"
            self.sohbet_baslik.after(0, lambda: self.sohbet_baslik.configure(text=metin))

    def mesaj_gonder(self):
        metin = self.mesaj_kutusu.get().strip()
        if not metin or not self.secili_karakter_id:
            return

        # 1. Kilit noktası: O anki sohbetin ID'sini ve düz ismini kopyalıyoruz (Snapshot)
        hedef_karakter_id = self.secili_karakter_id
        taban_isim = self.sohbet_baslik.cget("text")

        self.mesaj_kutusu.delete(0, "end") 
        self.mesaj_balonu_ciz(metin, "Kullanici")
        mesaj_ekle_ve_buda(hedef_karakter_id, "Kullanici", metin)

        # Anında geri bildirim: istek daha kuyruğa girmeden "Bekliyor..." göster
        self._durum_guncelle(hedef_karakter_id, taban_isim, " (Bekliyor...)")

        # 2. İşçiye hedef ID'yi ve taban ismi de gönderiyoruz!
        threading.Thread(target=self.bot_yaniti_bekle, args=(metin, hedef_karakter_id, taban_isim), daemon=True).start()

    def bot_yaniti_bekle(self, kullanici_mesaji, hedef_karakter_id, taban_isim):
        """Kullanıcı başka sohbete geçse bile, bu işçi doğru kişiye odaklanmaya devam eder"""

        karakter = karakter_bilgisi_getir(hedef_karakter_id)

        try:
            rol_aciklamasi = ROL_ACIKLAMALARI.get(
                karakter.rol_tipi,
                f"Kullanıcının {karakter.rol_tipi.lower()}isin."
            )

            dinamik_prompt = (
                f"Sen bir yapay zeka değil, gerçek, yaşayan bir karaktersin. "
                f"Adın: {karakter.isim}. Cinsiyetin: {karakter.cinsiyet}.\n\n"
                f"Kullanıcıyla ilişkin: {karakter.rol_tipi}. {rol_aciklamasi}\n\n"
                f"Kişiliğin ve davranış talimatların:\n{karakter.sistem_istemi}\n\n"
                f"Konuştuğun kişi: {self.kullanici.ad_soyad}, cinsiyeti: {self.kullanici.cinsiyet}.\n\n"
                f"KURALLAR (asla ihlal etme):\n"
                f"- Cinsiyetinin {karakter.cinsiyet} olduğunu asla unutma, buna uygun konuş.\n"
                f"- Karşındakinin cinsiyetinin {self.kullanici.cinsiyet} olduğunu bil ve ona göre hitap et.\n"
                f'- İlişki rolün olan "{karakter.rol_tipi}" kimliğinden asla çıkma.\n'
                f"- Kısa, doğal, gerçek bir WhatsApp mesajı gibi cevap ver; uzun paragraflar yazma.\n"
                f"- Sadece Türkçe cevap ver, başka dil kullanma."
            )

            gecmis_mesajlar = mesaj_gecmisini_getir(hedef_karakter_id)[-10:]

            # KİMLİK HATIRLATMASI: Konuşma uzadıkça modelin başta verilen sistem
            # promptunu "unutması" (recency bias) yaygın bir sorundur. Bu yüzden
            # en son mesajın hemen öncesine kısa bir hatırlatma ekliyoruz.
            hatirlatma = (
                f"[Hatırlatma: Sen {karakter.isim} adında bir {karakter.cinsiyet}sin ve "
                f"kullanıcının {karakter.rol_tipi.lower()}isin. Kullanıcı bir {self.kullanici.cinsiyet}. "
                f"Bu kimlikten çıkma.]"
            )
            takviyeli_mesaj = f"{hatirlatma}\n{kullanici_mesaji}"

            # Bu iki callback, motor.py'deki kuyruk/kilit durumunu arayüze
            # gerçek zamanlı yansıtır: önce "Sırada: N. sırada", sonra "Yazıyor..."
            def sira_bildir(sira_no):
                if sira_no > 1:
                    self._durum_guncelle(hedef_karakter_id, taban_isim, f" (Sırada: {sira_no}. sırada)")
                else:
                    self._durum_guncelle(hedef_karakter_id, taban_isim, " (Yazıyor...)")

            def uretim_basladi():
                self._durum_guncelle(hedef_karakter_id, taban_isim, " (Yazıyor...)")

            bot_cevabi = self.master.yz_motoru.yanit_uret_blok(
                dinamik_prompt, gecmis_mesajlar, takviyeli_mesaj,
                siraya_girdi_callback=sira_bildir,
                uretim_basladi_callback=uretim_basladi
            )

            mesaj_ekle_ve_buda(hedef_karakter_id, "Bot", bot_cevabi)

        except Exception as hata:
            print(f"[HATA] '{karakter.isim}' için cevap üretilirken sorun oluştu: {hata}")
            bot_cevabi = "⚠️ Cevap üretilemedi, lütfen tekrar deneyin."

        finally:
            # Durum artık ne olursa olsun temizlenir (başlık plain isme döner)
            self._durum_guncelle(hedef_karakter_id, taban_isim, "")

        # Görsel Güncelleme Kontrolü:
        # Kullanıcı HALA bu sohbette mi? Yoksa başka sohbete mi geçmiş?
        if getattr(self, "secili_karakter_id", None) == hedef_karakter_id:
            # Eğer hala aynı sohbetteyse ekrana çiz
            self.mesaj_alani.after(0, self.mesaj_balonu_ciz, bot_cevabi, "Bot")

    def yeni_karakter_ekle_popup(self):
        """Karakter ekleme butonuna basıldığında açılan küçük pencere (Toplevel)"""
        if hasattr(self, "popup") and self.popup is not None and self.popup.winfo_exists():
            self.popup.focus()
            return
            
        self.popup = ctk.CTkToplevel(self)
        self.popup.title("Yeni Karakter Yarat")
        self.popup.geometry("420x760")  # WhatsApp içe aktarma bölümü için boyutu büyüttük
        self.popup.attributes("-topmost", True) 
        
        # İçerikler
        ctk.CTkLabel(self.popup, text="Karakter Adı:", font=("Helvetica", 14, "bold")).pack(pady=(20, 5))
        isim_entry = ctk.CTkEntry(self.popup, width=300, placeholder_text="Örn: Ayşe, Kanka, Yoda")
        isim_entry.pack(pady=5)

        # YENİ EKLENEN KISIM: Karakter Cinsiyeti
        ctk.CTkLabel(self.popup, text="Karakterin Cinsiyeti:", font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        karakter_cinsiyet_combo = ctk.CTkComboBox(self.popup, values=["Kadın", "Erkek", "Robot/Tarafsız"], width=300, state="readonly")
        karakter_cinsiyet_combo.set("Kadın") # Varsayılan
        karakter_cinsiyet_combo.pack(pady=5)
        
        ctk.CTkLabel(self.popup, text="Rolü:", font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        rol_combo = ctk.CTkComboBox(self.popup, values=["Arkadaş", "Sevgili", "Mentor", "Asistan"], width=300, state="readonly")
        rol_combo.set("Arkadaş")
        rol_combo.pack(pady=5)
        
        ctk.CTkLabel(self.popup, text="Sistem İstemi (Kişilik Özellikleri):", font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        prompt_textbox = ctk.CTkTextbox(self.popup, width=300, height=100)
        prompt_textbox.pack(pady=5)
        prompt_textbox.insert("1.0", "Sen kullanıcının yakın bir arkadaşısın. Eğlenceli ve kısa cevaplar ver...")

        # --- GERÇEK BİR KİŞİYİ WHATSAPP SOHBETİNDEN KLONLAMA (opsiyonel) ---
        ctk.CTkLabel(self.popup, text="— veya gerçek birini klonla —", font=("Helvetica", 12, "italic")).pack(pady=(15, 2))
        whatsapp_kisi_entry = ctk.CTkEntry(
            self.popup, width=300,
            placeholder_text="Bu kişinin WhatsApp'taki adı (birebir aynı olmalı)"
        )
        whatsapp_kisi_entry.pack(pady=3)

        whatsapp_durum_label = ctk.CTkLabel(self.popup, text="", text_color="gray", wraplength=320)
        whatsapp_durum_label.pack(pady=2)

        def whatsapp_yukle():
            kisi_adi = whatsapp_kisi_entry.get().strip()
            if not kisi_adi:
                whatsapp_durum_label.configure(
                    text="Önce bu kişinin WhatsApp'ta görünen adını yaz.", text_color="red"
                )
                return

            dosya_yolu = filedialog.askopenfilename(
                title="WhatsApp Sohbet Dışa Aktarımını Seç (.txt)",
                filetypes=[("WhatsApp metin dosyası", "*.txt")]
            )
            if not dosya_yolu:
                return

            whatsapp_durum_label.configure(text="Analiz ediliyor, lütfen bekle...", text_color="gray")
            self.popup.update_idletasks()

            try:
                mesajlar = whatsapp_disa_aktarimini_oku(dosya_yolu, kisi_adi)
                if not mesajlar:
                    whatsapp_durum_label.configure(
                        text=f"'{kisi_adi}' adında kimseden mesaj bulunamadı. "
                             f"İsmin WhatsApp'taki gösterim adıyla BİREBİR aynı olduğundan emin ol.",
                        text_color="red"
                    )
                    return

                profil_metni = uslup_profili_olustur(mesajlar)
                mevcut_prompt = prompt_textbox.get("1.0", "end").strip()
                prompt_textbox.delete("1.0", "end")
                prompt_textbox.insert("1.0", f"{profil_metni}\n\n{mevcut_prompt}")

                whatsapp_durum_label.configure(
                    text=f"✅ {len(mesajlar)} mesaj analiz edildi, üslup sistem istemine eklendi. "
                         f"İstersen aşağıdan düzenleyebilirsin.",
                    text_color="green"
                )
            except Exception as hata:
                whatsapp_durum_label.configure(text=f"Dosya okunamadı: {hata}", text_color="red")

        ctk.CTkButton(
            self.popup, text="📄 .txt Dosyasını Seç ve Analiz Et", command=whatsapp_yukle
        ).pack(pady=5)
        
        uyari_label = ctk.CTkLabel(self.popup, text="", text_color="red")
        uyari_label.pack(pady=5)
        
        def kaydet_ve_kapat():
            isim = isim_entry.get().strip()
            rol = rol_combo.get()
            k_cinsiyet = karakter_cinsiyet_combo.get() # Cinsiyeti aldık
            prompt = prompt_textbox.get("1.0", "end").strip()
            
            if not isim or not prompt:
                uyari_label.configure(text="İsim ve İstek alanları boş kalamaz!")
                return
                
            # Veritabanına kaydederken cinsiyeti de gönderiyoruz!
            basarili, mesaj = karakter_ekle(isim, rol, k_cinsiyet, prompt)
            
            if basarili:
                self.popup.destroy() 
                for widget in self.kisiler_listesi.winfo_children():
                    widget.destroy()
                self.karakterleri_listele()
            else:
                uyari_label.configure(text=mesaj) 
                
        ctk.CTkButton(self.popup, text="Karakteri Kaydet", command=kaydet_ve_kapat).pack(pady=15)    

if __name__ == "__main__":
    uygulama = YapayZekaUygulamasi()
    uygulama.mainloop()