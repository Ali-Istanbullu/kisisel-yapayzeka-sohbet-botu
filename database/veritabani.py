import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class CinsiyetTipi(Base):
    __tablename__ = 'cinsiyet_tipleri'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isim = Column(String, nullable=False, unique=True) 

class RolTipi(Base):
    __tablename__ = 'rol_tipleri'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isim = Column(String, nullable=False, unique=True)          
    davranis_aciklamasi = Column(String, nullable=False)        
    karakterler = relationship("Karakter", back_populates="rol")

class KullaniciAyarlari(Base):
    __tablename__ = 'kullanici_ayarlari'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_soyad = Column(String, nullable=False)
    cinsiyet_id = Column(Integer, ForeignKey('cinsiyet_tipleri.id'), nullable=False)
    cinsiyet = relationship("CinsiyetTipi")

class Karakter(Base):
    __tablename__ = 'karakterler'
    id = Column(Integer, primary_key=True, autoincrement=True)
    isim = Column(String, nullable=False)
    rol_id = Column(Integer, ForeignKey('rol_tipleri.id'), nullable=False)
    cinsiyet_id = Column(Integer, ForeignKey('cinsiyet_tipleri.id'), nullable=False)
    sistem_istemi = Column(String, nullable=False)
    uzun_donem_hafiza = Column(String, default="")
    
    rol = relationship("RolTipi", back_populates="karakterler")
    cinsiyet = relationship("CinsiyetTipi")
    mesajlar = relationship("Mesaj", back_populates="karakter")
    whatsapp_profili = relationship("WhatsappUslupProfili", back_populates="karakter", uselist=False, cascade="all, delete-orphan")

class WhatsappUslupProfili(Base):
    __tablename__ = 'whatsapp_uslup_profilleri'
    id = Column(Integer, primary_key=True, autoincrement=True)
    karakter_id = Column(Integer, ForeignKey('karakterler.id'), nullable=False, unique=True)
    kaynak_kisi_adi = Column(String, nullable=False)
    uslup_ozeti = Column(String, nullable=False)
    ornek_mesajlar = Column(String, nullable=False)  
    karakter = relationship("Karakter", back_populates="whatsapp_profili")

class Mesaj(Base):
    __tablename__ = 'mesajlar'
    id = Column(Integer, primary_key=True, autoincrement=True)
    karakter_id = Column(Integer, ForeignKey('karakterler.id'))
    gonderen = Column(String, nullable=False)
    mesaj_metni = Column(String, nullable=False)
    tarih = Column(String, nullable=False)
    karakter = relationship("Karakter", back_populates="mesajlar")

# --- YENİ: GÜVENLİ DİZİN (APPDATA) VE WAL MODU ---
if sys.platform.startswith('win'):
    app_data_path = Path(os.getenv('APPDATA')) / 'YapayZekaSohbetBotu'
else:
    app_data_path = Path.home() / '.yapayzekasohbetbotu'

app_data_path.mkdir(parents=True, exist_ok=True)
db_path = app_data_path / 'sohbet_hafizasi.db'

engine = create_engine(
    f'sqlite:///{db_path}', 
    echo=False,
    connect_args={
        'check_same_thread': False, 
        'isolation_level': None 
    }
)

with engine.connect() as conn:
    conn.execute(text('PRAGMA journal_mode=WAL;'))
    conn.execute(text('PRAGMA synchronous=NORMAL;'))

Session = sessionmaker(bind=engine)

_VARSAYILAN_CINSIYETLER = ["Erkek", "Kadın", "Robot/Tarafsız"]
_VARSAYILAN_ROLLER = {
    "Arkadaş": "Kullanıcının yakın, samimi ve güvenilir bir arkadaşısın. Rahat, esprili ve destekleyici konuşursun.",
    "Sevgili": "Kullanıcının romantik partneri, sevgilisisin. Ona karşı sevgi dolu ve flörtöz bir üslupla konuşursun.",
    "Mentor": "Kullanıcının tecrübeli, bilge bir rehberisin. Yol gösterir, öğüt verirsin.",
    "Asistan": "Kullanıcının kişisel asistanısın. Net, yardımsever ve verimli konuşursun.",
    "Diğer / Belirtilmemiş": "Kullanıcı ile olan ilişkin özeldir. Sadece sistem istemindeki görev ve kurallara sıkı sıkıya bağlı kal."
}

