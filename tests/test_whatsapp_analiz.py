import unittest
import os
import tempfile
import sys

# Proje ana dizinini yola ekliyoruz ki backend klasörünü bulabilsin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.whatsapp_analiz import whatsapp_disa_aktarimini_oku, uslup_profili_olustur

class TestWhatsappAnaliz(unittest.TestCase):
    
    def setUp(self):
        """Her testten önce arka planda sahte bir WhatsApp .txt dosyası oluştururuz."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dosya_yolu = os.path.join(self.test_dir.name, "sahte_sohbet.txt")
        
        # İçinde normal mesaj, çok satırlı mesaj ve 'sistem mesajı' barındıran tuzaklı bir sohbet:
        sahte_icerik = """
[12.04.2023 14:30:00] Ali İstanbullu: Selam, nasılsın?
[12.04.2023 14:31:00] Ayşe: İyiyim sen?
[12.04.2023 14:32:00] Ali İstanbullu: Ben de iyiyim.
Yarınki randevu ne oldu?
[12.04.2023 14:35:00] Ali İstanbullu: bu mesaj silindi
[12.04.2023 14:40:00] Ayşe: <media omitted>
"""
        with open(self.test_dosya_yolu, "w", encoding="utf-8-sig") as f:
            f.write(sahte_icerik.strip())

    def tearDown(self):
        """Test bittikten sonra sahte dosyayı bilgisayardan temizler."""
        self.test_dir.cleanup()

    def test_whatsapp_disa_aktarimini_oku(self):
        """1. FONKSİYON TESTİ: Regex tabanlı metin ayrıştırma doğru çalışıyor mu?"""
        mesajlar = whatsapp_disa_aktarimini_oku(self.test_dosya_yolu, "Ali İstanbullu")
        
        # Sistem mesajı atlanmalı, Ayşe'nin mesajı atlanmalı, sadece Ali'nin 2 mesajı kalmalı:
        self.assertEqual(len(mesajlar), 2, "Yanlış sayıda mesaj okundu! Sistem mesajlarını ayıklamıyor olabilir.")
        
        # Birinci mesaj düz mü?
        self.assertEqual(mesajlar[0], "Selam, nasılsın?")
        
        # İkinci mesaj çok satırlı (Enter'a basılmış), kodumuz bunları doğru birleştiriyor mu?
        self.assertEqual(mesajlar[1], "Ben de iyiyim. Yarınki randevu ne oldu?", "Çok satırlı mesajlar tek parça yapılamadı!")

    def test_uslup_profili_olustur_kisa_ve_emojili(self):
        """2. FONKSİYON TESTİ: Kısa ve emojili mesajlardan doğru üslup tespiti yapılıyor mu?"""
        sahte_mesajlar = ["Evet 👍", "Hayır 👎", "Tamam 😊", "Yok", "Ne"]
        
        uslup_ozeti, ornekler = uslup_profili_olustur(sahte_mesajlar, ornek_sayisi=2)
        
        self.assertIsNotNone(uslup_ozeti)
        self.assertIn("çok kısa ve öz", uslup_ozeti, "Kısa mesaj tespiti çalışmadı!")
        self.assertIn("çoğu zaman tek kelimelik", uslup_ozeti, "Tek kelime tespiti patladı!")
        self.assertIn("sık sık emoji kullanır", uslup_ozeti, "Emoji hesabı yanlış!")
        self.assertTrue(len(ornekler) <= 2, "Örnek sayısı sınırını aşıyor!")

    def test_uslup_profili_olustur_buyuk_harf(self):
        """2. FONKSİYON TESTİ: Agresif/Büyük harfli mesajların tespiti yapılıyor mu?"""
        sahte_mesajlar = [
            "BU PROJE NEDEN HALA BİTMEDİ",
            "Sana defalarca kez bu konunun böyle çözülmeyeceğini söyledim.",
            "YİNE AYNI ŞEY",
            "Gerçekten detaylı ve uzun bir açıklama yapmak gerekirse durum şundan ibaret..."
        ]
        
        uslup_ozeti, ornekler = uslup_profili_olustur(sahte_mesajlar)
        self.assertIn("bazen tamamen büyük harfle vurgu yapar", uslup_ozeti, "Büyük harf tespiti atlandı!")
        self.assertIn("orta uzunlukta", uslup_ozeti, "Ortalama uzunluk hesabı yanlış!")

    def test_uslup_profili_bos_liste(self):
        """GÜVENLİK TESTİ: Programa boş liste atarsak kod çöker mi (ZeroDivisionError)?"""
        uslup_ozeti, ornekler = uslup_profili_olustur([])
        self.assertIsNone(uslup_ozeti, "Boş listede None dönmeliydi!")
        self.assertEqual(ornekler, [], "Boş listede örnek listesi boş olmalıydı!")

if __name__ == '__main__':
    unittest.main(verbosity=2)