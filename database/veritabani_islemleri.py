from sqlalchemy.orm import sessionmaker, joinedload
from database.veritabani import engine, Karakter, Mesaj, KullaniciAyarlari, RolTipi, CinsiyetTipi, WhatsappUslupProfili
from datetime import datetime

Session = sessionmaker(bind=engine)

def tum_rol_tiplerini_getir():
    session = Session()
    roller = session.query(RolTipi).order_by(RolTipi.id).all()
    session.close()
    return roller

def tum_cinsiyet_tiplerini_getir():
    session = Session()
    cinsiyetler = session.query(CinsiyetTipi).order_by(CinsiyetTipi.id).all()
    session.close()
    return cinsiyetler

def kullanici_profili_kaydet_veya_guncelle(ad_soyad, cinsiyet_id):
    session = Session()
    kullanici = session.query(KullaniciAyarlari).first()
    if kullanici:
        kullanici.ad_soyad, kullanici.cinsiyet_id = ad_soyad, cinsiyet_id
    else: session.add(KullaniciAyarlari(ad_soyad=ad_soyad, cinsiyet_id=cinsiyet_id))
    session.commit()
    session.close()

def kullanici_profilini_getir():
    session = Session()
    kullanici = session.query(KullaniciAyarlari).options(joinedload(KullaniciAyarlari.cinsiyet)).first()
    session.close()
    return kullanici

def karakter_ekle(isim, rol_id, cinsiyet_id, sistem_istemi, maksimum_karakter_siniri=15):
    session = Session()
    if session.query(Karakter).count() >= maksimum_karakter_siniri:
        session.close()
        return False, "Karakter sınırı aşıldı!", None
    yeni_karakter = Karakter(isim=isim, rol_id=rol_id, cinsiyet_id=cinsiyet_id, sistem_istemi=sistem_istemi)
    session.add(yeni_karakter)
    session.commit()
    y_id = yeni_karakter.id
    session.close()
    return True, "Başarılı", y_id

def karakter_bilgisi_getir(karakter_id):
    session = Session()
    karakter = session.query(Karakter).options(
        joinedload(Karakter.rol), joinedload(Karakter.cinsiyet), joinedload(Karakter.whatsapp_profili)
    ).filter_by(id=karakter_id).first()
    session.close()
    return karakter

def tum_karakterleri_getir():
    session = Session()
    karakterler = session.query(Karakter).all()
    session.close()
    return karakterler

def whatsapp_profili_kaydet(karakter_id, kaynak_kisi_adi, uslup_ozeti, ornek_mesajlar_listesi):
    session = Session()
    profil = session.query(WhatsappUslupProfili).filter_by(karakter_id=karakter_id).first()
    ornek_metni = "\n".join(ornek_mesajlar_listesi)
    if profil:
        profil.kaynak_kisi_adi, profil.uslup_ozeti, profil.ornek_mesajlar = kaynak_kisi_adi, uslup_ozeti, ornek_metni
    else: session.add(WhatsappUslupProfili(karakter_id=karakter_id, kaynak_kisi_adi=kaynak_kisi_adi, uslup_ozeti=uslup_ozeti, ornek_mesajlar=ornek_metni))
    session.commit()
    session.close()

def mesaj_ekle(karakter_id, gonderen, mesaj_metni):
    session = Session()
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session.add(Mesaj(karakter_id=karakter_id, gonderen=gonderen, mesaj_metni=mesaj_metni, tarih=tarih))
    session.commit()
    session.close()

def mesajlari_sil(mesaj_id_listesi):
    session = Session()
    session.query(Mesaj).filter(Mesaj.id.in_(mesaj_id_listesi)).delete(synchronize_session=False)
    session.commit()
    session.close()

def hafiza_guncelle(karakter_id, yeni_hafiza):
    session = Session()
    karakter = session.query(Karakter).filter_by(id=karakter_id).first()
    if karakter:
        karakter.uzun_donem_hafiza = yeni_hafiza
        session.commit()
    session.close()

def mesaj_gecmisini_getir(karakter_id):
    session = Session()
    mesajlar = session.query(Mesaj).filter_by(karakter_id=karakter_id).order_by(Mesaj.id.asc()).all()
    session.close()
    return mesajlar

# --- YENİ EKLENEN FONKSİYON: VERİTABANINDAN KOMPLE SİLME ---
def karakter_sil(karakter_id):
    session = Session()
    # Önce o karaktere ait tüm mesajları ve profilleri sil (Temizlik)
    session.query(Mesaj).filter_by(karakter_id=karakter_id).delete()
    session.query(WhatsappUslupProfili).filter_by(karakter_id=karakter_id).delete()
    # En son karakterin kendisini sil
    session.query(Karakter).filter_by(id=karakter_id).delete()
    session.commit()
    session.close()