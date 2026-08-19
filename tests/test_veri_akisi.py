import unittest
import sys
import os

# Projenin ana dizinini sistem yoluna ekliyoruz ki 'database' klasörünü bulabilsin
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.veritabani_islemleri import (
    karakter_ekle, 
    karakter_bilgisi_getir, 
    whatsapp_profili_kaydet, 
    karakter_sil
)

class TestVeriAkisi(unittest.TestCase):
    def test_veritabanindan_dogru_cekiliyor_mu(self):
        # 1. Sisteme sahte bir karakter kaydet
        basarili, mesaj, char_id = karakter_ekle(
            isim="Test Mankeni", 
            rol_id=1, 
            cinsiyet_id=1, 
            sistem_istemi="Sistem istemi testi."
        )
        self.assertTrue(basarili, "Test karakteri veritabanına eklenemedi!")

        # 2. Bu karaktere sahte bir WhatsApp txt analizi kaydet
        whatsapp_profili_kaydet(
            karakter_id=char_id, 
            kaynak_kisi_adi="Test Mankeni", 
            uslup_ozeti="Çok kısa ve öz mesajlar yazar.", 
            ornek_mesajlar_listesi=["selam", "naber"]
        )

        # 3. VERİYİ GERİ ÇEK (Asıl akış testi)
        cekilen_veri = karakter_bilgisi_getir(char_id)

        # 4. SAĞLAMA YAP 
        self.assertEqual(cekilen_veri.isim, "Test Mankeni", "İsim veritabanından yanlış geldi!")
        self.assertEqual(cekilen_veri.sistem_istemi, "Sistem istemi testi.", "Sistem istemi gelmedi!")
        self.assertIsNotNone(cekilen_veri.rol, "Rol verisi çekilemedi!")
        self.assertIsNotNone(cekilen_veri.whatsapp_profili, "WhatsApp veritabanı bağlantısı koptu!")
        self.assertEqual(cekilen_veri.whatsapp_profili.uslup_ozeti, "Çok kısa ve öz mesajlar yazar.", "WhatsApp özeti yanlış!")

        # 5. Temizlik
        karakter_sil(char_id)

if __name__ == '__main__':
    unittest.main()