def _lookup_tablolarini_tohumla(session):
    for isim in _VARSAYILAN_CINSIYETLER:
        if not session.query(CinsiyetTipi).filter_by(isim=isim).first():
            session.add(CinsiyetTipi(isim=isim))
            
    for isim, aciklama in _VARSAYILAN_ROLLER.items():
        if not session.query(RolTipi).filter_by(isim=isim).first():
            session.add(RolTipi(isim=isim, davranis_aciklamasi=aciklama))
            
    session.commit()

def _eski_semadan_veri_var_mi(conn, tablo, sutun):
    sonuc = conn.execute(text(f"PRAGMA table_info({tablo})")).fetchall()
    if not sonuc: return None
    sutun_adlari = {satir[1] for satir in sonuc}
    return sutun in sutun_adlari

def _eski_karakterler_semasini_tasi(conn, session):
    if _eski_semadan_veri_var_mi(conn, "karakterler", "rol_id") is not False: return 
    print("Eski karakter şeması tespit edildi, taşınıyor...")
    eski_satirlar = conn.execute(text("SELECT id, isim, rol_tipi, cinsiyet, sistem_istemi FROM karakterler")).fetchall()
    rol_id_haritasi = {r.isim: r.id for r in session.query(RolTipi).all()}
    cinsiyet_id_haritasi = {c.isim: c.id for c in session.query(CinsiyetTipi).all()}
    vars_rol_id = session.query(RolTipi).filter_by(isim="Arkadaş").first().id
    vars_cin_id = session.query(CinsiyetTipi).filter_by(isim="Kadın").first().id
    
    conn.execute(text("DROP TABLE karakterler"))
    conn.commit()
    Base.metadata.create_all(engine, tables=[Karakter.__table__])
    
    for satir in eski_satirlar:
        conn.execute(
            text("INSERT INTO karakterler (id, isim, rol_id, cinsiyet_id, sistem_istemi) VALUES (:id, :isim, :rol_id, :cinsiyet_id, :sistem_istemi)"),
            {"id": satir.id, "isim": satir.isim, "rol_id": rol_id_haritasi.get(satir.rol_tipi, vars_rol_id), "cinsiyet_id": cinsiyet_id_haritasi.get(satir.cinsiyet, vars_cin_id), "sistem_istemi": satir.sistem_istemi},
        )
    conn.commit()

def _eski_kullanici_semasini_tasi(conn, session):
    if _eski_semadan_veri_var_mi(conn, "kullanici_ayarlari", "cinsiyet_id") is not False: return
    print("Eski kullanıcı profili taşınıyor...")
    eski_satirlar = conn.execute(text("SELECT id, ad_soyad, cinsiyet FROM kullanici_ayarlari")).fetchall()
    cinsiyet_id_haritasi = {c.isim: c.id for c in session.query(CinsiyetTipi).all()}
    vars_cin_id = session.query(CinsiyetTipi).filter_by(isim="Kadın").first().id
    
    conn.execute(text("DROP TABLE kullanici_ayarlari"))
    conn.commit()
    Base.metadata.create_all(engine, tables=[KullaniciAyarlari.__table__])
    
    for satir in eski_satirlar:
        conn.execute(text("INSERT INTO kullanici_ayarlari (id, ad_soyad, cinsiyet_id) VALUES (:id, :ad_soyad, :cinsiyet_id)"),
            {"id": satir.id, "ad_soyad": satir.ad_soyad, "cinsiyet_id": cinsiyet_id_haritasi.get(satir.cinsiyet, vars_cin_id)})
    conn.commit()

def _yeni_hafiza_sutununu_ekle(conn):
    if _eski_semadan_veri_var_mi(conn, "karakterler", "uzun_donem_hafiza") is False:
        print("Hafıza sütunu otomatik ekleniyor...")
        conn.execute(text("ALTER TABLE karakterler ADD COLUMN uzun_donem_hafiza VARCHAR DEFAULT ''"))
        conn.commit()

def veritabanini_kur():
    Base.metadata.create_all(engine)
    with Session() as session:
        try:
            _lookup_tablolarini_tohumla(session)
            with engine.connect() as conn:
                _eski_karakterler_semasini_tasi(conn, session)
                _eski_kullanici_semasini_tasi(conn, session)
                _yeni_hafiza_sutununu_ekle(conn)
        except Exception as e:
            print(f"Veritabanı kurulum hatası: {e}")

veritabanini_kur()