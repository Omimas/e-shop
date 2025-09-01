from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
import ast
from datetime import datetime, timedelta
from functools import wraps
import random
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'omimas-secret-key-2024'
db = SQLAlchemy(app)

# Kullanıcı Modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Ürün Modeli
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='PLN')
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    images = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Sepet Modeli
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='cart_items')

# Kategori Modeli
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True)

# Yorum Modeli
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref='reviews')
    product = db.relationship('Product', backref='reviews')

# Sipariş Modeli
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(50), default='pending')
    blik_code = db.Column(db.String(6))
    shipping_address = db.Column(db.Text)
    billing_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order')

# Sipariş Ürünleri Modeli
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product', backref='order_items')

# Kargo Takip Modeli
class ShippingTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    tracking_number = db.Column(db.String(50), unique=True)
    carrier = db.Column(db.String(100))
    status = db.Column(db.String(100))
    estimated_delivery = db.Column(db.DateTime)
    actual_delivery = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', backref='tracking')

# Login gerektiren sayfalar için decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# API'den ürün çekme fonksiyonu
def fetch_products_from_api():
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
                images=str(product_data['images'])
            )
            db.session.add(product)
        
        db.session.commit()
        print(f"{len(products_data)} ürün API'den başarıyla çekildi!")
        
    except Exception as e:
        print(f"API hatası: {e}")

# Yorum Ortalaması Hesaplama
def calculate_product_rating(product_id):
    reviews = Review.query.filter_by(product_id=product_id, is_approved=True).all()
    if not reviews:
        return 0, 0
    
    total_rating = sum(review.rating for review in reviews)
    average_rating = total_rating / len(reviews)
    return round(average_rating, 1), len(reviews)

# Ana Sayfa
@app.route('/')
def index():
    products = Product.query.limit(12).all()
    categories = Category.query.all()
    return render_template('index.html', products=products, categories=categories)

# Arama Sayfası
@app.route('/search')
def search():
    query = request.args.get('q', '')
    category_filter = request.args.get('category', '')
    
    products_query = Product.query
    
    if query:
        products_query = products_query.filter(
            (Product.name.ilike(f'%{query}%')) | 
            (Product.description.ilike(f'%{query}%'))
        )
    
    if category_filter:
        products_query = products_query.filter(Product.category.ilike(f'%{category_filter}%'))
    
    products = products_query.all()
    categories = Category.query.all()
    
    return render_template('search.html', products=products, query=query, 
                         categories=categories, category_filter=category_filter)

# Ürün Detay Sayfası
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Benzer ürünler
    similar_products = Product.query.filter(
        Product.category == product.category,
        Product.id != product.id
    ).limit(4).all()
    
    # Resimleri string'den listeye çevir
    try:
        product_images = ast.literal_eval(product.images)
    except:
        product_images = [product.image_url]
    
    # Yorum ortalaması
    product_rating = calculate_product_rating(product_id)
    
    return render_template('product.html', product=product, 
                         product_images=product_images, 
                         similar_products=similar_products,
                         product_rating=product_rating)

# Kategori Sayfası
@app.route('/category/<category_name>')
def category_page(category_name):
    products = Product.query.filter(Product.category.ilike(f'%{category_name}%')).all()
    return render_template('category.html', products=products, category_name=category_name)

# Ürün Yorumları
@app.route('/product/<int:product_id>/reviews')
def product_reviews(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id, is_approved=True).order_by(Review.created_at.desc()).all()
    product_rating = calculate_product_rating(product_id)
    return render_template('reviews.html', product=product, reviews=reviews, product_rating=product_rating)

