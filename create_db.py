from app import app, db, Product, Category
import requests
from datetime import datetime

def init_database():
    with app.app_context():
        print("Veritabanı tabloları oluşturuluyor...")
        db.drop_all()  # Önce tüm tabloları sil
        db.create_all()  # Yeniden oluştur
        
        print("Kategoriler ekleniyor...")
        # Kategorileri ekle
        categories = [
            'smartphones', 'laptops', 'fragrances', 'skincare', 
            'groceries', 'home-decoration', 'furniture', 'tops', 
            'womens-dresses', 'womens-shoes', 'mens-shirts', 
            'mens-shoes', 'mens-watches', 'womens-watches', 
            'womens-bags', 'womens-jewellery', 'sunglasses', 
            'automotive', 'motorcycle', 'lighting'
        ]
        
        for cat in categories:
            category = Category(name=cat.replace('-', ' ').title(), slug=cat)
            db.session.add(category)
        
        db.session.commit()
        print("Kategoriler eklendi!")
        
        print("Ürünler API'den çekiliyor...")
        # API'den ürünleri çek
        try:
            response = requests.get('https://dummyjson.com/products?limit=20')
            products_data = response.json()['products']
            
            for product_data in products_data:
                price_pln = product_data['price'] * 4
                
                product = Product(
                    name=product_data['title'],
                    price=round(price_pln, 2),
                    currency='PLN',
                    image_url=product_data['thumbnail'],
                    category=product_data['category'],
                    description=product_data['description'],
                    images=str(product_data['images']),
                    created_at=datetime.utcnow()
                )
                db.session.add(product)
            
            db.session.commit()
            print(f"{len(products_data)} ürün eklendi!")
            
        except Exception as e:
            print(f"API hatası: {e}")
        
        print("Veritabanı hazır!")
        print(f"Toplam {Product.query.count()} ürün")
        print(f"Toplam {Category.query.count()} kategori")

if __name__ == '__main__':
    init_database()