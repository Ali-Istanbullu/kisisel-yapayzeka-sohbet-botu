import customtkinter as ctk
import threading
from tkinter import filedialog
import os

from database.veritabani_islemleri import (
    kullanici_profilini_getir, kullanici_profili_kaydet_veya_guncelle,
    mesaj_ekle, mesaj_gecmisini_getir, tum_karakterleri_getir,
    karakter_bilgisi_getir, karakter_ekle, tum_rol_tiplerini_getir,
    tum_cinsiyet_tiplerini_getir, whatsapp_profili_kaydet,
    mesajlari_sil, hafiza_guncelle, karakter_sil # <-- karakter_sil EKLENDİ
)
from backend.whatsapp_analiz import whatsapp_disa_aktarimini_oku, uslup_profili_olustur
from backend.prompt_olusturucu import karakter_sistem_prompti_olustur, hatirlatma_ekli_mesaj_olustur
from backend.motor import YapayZekaMotoru
from loglama import hata_logla

# WhatsApp Renk Paleti (Aydınlık Mod, Karanlık Mod)
WA_ARKAPLAN = ("#efeae2", "#111b21")      
WA_PANEL = ("#f0f2f5", "#202c33")         
WA_MESAJ_GIDEN = ("#d9fdd3", "#005c4b")   
WA_MESAJ_GELEN = ("#ffffff", "#202c33")   
WA_METIN = ("#111b21", "#e9edef")         
WA_GIRDI_ALANI = ("#ffffff", "#2a3942")   
WA_YESIL_BUTON = ("#00a884", "#00a884")   
WA_AVATAR_RENK = ("#6b7c85", "#6b7c85")   

ctk.set_appearance_mode("dark")  

