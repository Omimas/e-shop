🛒 Omimas E-Ticaret Projesi - Teknik Detaylar
📋 Proje Özeti
Omimas, Polonya pazarına yönelik tam fonksiyonel bir e-ticaret platformudur. Allegro benzeri modern bir alışveriş deneyimi sunar.

🛠️ Kullanılan Teknolojiler
Backend:
Python 3.12 - Ana programlama dili

Flask 2.3.3 - Web framework

Flask-SQLAlchemy 3.0.5 - ORM ve database yönetimi

SQLite - Veritabanı (geliştirme ortamı için)

Werkzeug - Şifre hashleme ve güvenlik

Frontend:
HTML5 - Sayfa yapısı

CSS3 - Tasarım ve responsive layout

JavaScript - Dinamik işlevler

Jinja2 - Template engine

Font Awesome 6 - İkonlar

API Entegrasyonları:
DummyJSON API - Ürün verileri için

RESTful API - Kendi backend API'lerimiz

🗃️ Veritabanı Yapısı
Modeller:
User - Kullanıcı bilgileri ve kimlik doğrulama

Product - Ürün katalog ve detayları

Category - Kategori yönetimi

Cart - Sepet işlemleri

Order - Sipariş yönetimi

OrderItem - Sipariş detayları

Review - Ürün yorum ve rating sistemi

ShippingTracking - Kargo takip sistemi

🌐 Veri Kaynakları
1. Ürün Verileri
Kaynak: DummyJSON API (https://dummyjson.com/products)

Yöntem: REST API GET isteği

İşlem: API'den gelen veriler otomatik olarak SQLite veritabanına kaydediliyor

Dönüşüm: USD fiyatlar PLN'ye çevriliyor (1 USD = 4 PLN)

2. Kategori Verileri
Kaynak: Manuel olarak tanımlandı (20+ kategori)

Yapı: Smartphones, Laptops, Fragrances, Skincare, Groceries, vb.

3. Kullanıcı Verileri
Kaynak: Kullanıcı kayıt formu

Güvenlik: Şifreler hashlenerek saklanıyor

⚙️ Proje Özellikleri
Temel Özellikler:
✅ Kullanıcı kayıt ve giriş sistemi

✅ Ürün katalog ve arama

✅ Sepet yönetimi (misafir/üye)

✅ Ödeme sistemi (BLIK + Kredi Kartı)

✅ Sipariş takip ve yönetimi

✅ Ürün yorum ve rating sistemi

Gelişmiş Özellikler:
🚀 Responsive tasarım (mobil uyumlu)

🚀 Gerçek zamanlı sepet güncelleme

🚀 Sipariş simülasyon ve takip

🚀 API entegrasyonları

🚀 Güvenli ödeme sistemi

📊 Teknik Detaylar
Database Bağlantısı:
python
# SQLite veritabanı bağlantısı
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
API Entegrasyonu:
python
# Ürünleri API'den çekme
response = requests.get('https://dummyjson.com/products?limit=20')
products_data = response.json()['products']
Güvenlik:
python
# Şifre hashleme
user.set_password(password)  # SHA256 ile hashleniyor
user.check_password(password)  # Güvenli doğrulama
🎯 Projenin Yenilikçi Yönleri
Çift Ödeme Sistemi - BLIK (Polonya'ya özel) + Kredi Kartı

Gerçek Zamanlı Takip - Sipariş durumu simülasyonu

Misafir Alışverişi - Üye olmadan sepete ekleme

API Entegrasyonu - Gerçek ürün verileri

Responsive Tasarım - Tüm cihazlarda çalışır

📈 Performans Optimizasyonları
Lazy Loading - Gerektiğinde veri çekme

Database Indexing - Hızlı arama ve sorgular

Session Management - Etkili kullanıcı yönetimi

Error Handling - Kapsamlı hata yönetimi

🔒 Güvenlik Önlemleri
Şifre hashleme (Werkzeug)

SQL injection koruması (SQLAlchemy)

XSS koruması (Jinja2 template escaping)

Session güvenliği

Form validation

---------------------------------------------

Önce demo yapın (ana sayfa → ürün → sepet → ödeme)

BLIK ödemesini gösterin (Polonya'ya özel)

Sipariş takip simülasyonunu gösterin

Responsive tasarımı gösterin (mobil görünüm)

Teknoloji stack'ini anlatın

Veri akışını açıklayın (API → Database → Frontend)
