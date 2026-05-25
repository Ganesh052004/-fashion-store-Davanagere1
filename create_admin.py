"""
Run this ONCE to create or reset the admin user.
Usage:  python create_admin.py
Login:  admin@luxe.com / admin123
"""
from flask_bcrypt import Bcrypt
import pymysql

bcrypt = Bcrypt()
pw_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')

DB = dict(
    host='localhost',
    user='root',
    password='',
    db='luxe_store',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

conn = pymysql.connect(**DB)
with conn.cursor() as cur:
    cur.execute("SELECT id FROM users WHERE email='admin@luxe.com'")
    existing = cur.fetchone()
    if existing:
        cur.execute("UPDATE users SET password=%s WHERE email='admin@luxe.com'", (pw_hash,))
        print("✅  Admin password reset.")
    else:
        cur.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s,%s,%s,%s)",
            ('Admin', 'admin@luxe.com', pw_hash, 'admin')
        )
        print("✅  Admin user created.")
    conn.commit()
conn.close()
print("Done!  Login → admin@luxe.com / admin123")