class YapayZekaUygulamasi(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI WhatsApp Klonu")
        self.geometry("800x530") 
        self.minsize(700, 480)
        self.configure(fg_color=WA_ARKAPLAN)
        
        try:
            self.iconbitmap("ikon.ico")
        except:
            # BİLİNÇLİ OLARAK sessiz: ikon dosyası .exe paketlenmeden önce
            # her geliştirme ortamında olmayabilir, bu gerçek bir hata değil,
            # sadece kozmetik bir eksiklik. Loglamaya değmez.
            pass

        self.aktif_frame = None
        self.baslangic_yonlendirmesi()

    def frame_degistir(self, yeni_frame_sinifi):
        if self.aktif_frame is not None: self.aktif_frame.destroy()
        self.aktif_frame = yeni_frame_sinifi(self)
        self.aktif_frame.pack(fill="both", expand=True)

    def baslangic_yonlendirmesi(self):
        # Eğer profil yoksa önce profil ekranına at, motoru yükleme
        if kullanici_profilini_getir() is None: 
            self.frame_degistir(ProfilOlusturmaEkrani)
            return

        # Profil varsa yükleme ekranı göster ve motoru arka planda başlat
        if not hasattr(self, 'yz_motoru'):
            self.yukleme_ekrani_goster()
            threading.Thread(target=self.motoru_arkaplanda_baslat, daemon=True).start()
        else:
            self.frame_degistir(AnaMenuEkrani)

    def yukleme_ekrani_goster(self):
        if self.aktif_frame is not None: self.aktif_frame.destroy()
        self.aktif_frame = ctk.CTkFrame(self, fg_color=WA_ARKAPLAN)
        self.aktif_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(self.aktif_frame, text="Yapay Zeka Motoru Isınıyor...\nLütfen Bekleyin (Bu işlem donanıma göre 10-20 sn sürebilir).", font=("Helvetica", 16, "bold"), text_color=WA_METIN).place(relx=0.5, rely=0.5, anchor="center")

    def motoru_arkaplanda_baslat(self):
        try:
            self.yz_motoru = YapayZekaMotoru()
            # Motor yüklenince ana menüye geç
            self.after(0, lambda: self.frame_degistir(AnaMenuEkrani))
        except Exception as hata:
            self.after(0, lambda: ctk.CTkLabel(self.aktif_frame, text=f"Motor yüklenemedi!\nDetaylar hatalar.log dosyasında.", text_color="#ef697a").place(relx=0.5, rely=0.6, anchor="center"))

class ProfilOlusturmaEkrani(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=WA_ARKAPLAN)
        self.master = master
        self.merkez_frame = ctk.CTkFrame(self, fg_color=WA_PANEL, corner_radius=15)
        self.merkez_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(self.merkez_frame, text="Profilini Oluştur", font=("Helvetica", 22, "bold"), text_color=WA_METIN).pack(pady=(20, 15), padx=40)
        
        self.isim_entry = ctk.CTkEntry(self.merkez_frame, placeholder_text="Adınız ve Soyadınız", width=250, height=35, fg_color=WA_GIRDI_ALANI, border_width=0, text_color=WA_METIN)
        self.isim_entry.pack(pady=10)

        self.cinsiyetler = tum_cinsiyet_tiplerini_getir()
        self._cinsiyet_isim_to_id = {c.isim: c.id for c in self.cinsiyetler}
        self.cinsiyet_combo = ctk.CTkComboBox(self.merkez_frame, values=[c.isim for c in self.cinsiyetler], width=250, height=35, state="readonly", fg_color=WA_GIRDI_ALANI, border_width=0, text_color=WA_METIN, dropdown_fg_color=WA_PANEL)
        self.cinsiyet_combo.set("Cinsiyet Seçiniz")
        self.cinsiyet_combo.pack(pady=10)

        ctk.CTkButton(self.merkez_frame, text="Kaydet ve Başla", height=35, width=250, fg_color=WA_YESIL_BUTON, text_color="white", font=("Helvetica", 14, "bold"), hover_color="#017a5f", command=self.kaydet).pack(pady=(15, 20))
        self.uyari_label = ctk.CTkLabel(self.merkez_frame, text="", text_color="#ef697a")
        self.uyari_label.pack(pady=(0,5))

    def kaydet(self):
        ad_soyad = self.isim_entry.get().strip()
        cinsiyet_isim = self.cinsiyet_combo.get()
        if not ad_soyad or cinsiyet_isim not in self._cinsiyet_isim_to_id:
            self.uyari_label.configure(text="Lütfen tüm alanları doldurun!")
            return
        kullanici_profili_kaydet_veya_guncelle(ad_soyad, self._cinsiyet_isim_to_id[cinsiyet_isim])
        self.master.baslangic_yonlendirmesi()

class AnaMenuEkrani(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=WA_ARKAPLAN)
        self.master = master
        self.secili_karakter_id = None
        self.kullanici = kullanici_profilini_getir()
        self.karakter_durumlari = {} 

        self.grid_columnconfigure(0, weight=1, minsize=230) 
        self.grid_columnconfigure(1, weight=4) 
        self.grid_rowconfigure(0, weight=1)

        # --- SOL PANEL ---
        self.sol_panel = ctk.CTkFrame(self, fg_color=WA_PANEL, corner_radius=0)
        self.sol_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 1))

        self.sol_ust_bar = ctk.CTkFrame(self.sol_panel, fg_color=WA_PANEL, corner_radius=0, height=55)
        self.sol_ust_bar.pack(fill="x")
        self.sol_ust_bar.pack_propagate(False)
        ctk.CTkLabel(self.sol_ust_bar, text="Sohbetler", font=("Helvetica", 18, "bold"), text_color=WA_METIN).pack(side="left", padx=15, pady=12)
        
        self.tema_buton = ctk.CTkButton(self.sol_ust_bar, text="☀️", width=30, height=30, fg_color="transparent", text_color=WA_METIN, hover_color=WA_GIRDI_ALANI, font=("Helvetica", 16), command=self.tema_degistir)
        self.tema_buton.pack(side="right", padx=(2, 10), pady=10)

        ctk.CTkButton(self.sol_ust_bar, text="+ Yeni", width=50, height=30, fg_color=WA_GIRDI_ALANI, text_color=WA_METIN, hover_color=WA_ARKAPLAN, command=self.yeni_karakter_ekle_popup).pack(side="right", padx=2)
        
        self.arama_kutu = ctk.CTkEntry(self.sol_panel, placeholder_text="Arama yapın", fg_color=WA_GIRDI_ALANI, border_width=0, height=30, corner_radius=8, text_color=WA_METIN)
        self.arama_kutu.pack(fill="x", padx=12, pady=(5, 8))
        self.arama_kutu.bind("<KeyRelease>", self.arama_yap)

        self.kisiler_listesi = ctk.CTkScrollableFrame(self.sol_panel, fg_color="transparent")
        self.kisiler_listesi.pack(fill="both", expand=True)
        self.karakterleri_listele()

        # --- SAĞ PANEL ---
        self.sag_panel = ctk.CTkFrame(self, fg_color=WA_ARKAPLAN, corner_radius=0)
        self.sag_panel.grid(row=0, column=1, sticky="nsew")
        self.sag_panel.grid_rowconfigure(1, weight=1)
        self.sag_panel.grid_columnconfigure(0, weight=1)

        self.sag_ust_bar = ctk.CTkFrame(self.sag_panel, fg_color=WA_PANEL, corner_radius=0, height=55)
        self.sag_ust_bar.grid(row=0, column=0, sticky="ew")
        self.sag_ust_bar.pack_propagate(False)

        self.ust_avatar = ctk.CTkFrame(self.sag_ust_bar, width=36, height=36, corner_radius=18, fg_color=WA_PANEL)
        self.ust_avatar.pack(side="left", padx=(15, 10), pady=8)
        self.ust_avatar.pack_propagate(False)
        self.ust_avatar_harf = ctk.CTkLabel(self.ust_avatar, text="", font=("Helvetica", 16, "bold"), text_color="white")
        self.ust_avatar_harf.place(relx=0.5, rely=0.5, anchor="center")

        self.sohbet_baslik = ctk.CTkLabel(self.sag_ust_bar, text="Kişi seçin", font=("Helvetica", 15, "bold"), text_color=WA_METIN)
        self.sohbet_baslik.pack(side="left", pady=15)
        
        # --- YENİ EKLENEN SİLME BUTONU ---
        self.sil_buton = ctk.CTkButton(self.sag_ust_bar, text="🗑️ Sil", width=60, height=30, fg_color="#ef697a", text_color="white", hover_color="#c85261", font=("Helvetica", 12, "bold"), command=self.sohbeti_sil)

        self.mesaj_alani = ctk.CTkScrollableFrame(self.sag_panel, fg_color="transparent")
        self.mesaj_alani.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)

        self.girdi_alani = ctk.CTkFrame(self.sag_panel, fg_color=WA_PANEL, corner_radius=0)
        self.girdi_alani.grid(row=2, column=0, sticky="ew")
        self.girdi_alani.grid_columnconfigure(0, weight=1)
        
        self.mesaj_kutusu = ctk.CTkEntry(self.girdi_alani, placeholder_text="Bir mesaj yazın", height=40, fg_color=WA_GIRDI_ALANI, border_width=0, text_color=WA_METIN, font=("Helvetica", 14), corner_radius=10)
        self.mesaj_kutusu.grid(row=0, column=0, sticky="ew", padx=(15, 10), pady=10)
        self.mesaj_kutusu.bind("<Return>", lambda event: self.mesaj_gonder())
        
        self.gonder_buton = ctk.CTkButton(self.girdi_alani, text="Gönder", width=75, height=40, fg_color=WA_YESIL_BUTON, text_color="white", font=("Helvetica", 14, "bold"), hover_color="#017a5f", command=self.mesaj_gonder)
        self.gonder_buton.grid(row=0, column=1, padx=(0, 15), pady=10)

    def tema_degistir(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
            self.tema_buton.configure(text="🌙")
        else:
            ctk.set_appearance_mode("Dark")
            self.tema_buton.configure(text="☀️")

    def arama_yap(self, event):
        arama_metni = self.arama_kutu.get().lower().strip()
        self.karakterleri_listele(arama_metni)

    def karakterleri_listele(self, filtre_metni=""):
        for widget in self.kisiler_listesi.winfo_children(): widget.destroy()
        
        for k in tum_karakterleri_getir():
            if filtre_metni and filtre_metni not in k.isim.lower():
                continue

            satir = ctk.CTkFrame(self.kisiler_listesi, fg_color="transparent", corner_radius=0)
            satir.pack(fill="x")
            
            avatar_kutu = ctk.CTkFrame(satir, width=36, height=36, corner_radius=18, fg_color=WA_AVATAR_RENK)
            avatar_kutu.pack(side="left", padx=(10, 8), pady=6)
            avatar_kutu.pack_propagate(False)
            harf = k.isim[0].upper() if k.isim else "?"
            ctk.CTkLabel(avatar_kutu, text=harf, font=("Helvetica", 16, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")
            
            btn = ctk.CTkButton(satir, text=k.isim, font=("Helvetica", 14), fg_color="transparent", text_color=WA_METIN, anchor="w", height=48, hover_color=WA_GIRDI_ALANI, corner_radius=0, command=lambda id=k.id, ad=k.isim: self.sohbeti_yukle(id, ad))
            btn.pack(side="left", fill="both", expand=True)
            
            ctk.CTkFrame(self.kisiler_listesi, height=1, fg_color=WA_GIRDI_ALANI).pack(fill="x", padx=(54, 0))

    def sohbeti_yukle(self, karakter_id, karakter_adi):
        self.secili_karakter_id = karakter_id
        _, durum = self.karakter_durumlari.get(karakter_id, (None, ""))
        self.sohbet_baslik.configure(text=f"{karakter_adi}{durum}")
        
        self.ust_avatar.configure(fg_color=WA_AVATAR_RENK)
        self.ust_avatar_harf.configure(text=karakter_adi[0].upper() if karakter_adi else "?")
        self.sil_buton.pack(side="right", padx=15) # Kişi seçildiğinde Sil butonunu göster
            
        for widget in self.mesaj_alani.winfo_children(): widget.destroy()
        for msg in mesaj_gecmisini_getir(karakter_id): self.mesaj_balonu_ciz(msg.mesaj_metni, msg.gonderen)

    def sohbeti_sil(self):
        """Kişiyi ve geçmişini tamamen veritabanından siler"""
        if self.secili_karakter_id:
            karakter_sil(self.secili_karakter_id)
            self.secili_karakter_id = None
            self.sohbet_baslik.configure(text="Kişi seçin")
            self.ust_avatar.configure(fg_color=WA_PANEL)
            self.ust_avatar_harf.configure(text="")
            self.sil_buton.pack_forget() # Butonu sakla
            for widget in self.mesaj_alani.winfo_children():
                widget.destroy()
            self.karakterleri_listele() # Sol listeyi güncelle

    def mesaj_balonu_ciz(self, metin, gonderen):
        kutu = ctk.CTkFrame(self.mesaj_alani, fg_color="transparent")
        kutu.pack(fill="x", pady=2)
        
        if gonderen == "Kullanici":
            renk = WA_MESAJ_GIDEN
            hizalama = "e"
        else:
            renk = WA_MESAJ_GELEN
            hizalama = "w"
            
        balon = ctk.CTkLabel(kutu, text=metin, font=("Helvetica", 13), fg_color=renk, text_color=WA_METIN, corner_radius=8, padx=12, pady=8, wraplength=400, justify="left")
        balon.pack(side="right" if hizalama == "e" else "left", padx=5, pady=2)

    def _durum_guncelle(self, karakter_id, taban_isim, durum_metni):
        if durum_metni: self.karakter_durumlari[karakter_id] = (taban_isim, durum_metni)
        else: self.karakter_durumlari.pop(karakter_id, None)

        if karakter_id == self.secili_karakter_id:
            self.sohbet_baslik.after(0, lambda: self.sohbet_baslik.configure(text=f"{taban_isim}{durum_metni}"))

    def mesaj_gonder(self):
        metin = self.mesaj_kutusu.get().strip()
        if not metin or not self.secili_karakter_id: return

        hedef_karakter_id = self.secili_karakter_id
        taban_isim = self.sohbet_baslik.cget("text").split(" (")[0]

        self.mesaj_kutusu.delete(0, "end")
        self.mesaj_balonu_ciz(metin, "Kullanici")
        mesaj_ekle(hedef_karakter_id, "Kullanici", metin)
        
        self._durum_guncelle(hedef_karakter_id, taban_isim, " (Yazıyor...)")
        threading.Thread(target=self.bot_yaniti_bekle, args=(metin, hedef_karakter_id, taban_isim), daemon=True).start()

    

    def bot_yaniti_bekle(self, kullanici_mesaji, hedef_karakter_id, taban_isim):
        try:
            karakter = karakter_bilgisi_getir(hedef_karakter_id)

            dinamik_prompt = karakter_sistem_prompti_olustur(karakter, self.kullanici)
            takviyeli_mesaj = hatirlatma_ekli_mesaj_olustur(karakter, self.kullanici, kullanici_mesaji)
            gecmis_mesajlar = mesaj_gecmisini_getir(hedef_karakter_id)[-10:]

            def sira_bildir(sira_no):
                if sira_no > 1: self._durum_guncelle(hedef_karakter_id, taban_isim, f" (Sırada: {sira_no}. sırada)")
                else: self._durum_guncelle(hedef_karakter_id, taban_isim, " (Yazıyor...)")

            def uretim_basladi():
                self._durum_guncelle(hedef_karakter_id, taban_isim, " (Yazıyor...)")

            bot_cevabi = self.master.yz_motoru.yanit_uret_blok(
                dinamik_prompt, gecmis_mesajlar, takviyeli_mesaj,
                siraya_girdi_callback=sira_bildir, uretim_basladi_callback=uretim_basladi
            )
            # DİKKAT: Eski kodda mesaj_ekle ve dinamik_hafiza_kontrolu buradaydı. 
            # Buradan sildik, çünkü adam sohbeti silmiş olabilir!

        except Exception:
            from loglama import hata_logla
            hata_logla(f"bot_yaniti_bekle (karakter_id={hedef_karakter_id})")
            bot_cevabi = "⚠️ Cevap üretilemedi, lütfen tekrar deneyin."
        finally:
            self._durum_guncelle(hedef_karakter_id, taban_isim, "")

        # --- İŞTE SİHİRLİ KONTROL BURASI ---
        # Sadece adam hala aynı sohbetin içindeyse veya sohbet silinmediyse çalışır:
        if getattr(self, "secili_karakter_id", None) == hedef_karakter_id:
            # Önce mesajı veritabanına kaydet
            mesaj_ekle(hedef_karakter_id, "Bot", bot_cevabi)
            # Sonra ekrana balonu çizdir
            self.mesaj_alani.after(0, self.mesaj_balonu_ciz, bot_cevabi, "Bot")
            # En son arkada hafıza kontrolünü tetikle
            threading.Thread(target=self.master.yz_motoru.dinamik_hafiza_kontrolu, args=(hedef_karakter_id,), daemon=True).start()

    def yeni_karakter_ekle_popup(self):
        if hasattr(self, "popup") and self.popup is not None and self.popup.winfo_exists():
            self.popup.focus()
            return
        self.popup = ctk.CTkToplevel(self)
        self.popup.title("Yeni Karakter")
        self.popup.geometry("380x520")
        self.popup.configure(fg_color=WA_ARKAPLAN)
        self.popup.attributes("-topmost", True)
        self.popup.resizable(False, False)

        # İKON SORUNU İÇİN GÜNCELLEME (Gecikmeli yükleme pencere açıldıktan sonra garanti eder)
        def ikon_yukle():
            try: self.popup.iconbitmap("ikon.ico")
            except: pass  # BİLİNÇLİ olarak sessiz - bkz. yukarıdaki ana pencere ikon notu
        self.popup.after(200, ikon_yukle)

        ctk.CTkLabel(self.popup, text="Karakter Adı:", font=("Helvetica", 13, "bold"), text_color=WA_METIN).pack(pady=(10, 2))
        isim_entry = ctk.CTkEntry(self.popup, width=320, height=30, fg_color=WA_GIRDI_ALANI, border_width=0, text_color=WA_METIN)
        isim_entry.pack(pady=2)

        cinsiyetler = tum_cinsiyet_tiplerini_getir()
        cinsiyet_isim_to_id = {c.isim: c.id for c in cinsiyetler}
        ctk.CTkLabel(self.popup, text="Cinsiyeti:", font=("Helvetica", 13, "bold"), text_color=WA_METIN).pack(pady=(5, 2))
        karakter_cinsiyet_combo = ctk.CTkComboBox(self.popup, values=[c.isim for c in cinsiyetler], width=320, height=30, state="readonly", fg_color=WA_GIRDI_ALANI, border_width=0, text_color=WA_METIN, dropdown_fg_color=WA_PANEL)
        karakter_cinsiyet_combo.set(cinsiyetler[0].isim if cinsiyetler else "")
        karakter_cinsiyet_combo.pack(pady=2)

        roller = tum_rol_tiplerini_getir()
        rol_isim_to_id = {r.isim: r.id for r in roller}
        ctk.CTkLabel(self.popup, text="Rolü:", font=("Helvetica", 13, "bold"), text_color=WA_METIN).pack(pady=(5, 2))
        rol_combo = ctk.CTkComboBox(self.popup, values=[r.isim for r in roller], width=320, height=30, state="readonly", fg_color=WA_GIRDI_ALANI, border_width=0, text_color=WA_METIN, dropdown_fg_color=WA_PANEL)
        varsayilan_rol = "Diğer / Belirtilmemiş" if "Diğer / Belirtilmemiş" in rol_isim_to_id else (roller[0].isim if roller else "")
        rol_combo.set(varsayilan_rol)
        rol_combo.pack(pady=2)

        ctk.CTkLabel(self.popup, text="Sistem İstemi (Kişilik Özellikleri):", font=("Helvetica", 13, "bold"), text_color=WA_METIN).pack(pady=(5, 2))
        prompt_textbox = ctk.CTkTextbox(self.popup, width=320, height=60, fg_color=WA_GIRDI_ALANI, border_width=0, text_color=WA_METIN)
        prompt_textbox.pack(pady=2)
        prompt_textbox.insert("1.0", "Kısa ve eğlenceli cevaplar ver...")

        ctk.CTkLabel(self.popup, text="— Gerçek Birini Klonla (Opsiyonel) —", font=("Helvetica", 11, "italic"), text_color=WA_YESIL_BUTON).pack(pady=(10, 2))
        whatsapp_kisi_entry = ctk.CTkEntry(self.popup, width=320, height=30, placeholder_text="WhatsApp'taki adı (birebir aynı)", fg_color=WA_GIRDI_ALANI, border_width=0, text_color=WA_METIN)
        whatsapp_kisi_entry.pack(pady=2)
        whatsapp_durum_label = ctk.CTkLabel(self.popup, text="", text_color="gray", wraplength=300)
        whatsapp_durum_label.pack(pady=2)
        bekleyen_whatsapp_verisi = {}

        def whatsapp_yukle():
            kisi_adi = whatsapp_kisi_entry.get().strip()
            if not kisi_adi:
                whatsapp_durum_label.configure(text="Önce WhatsApp'taki adını yaz.", text_color="#ef697a")
                return
                
            dosya_yolu = filedialog.askopenfilename(title="WhatsApp .txt Dosyasını Seç", filetypes=[("Metin dosyası", "*.txt")])
            if not dosya_yolu: return
            
            # Ekrana bekleme mesajını basıyoruz (Garson siparişi aldı)
            whatsapp_durum_label.configure(text="Analiz ediliyor, lütfen bekleyin...", text_color="gray")
            self.popup.update_idletasks()

            # Mutfaktan Başarılı sonuç gelirse arayüzün yapacağı iş:
            def analiz_basarili(kisi, ozet, ornek, mesaj_sayisi):
                bekleyen_whatsapp_verisi.update({"kisi_adi": kisi, "uslup_ozeti": ozet, "ornekler": ornek})
                self.popup.after(0, lambda: whatsapp_durum_label.configure(text=f"✅ {mesaj_sayisi} mesaj analiz edildi.", text_color=WA_YESIL_BUTON))

            # Mutfakta Hata çıkarsa arayüzün yapacağı iş:
            def analiz_hatali(hata_mesaji):
                self.popup.after(0, lambda: whatsapp_durum_label.configure(text=f"Hata: {hata_mesaji}", text_color="#ef697a"))

            # İşlemi mutfağa (backend'e) yolluyoruz
            from backend.whatsapp_analiz import whatsapp_analizini_arkaplanda_baslat
            whatsapp_analizini_arkaplanda_baslat(dosya_yolu, kisi_adi, analiz_basarili, analiz_hatali)

        ctk.CTkButton(self.popup, text="📄 .txt Analiz Et", width=320, height=30, fg_color=WA_PANEL, hover_color=WA_GIRDI_ALANI, text_color=WA_METIN, command=whatsapp_yukle).pack(pady=2)
        uyari_label = ctk.CTkLabel(self.popup, text="", text_color="#ef697a")
        uyari_label.pack(pady=2)

        def kaydet_ve_kapat():
            isim = isim_entry.get().strip()
            rol_isim = rol_combo.get()
            cinsiyet_isim = karakter_cinsiyet_combo.get()
            prompt = prompt_textbox.get("1.0", "end").strip()
            if not isim or not prompt:
                uyari_label.configure(text="İsim ve İstek boş kalamaz!")
                return
            basarili, mesaj, yeni_karakter_id = karakter_ekle(isim, rol_isim_to_id[rol_isim], cinsiyet_isim_to_id[cinsiyet_isim], prompt)
            
            if basarili:
                if bekleyen_whatsapp_verisi:
                    whatsapp_profili_kaydet(yeni_karakter_id, bekleyen_whatsapp_verisi["kisi_adi"], bekleyen_whatsapp_verisi["uslup_ozeti"], bekleyen_whatsapp_verisi["ornekler"])
                self.popup.destroy()
                self.karakterleri_listele()
            else:
                uyari_label.configure(text=mesaj)

        ctk.CTkButton(self.popup, text="Kaydet", width=320, height=35, fg_color=WA_YESIL_BUTON, text_color="white", font=("Helvetica", 14, "bold"), hover_color="#017a5f", command=kaydet_ve_kapat).pack(pady=(5, 10))