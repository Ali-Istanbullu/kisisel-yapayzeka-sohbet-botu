import unittest
import os
import sys
from pathlib import Path

# Proje ana dizinini yola ekliyoruz ki backend ve database klasörlerini bulabilsin
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.veritabani_islemleri import (
    kullanici_profili_kaydet_veya_guncelle,
    kullanici_profilini_getir,
    karakter_ekle,
    tum_karakterleri_getir,
    karakter_sil,
    tum_cinsiyet_tiplerini_getir,
    tum_rol_tiplerini_getir
)

class TestVeritabaniIslemleri(unittest.TestCase):
    
    def test_01_kullanici_kayit(self):
        """Kullanıcı profili oluşturma ve okuma testi"""
        print("\n[TEST] Kullanıcı kaydediliyor...")
        cinsiyetler = tum_cinsiyet_tiplerini_getir()
        self.assertTrue(len(cinsiyetler) > 0, "Cinsiyet tablosu boş olamaz!")
        
        test_cinsiyet_id = cinsiyetler[0].id
        kullanici_profili_kaydet_veya_guncelle("Test Kullanıcı", test_cinsiyet_id)
        
        kullanici = kullanici_profilini_getir()
        self.assertIsNotNone(kullanici, "Kullanıcı veritabanından çekilemedi!")
        self.assertEqual(kullanici.ad_soyad, "Test Kullanıcı", "Kullanıcı adı eşleşmiyor!")

    def test_02_karakter_ekle_ve_sil(self):
        """Karakter ekleme ve cascade (bağlantılı) silme testi"""
        print("\n[TEST] Karakter eklenip siliniyor...")
        cinsiyetler = tum_cinsiyet_tiplerini_getir()
        roller = tum_rol_tiplerini_getir()
        
        # Test karakteri ekle
        basarili, mesaj, karakter_id = karakter_ekle(
            isim="Test Karakter", 
            rol_id=roller[0].id, 
            cinsiyet_id=cinsiyetler[0].id, 
            sistem_istemi="Bu bir test karakteridir."
        )
        self.assertTrue(basarili, f"Karakter eklenemedi: {mesaj}")
        self.assertIsNotNone(karakter_id, "Karakter ID'si alınamadı!")
        
        # Eklenen karakteri doğrula
        karakterler = tum_karakterleri_getir()
        isimler = [k.isim for k in karakterler]
        self.assertIn("Test Karakter", isimler, "Eklenen karakter listede bulunamadı!")
        
        # Karakteri sil ve silindiğini doğrula
        karakter_sil(karakter_id)
        guncel_karakterler = tum_karakterleri_getir()
        guncel_isimler = [k.isim for k in guncel_karakterler]
        self.assertNotIn("Test Karakter", guncel_isimler, "Karakter silinmesine rağmen hala veritabanında!")

if __name__ == '__main__':
    unittest.main()