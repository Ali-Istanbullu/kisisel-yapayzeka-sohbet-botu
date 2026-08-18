import unittest
import sys
import os

# Proje ana dizinini yola ekliyoruz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.prompt_olusturucu import karakter_sistem_prompti_olustur, hatirlatma_ekli_mesaj_olustur

# Veritabanına bağlanmadan test yapabilmek için "Sahte (Mock)" nesneler üretiyoruz
class SahteCinsiyet:
    def __init__(self, isim):
        self.isim = isim

class SahteRol:
    def __init__(self, isim, aciklama):
        self.isim = isim
        self.davranis_aciklamasi = aciklama

class SahteWhatsappProfili:
    def __init__(self, ozet, ornekler):
        self.uslup_ozeti = ozet
        self.ornek_mesajlar = ornekler

class SahteKarakter:
    def __init__(self, isim, cinsiyet_ismi, rol_ismi, rol_aciklama, prompt, hafiza="", wp_ozet=None):
        self.isim = isim
        self.cinsiyet = SahteCinsiyet(cinsiyet_ismi)
        self.rol = SahteRol(rol_ismi, rol_aciklama)
        self.sistem_istemi = prompt
        self.uzun_donem_hafiza = hafiza
        # Eğer WhatsApp profili varsa onu da sahte olarak ekle
        self.whatsapp_profili = SahteWhatsappProfili(wp_ozet, "Ornek1\nOrnek2") if wp_ozet else None

class SahteKullanici:
    def __init__(self, ad_soyad, cinsiyet_ismi):
        self.ad_soyad = ad_soyad
        self.cinsiyet = SahteCinsiyet(cinsiyet_ismi)

class TestPromptOlusturucu(unittest.TestCase):

    def setUp(self):
        """Testlerden önce sahte bir Kullanıcı ve Karakter yaratıyoruz."""
        self.kullanici = SahteKullanici("Ali İstanbullu", "Erkek")
        self.karakter = SahteKarakter(
            isim="Ayşe",
            cinsiyet_ismi="Kadın",
            rol_ismi="Arkadaş",
            rol_aciklama="Samimi bir arkadaşsın.",
            prompt="Eğlenceli cevaplar ver.",
            hafiza="Önemli Not: Ali dün maça gitti.",
            wp_ozet="Kısa ve emojili yazar."
        )

    def test_karakter_sistem_prompti_olustur(self):
        """1. FONKSİYON TESTİ: Tüm veriler birleşip tek bir devasa kural metni oluyor mu?"""
        prompt = karakter_sistem_prompti_olustur(self.karakter, self.kullanici)
        
        # İçinde olması gereken kilit kelimeleri kontrol et
        self.assertIn("Ayşe", prompt, "Karakter ismi prompta eklenmemiş!")
        self.assertIn("Kadın", prompt, "Cinsiyet prompta eklenmemiş!")
        self.assertIn("Samimi bir arkadaşsın", prompt, "Rol açıklaması eksik!")
        self.assertIn("Ali dün maça gitti", prompt, "Uzun dönem hafıza prompta yansımamış!")
        self.assertIn("Kısa ve emojili yazar", prompt, "WhatsApp üslubu atlanmış!")
        self.assertIn("Ali İstanbullu", prompt, "Kullanıcının adı promptta yok!")
        self.assertIn("MUTLAKA KISA YAZ", prompt, "Sistem güvenlik kuralları silinmiş!")

    def test_hatirlatma_ekli_mesaj_olustur(self):
        """2. FONKSİYON TESTİ: Gelen her mesaja görünmez hatırlatma etiketi basılıyor mu?"""
        mesaj = hatirlatma_ekli_mesaj_olustur(self.karakter, self.kullanici, "Naber, nasılsın?")
        
        self.assertIn("[Hatırlatma:", mesaj, "Hatırlatma etiketi başa eklenmemiş!")
        self.assertIn("Ayşe", mesaj, "Hatırlatmanın içinde karakter adı yok!")
        self.assertIn("Naber, nasılsın?", mesaj, "Kullanıcının asıl mesajı kaybolmuş!")

if __name__ == '__main__':
    unittest.main(verbosity=2)