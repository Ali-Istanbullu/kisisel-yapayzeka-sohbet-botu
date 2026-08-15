from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# 1. Kök: Ana Kullanıcı Profil Tablosu
class KullaniciAyarlari(Base):
    __tablename__ = 'kullanici_ayarlari'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_soyad = Column(String, nullable=False)
    cinsiyet = Column(String, nullable=False) # 'Erkek' veya 'Kadin'

# 2. Karakterler Tablosu
class Karakter(Base):
    __tablename__ = 'karakterler'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isim = Column(String, nullable=False)
    rol_tipi = Column(String, nullable=False) 
    cinsiyet = Column(String, nullable=False, default="Belirtilmemiş")
    sistem_istemi = Column(String, nullable=False)
    
    mesajlar = relationship("Mesaj", back_populates="karakter")

# 3. Mesajlar Tablosu
class Mesaj(Base):
    __tablename__ = 'mesajlar'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    karakter_id = Column(Integer, ForeignKey('karakterler.id')) 
    gonderen = Column(String, nullable=False) 
    mesaj_metni = Column(String, nullable=False)
    tarih = Column(String, nullable=False)
    
    karakter = relationship("Karakter", back_populates="mesajlar")

engine = create_engine('sqlite:///sohbet_hafizasi.db', echo=False)

def veritabanini_kur():
    Base.metadata.create_all(engine)
    print("Veritabanı en güncel şemayla (Kullanıcı profili dahil) oluşturuldu!")

if __name__ == "__main__":
    veritabanini_kur()