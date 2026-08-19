"""
Projenin TEK merkezi loglama noktası. Her dosyadaki except bloğu artık
kendi başına print(str(e)) yapmak yerine buradaki hata_logla() fonksiyonunu
çağırır. Bu sayede:

  - Hata mesajı asla sessizce kaybolmaz (önceki hafta yaşadığımız
    "Cevap üretilemedi" sorununda olduğu gibi - gerçek sebep hiç
    görünmüyordu).
  - Tam stack trace (hangi dosya, hangi satır) hem konsola hem de
    kalıcı bir dosyaya (hatalar.log) yazılır - uygulama kapansa bile
    log dosyası kalır, sonradan incelenebilir.
  - Tek bir yerden formatı/seviyeyi değiştirmek yeterli, her dosyayı
    tek tek değiştirmek gerekmez.

Kullanımı (SADECE bir except bloğunun İÇİNDEN çağrılmalı):

    try:
        ...
    except Exception:
        hata_logla("karakter eklenirken")
        # istersen burada kullanıcıya gösterilecek genel bir mesaj da ayarla
"""

import logging
import os
import sys
from pathlib import Path

# Log dosyasını da veritabaniyla AYNI güvenli (APPDATA / home) klasöre koyuyoruz -
# proje klasörüne değil, çünkü .exe olunca proje klasörü yazılabilir olmayabilir.
if sys.platform.startswith("win"):
    _log_klasoru = Path(os.getenv("APPDATA", ".")) / "YapayZekaSohbetBotu"
else:
    _log_klasoru = Path.home() / ".yapayzekasohbetbotu"

_log_klasoru.mkdir(parents=True, exist_ok=True)
LOG_DOSYA_YOLU = _log_klasoru / "hatalar.log"

logger = logging.getLogger("yapayzeka_sohbet_botu")
logger.setLevel(logging.DEBUG)

# Modül birden fazla kez import edilse bile handler'ları ikiye katlamayalım
if not logger.handlers:
    dosya_handler = logging.FileHandler(LOG_DOSYA_YOLU, encoding="utf-8")
    dosya_handler.setLevel(logging.DEBUG)
    dosya_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )

    konsol_handler = logging.StreamHandler()
    konsol_handler.setLevel(logging.INFO)
    konsol_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(dosya_handler)
    logger.addHandler(konsol_handler)


def hata_logla(baglam: str):
    """
    SADECE bir 'except' bloğunun İÇİNDEN çağrılmalı - o an işlenmekte olan
    exception'ı otomatik yakalar (logging.exception ile aynı mantık) ve
    tam stack trace'i hem konsola hem hatalar.log dosyasına yazar.

    baglam: "karakter eklenirken", "whatsapp analiz edilirken" gibi kısa,
            hangi işlemin sırasında patladığını anlatan bir açıklama.
    """
    logger.exception(baglam)


def bilgi_logla(mesaj: str):
    """Hata olmayan ama kayda değer olayları (ör. motor başlatıldı) loglar."""
    logger.info(mesaj)