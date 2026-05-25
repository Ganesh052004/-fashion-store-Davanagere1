# LUXE Fashion Store — Setup Guide

## Project Structure

```
luxe_project/
├── backend/
│   ├── app.py              ← Flask API server
│   ├── create_admin.py     ← Run once to create admin user
│   └── requirements.txt    ← Python dependencies
├── frontend/
│   ├── login.html
│   ├── user.html
│   └── admin.html
└── luxe_db.sql             ← Database schema + sample data
```

---

## Step 1 — Install XAMPP

Download and install XAMPP from https://www.apachefriends.org  
Start **Apache** and **MySQL** from the XAMPP Control Panel.

---

## Step 2 — Import the Database

**Option A — phpMyAdmin (easiest):**
1. Open http://localhost/phpmyadmin in your browser
2. Click **Import** → **Choose File** → select `luxe_db.sql` → click **Go**

**Option B — Terminal:**
```bash
mysql -u root < luxe_db.sql
```

---

## Step 3 — Install Python Dependencies

Open a terminal in the `backend/` folder:

```bash
pip install -r requirements.txt
```

> On some systems use `pip3` instead of `pip`.

---

## Step 4 — Create the Admin User

Still inside the `backend/` folder:

```bash
python create_admin.py
```

This creates the admin account:
- **Email:** admin@luxe.com  
- **Password:** admin123

---

## Step 5 — Run the Flask Server

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

---

## Step 6 — Open the App

Open your browser and go to: **http://127.0.0.1:5000**

| Account | Email | Password |
|---------|-------|----------|
| Admin   | admin@luxe.com | admin123 |
| User    | Register a new account | — |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `pymysql.err.OperationalError` | Make sure XAMPP MySQL is running |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| Admin login fails | Run `python create_admin.py` again to reset password |
| Port 5000 in use | Change `port=5000` to `port=5001` in `app.py` and update the `API` variable in all HTML files |

---

## API Endpoints Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/register | — | Register new user |
| POST | /api/login | — | Login |
| GET | /api/products | — | List all products |
| GET | /api/cart | User | View cart |
| POST | /api/cart | User | Add item to cart |
| DELETE | /api/cart/:id | User | Remove from cart |
| POST | /api/cart/checkout | User | Place order |
| GET | /api/admin/stats | Admin | Dashboard stats |
| GET | /api/admin/orders | Admin | All orders |
| PUT | /api/admin/orders/:id | Admin | Update order status |
| GET | /api/admin/users | Admin | All users |
| POST | /api/products | Admin | Add product |
| PUT | /api/products/:id | Admin | Edit product |
| DELETE | /api/products/:id | Admin | Delete product |
