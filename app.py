from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Ürün Modeli
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='PLN')
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(100))

# API'den ürün çekme fonksiyonu
def fetch_products_from_api():
    try:
        # Örnek API - DummyJSON kullanabiliriz
        response = requests.get('https://dummyjson.com/products')
        products_data = response.json()['products']
        
        for product_data in products_data:
            product = Product(
                name=product_data['title'],
                price=product_data['price'],
                currency='PLN',
                image_url=product_data['thumbnail'],
                category=product_data['category']
            )
            db.session.add(product)
        
        db.session.commit()
        print("Ürünler API'den başarıyla çekildi!")
        
    except Exception as e:
        print(f"API hatası: {e}")

# Ana Sayfa
@app.route('/')
def index():
    products = Product.query.limit(12).all()
    return render_template('index.html', products=products)

# Ürün Detay Sayfası
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Eğer veritabanı boşsa API'den ürünleri çek
        if Product.query.count() == 0:
            fetch_products_from_api()
    app.run(debug=True, port=5000)