from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Sample product data
PRODUCTS = [
    {
        'id': 1,
        'name': 'Laptop',
        'price': 999.99,
        'description': 'High-performance laptop with 16GB RAM',
        'image': 'https://via.placeholder.com/200x200?text=Laptop',
        'stock': 10
    },
    {
        'id': 2,
        'name': 'Wireless Mouse',
        'price': 29.99,
        'description': 'Ergonomic wireless mouse with precision tracking',
        'image': 'https://via.placeholder.com/200x200?text=Mouse',
        'stock': 50
    },
    {
        'id': 3,
        'name': 'Mechanical Keyboard',
        'price': 149.99,
        'description': 'RGB mechanical keyboard with custom switches',
        'image': 'https://via.placeholder.com/200x200?text=Keyboard',
        'stock': 25
    },
    {
        'id': 4,
        'name': 'USB-C Hub',
        'price': 49.99,
        'description': '7-in-1 USB-C hub with HDMI and ethernet',
        'image': 'https://via.placeholder.com/200x200?text=USB+Hub',
        'stock': 30
    },
    {
        'id': 5,
        'name': 'Webcam HD',
        'price': 79.99,
        'description': '1080p HD webcam with built-in microphone',
        'image': 'https://via.placeholder.com/200x200?text=Webcam',
        'stock': 15
    },
    {
        'id': 6,
        'name': 'Headphones',
        'price': 199.99,
        'description': 'Noise-canceling over-ear headphones',
        'image': 'https://via.placeholder.com/200x200?text=Headphones',
        'stock': 20
    }
]

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>TechStore - Home</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        h1 { font-size: 1.8rem; }
        nav a { color: white; text-decoration: none; margin-left: 2rem; }
        nav a:hover { text-decoration: underline; }
        .cart-badge { background: #e74c3c; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.9rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .flash { padding: 1rem; margin-bottom: 1rem; border-radius: 4px; }
        .flash.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .flash.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .products { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem; }
        .product-card { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .product-card:hover { transform: translateY(-5px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
        .product-card img { width: 100%; height: 200px; object-fit: cover; border-radius: 4px; margin-bottom: 1rem; }
        .product-card h3 { color: #2c3e50; margin-bottom: 0.5rem; }
        .product-card p { color: #666; font-size: 0.9rem; margin-bottom: 1rem; }
        .price { color: #27ae60; font-size: 1.4rem; font-weight: bold; margin-bottom: 1rem; }
        .stock { color: #7f8c8d; font-size: 0.85rem; margin-bottom: 1rem; }
        button { background: #3498db; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; font-size: 1rem; width: 100%; }
        button:hover { background: #2980b9; }
        button:disabled { background: #95a5a6; cursor: not-allowed; }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>🛒 TechStore</h1>
            <nav>
                <a href="/">Products</a>
                <a href="/cart">Cart <span class="cart-badge">{{ cart_count }}</span></a>
            </nav>
        </div>
    </header>
    <div class="container">
        {% for message in get_flashed_messages() %}
        <div class="flash success">{{ message }}</div>
        {% endfor %}
        
        <h2 style="margin-bottom: 2rem; color: #2c3e50;">Our Products</h2>
        <div class="products">
            {% for product in products %}
            <div class="product-card">
                <img src="{{ product.image }}" alt="{{ product.name }}">
                <h3>{{ product.name }}</h3>
                <p>{{ product.description }}</p>
                <div class="price">${{ "%.2f"|format(product.price) }}</div>
                <div class="stock">Stock: {{ product.stock }} available</div>
                <form method="POST" action="/add-to-cart/{{ product.id }}">
                    <button type="submit" {% if product.stock == 0 %}disabled{% endif %}>
                        {% if product.stock == 0 %}Out of Stock{% else %}Add to Cart{% endif %}
                    </button>
                </form>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

CART_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>TechStore - Shopping Cart</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        h1 { font-size: 1.8rem; }
        nav a { color: white; text-decoration: none; margin-left: 2rem; }
        nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .cart-item { background: white; padding: 1.5rem; margin-bottom: 1rem; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .item-info { flex: 1; }
        .item-info h3 { color: #2c3e50; margin-bottom: 0.5rem; }
        .item-price { color: #27ae60; font-size: 1.2rem; font-weight: bold; }
        .item-controls { display: flex; gap: 1rem; align-items: center; }
        .quantity { display: flex; gap: 0.5rem; align-items: center; }
        .quantity button { padding: 0.5rem 1rem; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .quantity button:hover { background: #2980b9; }
        .quantity span { min-width: 30px; text-align: center; }
        .remove-btn { background: #e74c3c; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
        .remove-btn:hover { background: #c0392b; }
        .cart-summary { background: white; padding: 2rem; border-radius: 8px; margin-top: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .summary-row { display: flex; justify-content: space-between; margin-bottom: 1rem; font-size: 1.1rem; }
        .summary-row.total { font-size: 1.5rem; font-weight: bold; color: #2c3e50; padding-top: 1rem; border-top: 2px solid #ecf0f1; }
        .checkout-btn { background: #27ae60; color: white; border: none; padding: 1rem 2rem; border-radius: 4px; cursor: pointer; font-size: 1.1rem; width: 100%; margin-top: 1rem; }
        .checkout-btn:hover { background: #229954; }
        .empty-cart { text-align: center; padding: 4rem 2rem; background: white; border-radius: 8px; }
        .empty-cart p { color: #7f8c8d; font-size: 1.2rem; margin-bottom: 2rem; }
        .continue-shopping { background: #3498db; color: white; text-decoration: none; padding: 1rem 2rem; border-radius: 4px; display: inline-block; }
        .continue-shopping:hover { background: #2980b9; }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>🛒 TechStore</h1>
            <nav>
                <a href="/">Products</a>
                <a href="/cart">Cart</a>
            </nav>
        </div>
    </header>
    <div class="container">
        <h2 style="margin-bottom: 2rem; color: #2c3e50;">Shopping Cart</h2>
        
        {% if cart_items %}
            {% for item in cart_items %}
            <div class="cart-item">
                <div class="item-info">
                    <h3>{{ item.name }}</h3>
                    <div class="item-price">${{ "%.2f"|format(item.price) }} each</div>
                </div>
                <div class="item-controls">
                    <div class="quantity">
                        <form method="POST" action="/update-cart/{{ item.id }}/decrease" style="display: inline;">
                            <button type="submit">-</button>
                        </form>
                        <span>{{ item.quantity }}</span>
                        <form method="POST" action="/update-cart/{{ item.id }}/increase" style="display: inline;">
                            <button type="submit">+</button>
                        </form>
                    </div>
                    <div style="min-width: 100px; text-align: right;">
                        <strong>${{ "%.2f"|format(item.price * item.quantity) }}</strong>
                    </div>
                    <form method="POST" action="/remove-from-cart/{{ item.id }}" style="display: inline;">
                        <button type="submit" class="remove-btn">Remove</button>
                    </form>
                </div>
            </div>
            {% endfor %}
            
            <div class="cart-summary">
                <div class="summary-row">
                    <span>Subtotal:</span>
                    <span>${{ "%.2f"|format(total) }}</span>
                </div>
                <div class="summary-row">
                    <span>Shipping:</span>
                    <span>$10.00</span>
                </div>
                <div class="summary-row total">
                    <span>Total:</span>
                    <span>${{ "%.2f"|format(total + 10) }}</span>
                </div>
                <form method="POST" action="/checkout">
                    <button type="submit" class="checkout-btn">Proceed to Checkout</button>
                </form>
            </div>
        {% else %}
            <div class="empty-cart">
                <p>Your cart is empty</p>
                <a href="/" class="continue-shopping">Continue Shopping</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

CHECKOUT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>TechStore - Order Complete</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        h1 { font-size: 1.8rem; }
        nav a { color: white; text-decoration: none; margin-left: 2rem; }
        .container { max-width: 800px; margin: 2rem auto; padding: 0 2rem; }
        .success-message { background: white; padding: 3rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .success-icon { font-size: 4rem; color: #27ae60; margin-bottom: 1rem; }
        h2 { color: #2c3e50; margin-bottom: 1rem; }
        .order-number { color: #7f8c8d; margin-bottom: 2rem; }
        .continue-btn { background: #3498db; color: white; text-decoration: none; padding: 1rem 2rem; border-radius: 4px; display: inline-block; margin-top: 1rem; }
        .continue-btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>🛒 TechStore</h1>
            <nav>
                <a href="/">Products</a>
            </nav>
        </div>
    </header>
    <div class="container">
        <div class="success-message">
            <div class="success-icon">✓</div>
            <h2>Order Placed Successfully!</h2>
            <p class="order-number">Order #{{ order_number }}</p>
            <p>Thank you for your purchase. We'll send you a confirmation email shortly.</p>
            <p style="margin-top: 1rem; color: #7f8c8d;">Total: ${{ "%.2f"|format(total) }}</p>
            <a href="/" class="continue-btn">Continue Shopping</a>
        </div>
    </div>
</body>
</html>
'''

# Helper functions
def get_product_by_id(product_id):
    return next((p for p in PRODUCTS if p['id'] == product_id), None)

def get_cart():
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']

def get_cart_count():
    cart = get_cart()
    return sum(cart.values())

def get_cart_items():
    cart = get_cart()
    items = []
    for product_id, quantity in cart.items():
        product = get_product_by_id(int(product_id))
        if product:
            items.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity
            })
    return items

def get_cart_total():
    items = get_cart_items()
    return sum(item['price'] * item['quantity'] for item in items)

# Routes
@app.route('/')
def home():
    cart_count = get_cart_count()
    return render_template_string(HOME_TEMPLATE, products=PRODUCTS, cart_count=cart_count)

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found')
        return redirect(url_for('home'))
    
    if product['stock'] == 0:
        flash('Product is out of stock')
        return redirect(url_for('home'))
    
    cart = get_cart()
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
    
    session['cart'] = cart
    flash(f'{product["name"]} added to cart!')
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    items = get_cart_items()
    total = get_cart_total()
    return render_template_string(CART_TEMPLATE, cart_items=items, total=total)

@app.route('/update-cart/<int:product_id>/<action>', methods=['POST'])
def update_cart(product_id, action):
    cart = get_cart()
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        if action == 'increase':
            cart[product_id_str] += 1
        elif action == 'decrease':
            cart[product_id_str] -= 1
            if cart[product_id_str] <= 0:
                del cart[product_id_str]
    
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = get_cart()
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
    
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    total = get_cart_total() + 10  # Add shipping
    order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Clear cart after checkout
    session['cart'] = {}
    
    return render_template_string(CHECKOUT_TEMPLATE, order_number=order_number, total=total)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
