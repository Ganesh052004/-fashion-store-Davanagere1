from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import pymysql
import jwt
import datetime
import os

# ── PATHS ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = BASE_DIR  # Assuming HTML files are in the same directory as app.py

app = Flask(__name__, static_folder=None)
CORS(app, origins="*")
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = 'luxe_secret_key_2026'

# ── DB CONFIG (XAMPP defaults) ───────────────────────────────────────────────
DB = dict(
    host='localhost',
    user='root',
    password='',
    db='luxe_store',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

def get_db():
    return pymysql.connect(**DB)

def decode_token(token):
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except Exception:
        return None

def auth_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        data = decode_token(token)
        if not data:
            return jsonify({'error': 'Unauthorized'}), 401
        request.user = data
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        data = decode_token(token)
        if not data or data.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        request.user = data
        return f(*args, **kwargs)
    return decorated

# ── SERVE FRONTEND ───────────────────────────────────────────────────────────

@app.route('/')
def home():
    return send_from_directory(FRONTEND_DIR, 'login.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    # Only serve known HTML files, block everything else
    allowed = {'login.html', 'user.html', 'admin.html'}
    if filename in allowed:
        return send_from_directory(FRONTEND_DIR, filename)
    return jsonify({'error': 'Not found'}), 404

# ── AUTH ─────────────────────────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    d = request.json or {}
    name = d.get('name', '').strip()
    email = d.get('email', '').strip().lower()
    password = d.get('password', '')
    if not all([name, email, password]):
        return jsonify({'error': 'All fields required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed)
            )
            conn.commit()
            user_id = cur.lastrowid
        conn.close()
        token = jwt.encode(
            {'id': user_id, 'email': email, 'role': 'user',
             'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
            app.config['SECRET_KEY'], algorithm='HS256'
        )
        return jsonify({'token': token, 'role': 'user', 'name': name})
    except pymysql.err.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 409
    except Exception as e:
        return jsonify({'error': 'Database error: ' + str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    d = request.json or {}
    email = d.get('email', '').strip().lower()
    password = d.get('password', '')
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
        conn.close()
    except Exception as e:
        return jsonify({'error': 'Database error: ' + str(e)}), 500
    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401
    token = jwt.encode(
        {'id': user['id'], 'email': email, 'role': user['role'],
         'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
        app.config['SECRET_KEY'], algorithm='HS256'
    )
    return jsonify({'token': token, 'role': user['role'], 'name': user['name']})

# ── PRODUCTS ─────────────────────────────────────────────────────────────────

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM products ORDER BY id")
            products = cur.fetchall()
        conn.close()
        # Ensure price fields are serialisable
        for p in products:
            p['price'] = float(p['price'])
            p['old_price'] = float(p['old_price']) if p.get('old_price') else None
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
@admin_required
def add_product():
    d = request.json or {}
    required = ['name', 'category', 'price']
    if not all(d.get(k) for k in required):
        return jsonify({'error': 'name, category, price are required'}), 400
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO products (name, category, price, old_price, emoji, badge, stock)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (d['name'], d['category'], d['price'], d.get('old_price') or None,
                 d.get('emoji', '👕'), d.get('badge', ''), int(d.get('stock', 100)))
            )
            conn.commit()
            pid = cur.lastrowid
        conn.close()
        return jsonify({'id': pid, 'message': 'Product added'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:pid>', methods=['PUT'])
@admin_required
def update_product(pid):
    d = request.json or {}
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE products SET name=%s, category=%s, price=%s, old_price=%s,
                   emoji=%s, badge=%s, stock=%s WHERE id=%s""",
                (d['name'], d['category'], d['price'], d.get('old_price') or None,
                 d.get('emoji', '👕'), d.get('badge', ''), int(d.get('stock', 100)), pid)
            )
            conn.commit()
        conn.close()
        return jsonify({'message': 'Product updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:pid>', methods=['DELETE'])
@admin_required
def delete_product(pid):
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM products WHERE id=%s", (pid,))
            conn.commit()
        conn.close()
        return jsonify({'message': 'Product deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── CART ─────────────────────────────────────────────────────────────────────

@app.route('/api/cart', methods=['GET'])
@auth_required
def get_cart():
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """SELECT c.id, c.quantity, p.id as product_id,
                          p.name, p.price, p.emoji, p.category
                   FROM cart c JOIN products p ON c.product_id=p.id
                   WHERE c.user_id=%s""",
                (request.user['id'],)
            )
            items = cur.fetchall()
        conn.close()
        for item in items:
            item['price'] = float(item['price'])
        return jsonify(items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart', methods=['POST'])
@auth_required
def add_to_cart():
    d = request.json or {}
    product_id = d.get('product_id')
    if not product_id:
        return jsonify({'error': 'product_id required'}), 400
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO cart (user_id, product_id, quantity)
                   VALUES (%s, %s, 1)
                   ON DUPLICATE KEY UPDATE quantity = quantity + 1""",
                (request.user['id'], product_id)
            )
            conn.commit()
        conn.close()
        return jsonify({'message': 'Added to cart'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/<int:product_id>', methods=['DELETE'])
@auth_required
def remove_from_cart(product_id):
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM cart WHERE user_id=%s AND product_id=%s",
                (request.user['id'], product_id)
            )
            conn.commit()
        conn.close()
        return jsonify({'message': 'Removed from cart'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/checkout', methods=['POST'])
@auth_required
def checkout():
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """SELECT c.quantity, p.price FROM cart c
                   JOIN products p ON c.product_id=p.id WHERE c.user_id=%s""",
                (request.user['id'],)
            )
            items = cur.fetchall()
            if not items:
                conn.close()
                return jsonify({'error': 'Cart is empty'}), 400
            total = sum(float(i['price']) * i['quantity'] for i in items)
            cur.execute(
                "INSERT INTO orders (user_id, total) VALUES (%s, %s)",
                (request.user['id'], total)
            )
            order_id = cur.lastrowid
            cur.execute(
                """INSERT INTO order_items (order_id, product_id, quantity, price)
                   SELECT %s, c.product_id, c.quantity, p.price
                   FROM cart c JOIN products p ON c.product_id=p.id
                   WHERE c.user_id=%s""",
                (order_id, request.user['id'])
            )
            cur.execute("DELETE FROM cart WHERE user_id=%s", (request.user['id'],))
            conn.commit()
        conn.close()
        return jsonify({'message': 'Order placed!', 'order_id': order_id, 'total': total})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── ADMIN ─────────────────────────────────────────────────────────────────────

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM users WHERE role='user'")
            users = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) as total FROM orders")
            orders = cur.fetchone()['total']
            cur.execute("SELECT COALESCE(SUM(total),0) as revenue FROM orders WHERE status!='cancelled'")
            revenue = float(cur.fetchone()['revenue'])
            cur.execute("SELECT COUNT(*) as total FROM products")
            products = cur.fetchone()['total']
        conn.close()
        return jsonify({'users': users, 'orders': orders, 'revenue': revenue, 'products': products})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/orders', methods=['GET'])
@admin_required
def admin_orders():
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """SELECT o.id, o.total, o.status, o.created_at,
                          u.name as user_name, u.email
                   FROM orders o JOIN users u ON o.user_id=u.id
                   ORDER BY o.created_at DESC"""
            )
            orders = cur.fetchall()
        conn.close()
        for o in orders:
            o['total'] = float(o['total'])
            if hasattr(o['created_at'], 'isoformat'):
                o['created_at'] = o['created_at'].isoformat()
        return jsonify(orders)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/orders/<int:oid>', methods=['PUT'])
@admin_required
def update_order_status(oid):
    status = (request.json or {}).get('status')
    valid = {'pending', 'processing', 'shipped', 'delivered', 'cancelled'}
    if status not in valid:
        return jsonify({'error': 'Invalid status'}), 400
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("UPDATE orders SET status=%s WHERE id=%s", (status, oid))
            conn.commit()
        conn.close()
        return jsonify({'message': 'Status updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_users():
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC"
            )
            users = cur.fetchall()
        conn.close()
        for u in users:
            if hasattr(u['created_at'], 'isoformat'):
                u['created_at'] = u['created_at'].isoformat()
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
