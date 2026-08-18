from sqlalchemy.orm import sessionmaker, joinedload
from database.veritabani import engine, Karakter, Mesaj, KullaniciAyarlari, RolTipi, CinsiyetTipi, WhatsappUslupProfili
from datetime import datetime

Session = sessionmaker(bind=engine)

def tum_rol_tiplerini_getir():
    with Session() as session:
        return session.query(RolTipi).order_by(RolTipi.id).all()

def tum_cinsiyet_tiplerini_getir():
    with Session() as session:
        return session.query(CinsiyetTipi).order_by(CinsiyetTipi.id).all()

def kullanici_profili_kaydet_veya_guncelle(ad_soyad, cinsiyet_id):
    with Session() as session:
        try:
            kullanici = session.query(KullaniciAyarlari).first()
            if kullanici:
                kullanici.ad_soyad, kullanici.cinsiyet_id = ad_soyad, cinsiyet_id
            else: 
                session.add(KullaniciAyarlari(ad_soyad=ad_soyad, cinsiyet_id=cinsiyet_id))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Hata (kullanici profili): {e}")

def kullanici_profilini_getir():
    with Session() as session:
        return session.query(KullaniciAyarlari).options(joinedload(KullaniciAyarlari.cinsiyet)).first()

def karakter_ekle(isim, rol_id, cinsiyet_id, sistem_istemi, maksimum_karakter_siniri=15):
    with Session() as session:
        try:
            if session.query(Karakter).count() >= maksimum_karakter_siniri:
                return False, "Karakter sınırı aşıldı!", None
            yeni_karakter = Karakter(isim=isim, rol_id=rol_id, cinsiyet_id=cinsiyet_id, sistem_istemi=sistem_istemi)
            session.add(yeni_karakter)
            session.commit()
            return True, "Başarılı", yeni_karakter.id
        except Exception as e:
            session.rollback()
            return False, f"Hata oluştu: {e}", None

def karakter_bilgisi_getir(karakter_id):
    with Session() as session:
        return session.query(Karakter).options(
            joinedload(Karakter.rol), joinedload(Karakter.cinsiyet), joinedload(Karakter.whatsapp_profili)
        ).filter_by(id=karakter_id).first()

def tum_karakterleri_getir():
    with Session() as session:
        return session.query(Karakter).all()

def whatsapp_profili_kaydet(karakter_id, kaynak_kisi_adi, uslup_ozeti, ornek_mesajlar_listesi):
    with Session() as session:
        try:
            profil = session.query(WhatsappUslupProfili).filter_by(karakter_id=karakter_id).first()
            ornek_metni = "\n".join(ornek_mesajlar_listesi)
            if profil:
                profil.kaynak_kisi_adi, profil.uslup_ozeti, profil.ornek_mesajlar = kaynak_kisi_adi, uslup_ozeti, ornek_metni
            else: 
                session.add(WhatsappUslupProfili(karakter_id=karakter_id, kaynak_kisi_adi=kaynak_kisi_adi, uslup_ozeti=uslup_ozeti, ornek_mesajlar=ornek_metni))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Hata (whatsapp profili): {e}")

def mesaj_ekle(karakter_id, gonderen, mesaj_metni):
    with Session() as session:
        try:
            tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session.add(Mesaj(karakter_id=karakter_id, gonderen=gonderen, mesaj_metni=mesaj_metni, tarih=tarih))
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Hata (mesaj ekle): {e}")

def mesajlari_sil(mesaj_id_listesi):
    with Session() as session:
        try:
            session.query(Mesaj).filter(Mesaj.id.in_(mesaj_id_listesi)).delete(synchronize_session=False)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Hata (mesajları sil): {e}")

def hafiza_guncelle(karakter_id, yeni_hafiza):
    with Session() as session:
        try:
            karakter = session.query(Karakter).filter_by(id=karakter_id).first()
            if karakter:
                karakter.uzun_donem_hafiza = yeni_hafiza
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Hata (hafıza güncelle): {e}")

def mesaj_gecmisini_getir(karakter_id):
    with Session() as session:
        return session.query(Mesaj).filter_by(karakter_id=karakter_id).order_by(Mesaj.id.asc()).all()

def karakter_sil(karakter_id):
    with Session() as session:
        try:
            session.query(Mesaj).filter_by(karakter_id=karakter_id).delete()
            session.query(WhatsappUslupProfili).filter_by(karakter_id=karakter_id).delete()
            session.query(Karakter).filter_by(id=karakter_id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Hata (karakter sil): {e}")