from sqlalchemy.orm import sessionmaker
from veritabani import engine, Karakter, Mesaj, KullaniciAyarlari
from datetime import datetime

Session = sessionmaker(bind=engine)

# --- AĞAÇ KÖKÜ: KULLANICI İŞLEMLERİ ---
def kullanici_profili_kaydet_veya_guncelle(ad_soyad, cinsiyet):
    session = Session()
    kullanici = session.query(KullaniciAyarlari).first()
    if kullanici:
        kullanici.ad_soyad = ad_soyad
        kullanici.cinsiyet = cinsiyet
    else:
        kullanici = KullaniciAyarlari(ad_soyad=ad_soyad, cinsiyet=cinsiyet)
        session.add(kullanici)
    session.commit()
    session.close()

def kullanici_profilini_getir():
    session = Session()
    kullanici = session.query(KullaniciAyarlari).first()
    session.close()
    return kullanici

# --- DAL 1: KARAKTER İŞLEMLERİ ---
# --- DAL 1: KARAKTER İŞLEMLERİ ---
# Cinsiyet parametresini ekledik
def karakter_ekle(isim, rol_tipi, cinsiyet, sistem_istemi, maksimum_karakter_siniri=5):
    session = Session()
    mevcut = session.query(Karakter).count()
    if mevcut >= maksimum_karakter_siniri:
        session.close()
        return False, "Karakter sınırı aşıldı!"
    
    # Karakter oluşturulurken cinsiyet verisini de kaydediyoruz
    yeni_karakter = Karakter(isim=isim, rol_tipi=rol_tipi, cinsiyet=cinsiyet, sistem_istemi=sistem_istemi)
    session.add(yeni_karakter)
    session.commit()
    session.close()
    return True, "Karakter başarıyla eklendi."

def karakter_bilgisi_getir(karakter_id):
    session = Session()
    karakter = session.query(Karakter).filter_by(id=karakter_id).first()
    session.close()
    return karakter

# --- DAL 2: MESAJ VE HAFIZA İŞLEMLERİ ---
def mesaj_ekle_ve_buda(karakter_id, gonderen, mesaj_metni, maksimum_mesaj_siniri=40):
    session = Session()
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    yeni_mesaj = Mesaj(karakter_id=karakter_id, gonderen=gonderen, mesaj_metni=mesaj_metni, tarih=tarih)
    session.add(yeni_mesaj)
    session.commit()
    
    mesajlar = session.query(Mesaj).filter_by(karakter_id=karakter_id).order_by(Mesaj.id.desc()).all()
    if len(mesajlar) > maksimum_mesaj_siniri:
        silinecekler = mesajlar[maksimum_mesaj_siniri:] 
        for eski in silinecekler:
            session.delete(eski)
        session.commit()
    session.close()

def mesaj_gecmisini_getir(karakter_id):
    session = Session()
    mesajlar = session.query(Mesaj).filter_by(karakter_id=karakter_id).order_by(Mesaj.id.asc()).all()
    session.close()
    return mesajlar

def tum_karakterleri_getir():
    """Sol panel için veritabanındaki tüm karakterleri getirir."""
    session = Session()
    karakterler = session.query(Karakter).all()
    session.close()
    return karakterler