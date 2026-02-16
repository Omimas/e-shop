# Omimas E-Commerce Platform (In Development)

A high-performance, Flask-based e-commerce solution tailored for the Polish market. This project features a modern architecture similar to platforms like Allegro, focusing on localized UI/UX, core e-commerce logic, and secure authentication.

## 🚀 Key Features

* **Dynamic Inventory:** Integrated with **DummyJSON API** to fetch and synchronize real product data into a local SQLite database.
* **Localization (Poland):** Support for **PLN** currency conversion and **BLIK** payment simulation **(UI Concept)**.
* **User Management:** Secure authentication system with password hashing (SHA256) and session management.
* **Advanced Cart & Checkout:** Real-time cart updates, guest checkout support, and a simulated order tracking system.
* **Review System (UI Concept):** Designed interface for user-generated content and rating logic.

## 🛠️ Technical Stack

* **Backend:** Python 3.12, Flask 2.3.3
* **Database (ORM):** Flask-SQLAlchemy 3.0.5 with SQLite (Development)
* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Jinja2 Template Engine
* **Security:** Werkzeug (Password Hashing), SQLAlchemy (SQLi Protection)
* **UI Elements:** Font Awesome 6

## 📂 Project Architecture

### **Database Schema**
The system relies on a relational database design with the following core models:
* `User`: Authentication and profile management.
* `Product & Category`: Inventory management with 20+ predefined categories.
* `Cart & Order`: Transactional logic and order item tracking.
* `ShippingTracking (Simulated)`: Interface for real-time order status simulation.

### **API Integration & Data Processing**
Products are fetched from the external DummyJSON API and processed locally:
```python
# Real-time API Fetching Logic
response = requests.get('[https://dummyjson.com/products?limit=20](https://dummyjson.com/products?limit=20)')
products_data = response.json()['products']
# Data is then mapped and converted (1 USD = 4 PLN)
