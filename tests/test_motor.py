import unittest
from unittest.mock import patch
import sys
import os

# Proje ana dizinini yola ekliyoruz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.motor import YapayZekaMotoru

# Sahte veritabanı mesajı objesi
class SahteMesaj:
    def __init__(self, gonderen, metin):
        self.gonderen = gonderen
        self.mesaj_metni = metin

class TestMotor(unittest.TestCase):
    
    # Burada Python'a diyoruz ki: "Llama'yı ve ayarları yüklemeye kalkma, onların yerine sahtelerini kullan!"
    @patch('backend.motor.Llama') 
    @patch('backend.motor.ayarlari_oku')
    def setUp(self, mock_ayarlar, mock_llama):
        # Ayarlar dosyası sanki varmış gibi sahte bir veri döndürüyoruz
        mock_ayarlar.return_value = {"model_dosya_adi": "sahte_model.gguf", "gpu_kullanimi": False}
        
        # Motoru başlatıyoruz (Sahte Llama sayesinde saniyesinde açılacak)
        self.motor = YapayZekaMotoru()
        
        # Motor cevap üretmeye çalıştığında ona her zaman şu sabit sahte metni verdirtiyoruz
        self.motor.llm.create_chat_completion.return_value = {
            "choices": [
                {"message": {"content": "Bu tamamen sahte bir yapay zeka cevabıdır."}}
            ]
        }

    def test_yanit_uret_blok(self):
        """1. FONKSİYON TESTİ: Motor, mesaj geçmişini doğru birleştirip LLM'e yolluyor mu?"""
        gecmis = [SahteMesaj("Kullanici", "Naber?"), SahteMesaj("Bot", "İyiyim!")]
        
        # Motorun cevap üretme fonksiyonunu tetikliyoruz
        cevap = self.motor.yanit_uret_blok("Sen bir botsun.", gecmis, "Günün nasıl geçti?")
        
        # 1. Bize gerçekten ayarladığımız sahte cevabı mı döndü?
        self.assertEqual(cevap, "Bu tamamen sahte bir yapay zeka cevabıdır.")
        
        # 2. Arka planda Llama'nın create_chat_completion fonksiyonu gerçekten tetiklendi mi?
        self.assertTrue(self.motor.llm.create_chat_completion.called, "Yapay Zeka motoru hiç çağrılmadı!")
        
        # 3. LLM'e gönderilen dizilim doğru mu? (En başta sistem promptu, en sonda kullanıcının son mesajı olmalı)
        cagri_argumanlari = self.motor.llm.create_chat_completion.call_args[1]['messages']
        self.assertEqual(cagri_argumanlari[0]['role'], 'system', "İlk mesaj sistem promptu değil!")
        self.assertEqual(cagri_argumanlari[-1]['content'], 'Günün nasıl geçti?', "Son mesaj hedefe ulaşmamış!")

    def test_hafiza_ozeti_olustur(self):
        """2. FONKSİYON TESTİ: Hafıza özetleyici arka planda doğru formatta çalışıyor mu?"""
        ozet = self.motor.hafiza_ozeti_olustur("Eski hafıza", "Yeni mesajlar burada")
        
        # Ozetleyici de aynı sahte cevabı döndürmeli
        self.assertEqual(ozet, "Bu tamamen sahte bir yapay zeka cevabıdır.")
        
        # Sistem promptunda "Sen bir hafıza özetleyicisin" komutu gerçekten modele gitmiş mi?
        cagri_argumanlari = self.motor.llm.create_chat_completion.call_args[1]['messages']
        self.assertIn("hafıza özetleyicisin", cagri_argumanlari[0]['content'], "Özetleme talimatı yanlış gönderilmiş!")

if __name__ == '__main__':
    unittest.main(verbosity=2)