# Yorum Ekleme
@app.route('/product/<int:product_id>/add_review', methods=['POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    rating = int(request.form['rating'])
    comment = request.form['comment'].strip()
    
    # Validasyon
    if not 1 <= rating <= 5:
        flash('Rating must be between 1 and 5 stars!', 'danger')
        return redirect(url_for('product_detail', product_id=product_id))
    
    if len(comment) < 10:
        flash('Comment must be at least 10 characters long!', 'danger')
        return redirect(url_for('product_detail', product_id=product_id))
    
    # Yorumu kaydet
    review = Review(
        product_id=product_id,
        user_id=session['user_id'],
        rating=rating,
        comment=comment
    )
    
    db.session.add(review)
    db.session.commit()
    
    flash('Thank you for your review! It will be visible after approval.', 'success')
    return redirect(url_for('product_detail', product_id=product_id))

# Yorum Düzenleme
@app.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    if review.user_id != session['user_id']:
        flash('You can only edit your own reviews!', 'danger')
        return redirect(url_for('product_detail', product_id=review.product_id))
    
    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form['comment'].strip()
        
        review.rating = rating
        review.comment = comment
        db.session.commit()
        
        flash('Review updated successfully!', 'success')
        return redirect(url_for('product_detail', product_id=review.product_id))
    
    return render_template('edit_review.html', review=review)

# Yorum Silme
@app.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    product_id = review.product_id
    
    if review.user_id != session['user_id']:
        flash('You can only delete your own reviews!', 'danger')
        return redirect(url_for('product_detail', product_id=product_id))
    
    db.session.delete(review)
    db.session.commit()
    
    flash('Review deleted successfully!', 'success')
    return redirect(url_for('product_detail', product_id=product_id))

# KAYIT İŞLEMLERİ
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('register'))
        
        # Yeni kullanıcı oluştur
        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# GİRİŞ İŞLEMLERİ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hem username hem email ile deneme
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if user:
            if user.check_password(password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['email'] = user.email
                
                flash('Welcome back, {user.username}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid password!', 'danger')
        else:
            flash('User not found!', 'danger')
    
    return render_template('login.html')

# ÇIKIŞ İŞLEMLERİ
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# HESABIM SAYFASI - DÜZELTİLMİŞ
@app.route('/account')
@login_required
def account():
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('index'))
    return render_template('account.html', user=user)

# SEPET İŞLEMLERİ - MİSAFİR DESTEKLİ
@app.route('/cart')
def cart():
    if 'user_id' in session:
        # Giriş yapmış kullanıcı
        cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
        total = sum(item.product.price * item.quantity for item in cart_items)
        cart_type = 'user'
    else:
        # Misafir kullanıcı
        cart_items = []
        guest_cart = session.get('guest_cart', {})
        for product_id, quantity in guest_cart.items():
            product = Product.query.get(int(product_id))
            if product:
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'id': product_id
                })
        total = sum(item['product'].price * item['quantity'] for item in cart_items)
        cart_type = 'guest'
    
    return render_template('cart.html', cart_items=cart_items, total=total, cart_type=cart_type)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    if 'user_id' in session:
        # Giriş yapmış kullanıcı
        cart_item = Cart.query.filter_by(
            user_id=session['user_id'], 
            product_id=product_id
        ).first()
        
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(
                user_id=session['user_id'],
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'{product.name} added to cart!', 'type': 'user'})
    else:
        # Misafir kullanıcı
        guest_cart = session.get('guest_cart', {})
        product_id_str = str(product_id)
        
        if product_id_str in guest_cart:
            guest_cart[product_id_str] += quantity
        else:
            guest_cart[product_id_str] = quantity
        
        session['guest_cart'] = guest_cart
        session.modified = True
        
        return jsonify({'success': True, 'message': f'{product.name} added to cart!', 'type': 'guest'})

# Sepet sayacı API
@app.route('/api/cart_count')
def api_cart_count():
    if 'user_id' in session:
        count = Cart.query.filter_by(user_id=session['user_id']).count()
        return jsonify({'count': count})
    else:
        guest_cart = session.get('guest_cart', {})
        return jsonify({'count': len(guest_cart)})

