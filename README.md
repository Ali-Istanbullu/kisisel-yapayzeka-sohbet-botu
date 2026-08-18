# 🤖 Kişisel Yapay Zeka Sohbet Botu (WhatsApp Klonu)

Tamamen yerel donanımınız üzerinde çalışan, WhatsApp arayüz deneyimine sahip, akıllı hafıza yönetimli ve dinamik model destekli yeni nesil yapay zeka asistanı.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-UI-green?style=for-the-badge)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

---

## ✨ Öne Çıkan Özellikler

* **💬 Gerçekçi WhatsApp Arayüzü:** Aydınlık/Karanlık tema desteği, özel mesaj balonu tasarımı, akıcı sohbet akışı ve anlık "Yazıyor..." simülasyonu.
* **🧠 Uzun Dönem Hafıza & Özetleme:** Sohbetler uzadığında arka planda eski konuşmaları akıllıca özetleyerek bağlamın kopmasını önler.
* **📂 WhatsApp Sohbet Klonlama:** Herhangi bir WhatsApp `.txt` sohbet dışa aktarım dosyasını analiz ederek gerçek bir kişinin üslubunu, emoji kullanım alışkanlıklarını ve konuşma tarzını yapay zekaya klonlayabilirsiniz.
* **⚡ Yerel ve Güvenli Çalışma:** Verileriniz (`sohbet_hafizasi.db`) harici sunucularda değil, tamamen bilgisayarınızın güvenli **AppData** dizininde saklanır.
* **🚀 Akıllı Kurulum Sihirbazı:** Inno Setup destekli kurulum aracı, bilgisayarınızın RAM miktarını otomatik tarayarak size en uygun **Qwen 2.5** modelini önerir ve doğrudan HuggingFace'ten indirir.

---

## 🛠️ Mimari ve Teknolojiler

Proje, performans ve sürdürülebilirlik odaklı modern teknolojilerle inşa edilmiştir:
* **Arayüz (GUI):** `CustomTkinter` (Modern ve şık masaüstü arayüzü)
* **Yapay Zeka Motoru:** `llama-cpp-python` (Donanım hızlandırmalı yerel LLM inference)
* **Veritabanı:** `SQLAlchemy` ORM + SQLite (WAL modu aktif, güvenli ve thread-safe yapı)
* **Paketleme & Dağıtım:** `PyInstaller` (Çekirdek derleme) ve `Inno Setup` (Kurulum sihirbazı ve donanım tarama)

---

## 📥 Kurulum ve Kullanım

1. Projenin **Releases** sekmesine gidin.
2. En son sürümden **`AI_Sohbet_Kurulum_v1.exe`** dosyasını indirin.
3. Çift tıklayarak kurulum sihirbazını başlatın:
   * Sihirbaz sistem RAM'inizi tarayarak size en uygun modeli önerecektir.
   * Seçtiğiniz model doğrudan buluttan indirilecek ve kurulum tamamlanacaktır.
4. Masaüstünüzdeki kısayol ile uygulamayı başlatın ve sohbetin tadını çıkarın!

---

## 📂 Proje Yapısı

```tree
kisisel-yapayzeka-sohbet-botu/
│
├── frontend/
│   └── arayuz.py          # WhatsApp tema ve CustomTkinter ekranları
├── backend/
│   ├── motor.py           # Llama-cpp yapay zeka motoru ve iş parçacığı (threading) yönetimi
│   ├── prompt_olusturucu.py # Dinamik sistem istemi (prompt) ve hafıza entegrasyonu
│   └── whatsapp_analiz.py # .txt sohbet analizi ve üslup çıkarma
├── database/
│   ├── veritabani.py      # SQLAlchemy ORM şemaları ve AppData dizin yönetimi
│   └── veritabani_islemleri.py # CRUD operasyonları ve veri yönetimi
├── baslat.exe             # Ana uygulama başlatıcısı
└── ikon.ico               # Kurulum ve uygulama simgesi
