import sqlite3
import json
import hashlib
import os

def get_app_dir():
    try:
        from android.storage import app_storage_path
        return app_storage_path()
    except ImportError:
        return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()
DATABASE = os.path.join(APP_DIR, 'radatlas.db')
USER_DB = os.path.join(APP_DIR, 'users.db')


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def init_user_db():
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  role TEXT NOT NULL DEFAULT 'user',
                  database TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role, database) VALUES (?, ?, ?, ?)",
                  ('admin', hash_password('admin123'), 'admin', DATABASE))
    conn.commit()
    conn.close()


def authenticate_user(username, password):
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT id, username, role, database FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'username': row[1], 'role': row[2], 'database': row[3]}
    return None


def get_all_users():
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT id, username, role, database, created_at FROM users ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows


def create_user(username, password, role='user', database=None):
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    try:
        if database is None:
            db_name = os.path.join(APP_DIR, f"user_{username}.db")
            database = db_name
        c.execute("INSERT INTO users (username, password, role, database) VALUES (?, ?, ?, ?)",
                  (username, hash_password(password), role, database))
        conn.commit()
        conn.close()
        return True, database
    except sqlite3.IntegrityError:
        conn.close()
        return False, None


def delete_user(user_id):
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT database FROM users WHERE id=? AND role!='admin'", (user_id,))
    row = c.fetchone()
    if row and row[0] and os.path.exists(row[0]):
        os.remove(row[0])
    c.execute("DELETE FROM users WHERE id=? AND role!='admin'", (user_id,))
    conn.commit()
    conn.close()


def change_password(user_id, old_password, new_password):
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE id=? AND password=?", (user_id, hash_password(old_password)))
    if c.fetchone():
        c.execute("UPDATE users SET password=? WHERE id=?", (hash_password(new_password), user_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


def init_db(db_path=None):
    if db_path is None:
        db_path = DATABASE
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS diseases
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name_cn TEXT, name_en TEXT, system TEXT, category TEXT,
                  clinical TEXT, diagnosis TEXT,
                  primary_img TEXT, secondary_img TEXT,
                  xray_finding TEXT, ct_finding TEXT, mri_finding TEXT, pet_finding TEXT,
                  report_template TEXT, differential_diagnosis TEXT, treatment TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS images
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  disease_id INTEGER, filename TEXT, image_type TEXT,
                  caption TEXT, source TEXT, media_type TEXT, annotations TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS medical_records
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  disease_id INTEGER, title TEXT, content TEXT,
                  image_filename TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS anatomy_records
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT, content TEXT,
                  image_filename TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    try:
        c.execute("ALTER TABLE images ADD COLUMN media_type TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE images ADD COLUMN annotations TEXT")
    except sqlite3.OperationalError:
        pass
    c.execute("UPDATE images SET media_type = 'image' WHERE media_type IS NULL")
    conn.commit()
    conn.close()


def load_data(db_path=None):
    if db_path is None:
        db_path = DATABASE
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM diseases')
    if c.fetchone()[0] == 0:
        data_json = os.path.join(APP_DIR, 'data.json')
        if os.path.exists(data_json):
            with open(data_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for system, diseases in data.items():
                for d in diseases:
                    c.execute('''INSERT INTO diseases
                    (name_cn, name_en, system, category, clinical, diagnosis,
                     primary_img, secondary_img, xray_finding, ct_finding, mri_finding, pet_finding,
                     report_template, differential_diagnosis, treatment)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (d['name_cn'], d['name_en'], system, d.get('category',''),
                     d.get('clinical',''), d.get('diagnosis',''),
                     d.get('primary_img',''), d.get('secondary_img',''),
                     d.get('xray',''), d.get('ct',''), d.get('mri',''), d.get('pet',''),
                     d.get('report',''), d.get('diff',''), d.get('treatment','')))
            conn.commit()
    conn.close()


def copy_public_to_user(user_db):
    if not os.path.exists(user_db):
        import shutil
        shutil.copy2(DATABASE, user_db)
