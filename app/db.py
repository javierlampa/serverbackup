import sqlite3
import datetime
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = get_db()
        # Crear tablas si no existen
        db.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, action TEXT, details TEXT, result TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        db.execute('''CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)''')
        
        # Configuración inicial
        db.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES (?, ?)", ("current_mode", "READ_ONLY"))
        
        # Usuario Admin por defecto si no existe ninguno
        from werkzeug.security import generate_password_hash
        if not db.execute("SELECT * FROM users WHERE username='admin'").fetchone():
            db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                      ("admin", generate_password_hash("admin123"), "admin"))
            db.commit()
            print(">>> Usuario 'admin' creado por defecto.")
        db.commit()

def log_audit(action, details="", result="INFO", u="SYSTEM"):
    """Registra una acción en la base de datos de auditoría."""
    try:
        # Limpieza de logs antiguos (Mantenimiento inline, aunque idealmente sería una tarea background)
        db = get_db()
        # cleanup_old_logs logic moved inline or called here
        db.execute("DELETE FROM audit_logs WHERE timestamp < datetime('now', '-10 days', 'localtime')")
        
        db.execute("INSERT INTO audit_logs (username, action, details, result, timestamp) VALUES (?,?,?,?,?)", 
                     (u, action, details, result, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
    except Exception as e:
        print(f"Error logging audit: {e}")

def get_current_mode(): 
    try: 
        row = get_db().execute("SELECT value FROM system_config WHERE key='current_mode'").fetchone()
        return row['value'] if row else "READ_ONLY"
    except: return "READ_ONLY"

def set_current_mode(m): 
    try: 
        get_db().execute("INSERT OR REPLACE INTO system_config (key, value) VALUES (?, ?)", ("current_mode", m))
        get_db().commit()
    except Exception as e:
        print(f"Error setting mode: {e}")