# Sepetten ürün silme
@app.route('/remove_from_cart/<item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if 'user_id' in session:
        cart_item = Cart.query.get_or_404(int(item_id))
        if cart_item.user_id != session['user_id']:
            flash('Unauthorized action!', 'danger')
            return redirect(url_for('cart'))
        
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart!', 'success')
    else:
        guest_cart = session.get('guest_cart', {})
        if item_id in guest_cart:
            del guest_cart[item_id]
            session['guest_cart'] = guest_cart
            session.modified = True
            flash('Item removed from cart!', 'success')
        else:
            flash('Item not found in cart!', 'danger')
    
    return redirect(url_for('cart'))

# Sepeti güncelleme
@app.route('/update_cart/<item_id>', methods=['POST'])
def update_cart(item_id):
    quantity = request.form.get('quantity', 1)
    
    try:
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
        if quantity > 10:
            quantity = 10
    except:
        quantity = 1
    
    if 'user_id' in session:
        cart_item = Cart.query.get_or_404(int(item_id))
        if cart_item.user_id != session['user_id']:
            return jsonify({'success': False, 'message': 'Unauthorized'})
        
        cart_item.quantity = quantity
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cart updated'})
    else:
        guest_cart = session.get('guest_cart', {})
        if item_id in guest_cart:
            guest_cart[item_id] = quantity
            session['guest_cart'] = guest_cart
            session.modified = True
            return jsonify({'success': True, 'message': 'Cart updated'})
        else:
            return jsonify({'success': False, 'message': 'Item not found'})

# Misafir sepetini kullanıcı hesabına taşıma
@app.route('/transfer_guest_cart')
@login_required
def transfer_guest_cart():
    guest_cart = session.get('guest_cart', {})
    
    for product_id_str, quantity in guest_cart.items():
        product_id = int(product_id_str)
        
        existing_item = Cart.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = Cart(
                user_id=session['user_id'],
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(new_item)
    
    db.session.commit()
    session.pop('guest_cart', None)
    flash('Your guest cart items have been transferred to your account!', 'success')
    return redirect(url_for('cart'))

# Sepeti temizleme
@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if 'user_id' in session:
        Cart.query.filter_by(user_id=session['user_id']).delete()
        db.session.commit()
        flash('Cart cleared successfully!', 'success')
    else:
        session.pop('guest_cart', None)
        flash('Cart cleared successfully!', 'success')
    
    return redirect(url_for('cart'))

# Session cart count güncelleme
@app.route('/api/update_session_cart', methods=['POST'])
def update_session_cart():
    data = request.get_json()
    if 'cart_count' in data:
        session['cart_count'] = data['cart_count']
    if 'guest_cart_count' in data:
        session['guest_cart_count'] = data['guest_cart_count']
    return jsonify({'success': True})

# Ödeme Sayfası
@app.route('/checkout')
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

# Sipariş Oluşturma
@app.route('/create_order', methods=['POST'])
@login_required
def create_order():
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    if not cart_items:
        return jsonify({'success': False, 'message': 'Cart is empty'})
    
    today = datetime.now().strftime('%Y%m%d')
    last_order = Order.query.filter(Order.order_number.like(f'OM{today}-%')).order_by(Order.id.desc()).first()
    
    if last_order:
        last_number = int(last_order.order_number.split('-')[-1])
        new_number = f'OM{today}-{last_number + 1:04d}'
    else:
        new_number = f'OM{today}-0001'
    
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
    # Sadece isim ve adres zorunlu
    order = Order(
        order_number=new_number,
        user_id=session['user_id'],
        total_amount=total_amount,
        shipping_address=request.form['shipping_address'],
        billing_address=request.form.get('billing_address', ''),
        payment_method=request.form['payment_method']
    )
    
    db.session.add(order)
    db.session.flush()
    
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.session.add(order_item)
    
    Cart.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'order_id': order.id,
        'order_number': order.order_number
    })

# BLIK Ödeme
@app.route('/pay_with_blik/<int:order_id>', methods=['POST'])
@login_required
def pay_with_blik(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    blik_code = request.form.get('blik_code', '')
    
    # BLIK kodu validasyonu (6 haneli rakam)
    if not blik_code.isdigit() or len(blik_code) != 6:
        return jsonify({'success': False, 'message': 'Invalid BLIK code. Must be 6 digits.'})
    
    # Ödeme simülasyonu (her zaman başarılı)
    order.payment_status = 'completed'
    order.status = 'paid'
    order.blik_code = blik_code
    order.updated_at = datetime.utcnow()
    
    # Kargo takip numarası oluştur
    tracking_number = f'TRK{random.randint(1000000000, 9999999999)}'
    
    shipping = ShippingTracking(
        order_id=order.id,
        tracking_number=tracking_number,
        carrier='DHL',
        status='label_created',
        estimated_delivery=datetime.utcnow().replace(hour=23, minute=59, second=59) + timedelta(days=3)
    )
    db.session.add(shipping)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Payment successful!',
        'tracking_number': tracking_number,
        'order_number': order.order_number
    })

# Kredi Kartı Ödeme - DÜZELTİLMİŞ
@app.route('/pay_with_credit_card/<int:order_id>', methods=['POST'])
@login_required
def pay_with_credit_card(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    # Kredi kartı bilgilerini al - request.form.get() kullan
    card_number = request.form.get('card_number', '').replace(' ', '')
    expiry_date = request.form.get('expiry_date', '')
    cvv = request.form.get('cvv', '')
    card_holder = request.form.get('card_holder', '')
    
    # Sadece 16 hane kontrolü (diğer alanlar zorunlu değil)
    if not card_number or len(card_number) != 16 or not card_number.isdigit():
        return jsonify({'success': False, 'message': 'Invalid card number. Must be 16 digits.'})
    
    # Ödeme simülasyonu (HER ZAMAN BAŞARILI)
    order.payment_status = 'completed'
    order.status = 'paid'
    order.updated_at = datetime.utcnow()
    
    # Kargo takip numarası oluştur
    tracking_number = f'TRK{random.randint(1000000000, 9999999999)}'
    
    shipping = ShippingTracking(
        order_id=order.id,
        tracking_number=tracking_number,
        carrier='UPS',
        status='label_created',
        estimated_delivery=datetime.utcnow().replace(hour=23, minute=59, second=59) + timedelta(days=2)
    )
    db.session.add(shipping)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Payment successful!',
        'tracking_number': tracking_number,
        'order_number': order.order_number
    })

# Sipariş Takip
@app.route('/order/<order_number>')
@login_required
def order_tracking(order_number):
    order = Order.query.filter_by(order_number=order_number, user_id=session['user_id']).first_or_404()
    return render_template('order_tracking.html', order=order)

# Sipariş Geçmişi
@app.route('/orders')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('order_history.html', orders=orders)

# Sipariş Simülasyon API
@app.route('/api/simulate_order/<order_number>')
@login_required
def simulate_order(order_number):
    order = Order.query.filter_by(order_number=order_number, user_id=session['user_id']).first_or_404()
    
    # Sipariş durumunu güncelle (simülasyon)
    stages = [
        {'status': 'confirmed', 'message': 'Order confirmed', 'delay': 3},
        {'status': 'processing', 'message': 'Preparing for shipment', 'delay': 5},
        {'status': 'shipped', 'message': 'Shipped with DHL', 'delay': 8},
        {'status': 'out_for_delivery', 'message': 'Out for delivery', 'delay': 12},
        {'status': 'delivered', 'message': 'Delivered successfully', 'delay': 15}
    ]
    
    current_status = order.status
    current_index = next((i for i, stage in enumerate(stages) if stage['status'] == current_status), 0)
    
    if current_index < len(stages) - 1:
        next_stage = stages[current_index + 1]
        order.status = next_stage['status']
        order.updated_at = datetime.utcnow()
        db.session.commit()
    
    return jsonify({
        'success': True,
        'status': order.status,
        'message': f'Order status updated to {order.status}'
    })

# API Endpoint - Ürün Listesi
@app.route('/api/products')
def api_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'currency': p.currency,
        'image_url': p.image_url,
        'category': p.category
    } for p in products])

# Veritabanı init fonksiyonu
def init_database():
    with app.app_context():
        db.create_all()
        
        categories = [
            'smartphones', 'laptops', 'fragrances', 'skincare', 
            'groceries', 'home-decoration', 'furniture', 'tops', 
            'womens-dresses', 'womens-shoes', 'mens-shirts', 
            'mens-shoes', 'mens-watches', 'womens-watches', 
            'womens-bags', 'womens-jewellery', 'sunglasses', 
            'automotive', 'motorcycle', 'lighting'
        ]
        
        for cat in categories:
            if not Category.query.filter_by(slug=cat).first():
                category = Category(name=cat.replace('-', ' ').title(), slug=cat)
                db.session.add(category)
        
        if Product.query.count() == 0:
            fetch_products_from_api()
        
        if User.query.count() == 0:
            admin = User(username='admin', email='admin@omimas.pl', first_name='Admin', last_name='User')
            admin.set_password('admin123')
            db.session.add(admin)
            print("Örnek admin kullanıcısı oluşturuldu: admin / admin123")
        
        db.session.commit()
        print(f"Veritabanı hazır! {Product.query.count()} ürün, {Category.query.count()} kategori, {User.query.count()} kullanıcı.")

if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5000, host='0.0.0.0')