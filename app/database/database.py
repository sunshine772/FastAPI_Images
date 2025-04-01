import psycopg2
from psycopg2.extras import RealDictCursor
from app.config.config import config
import time
import secrets
import hashlib

def generate_api_key():
    random_string = secrets.token_hex(16) + str(time.time())
    return hashlib.sha256(random_string.encode('utf-8')).hexdigest()

def get_db_connection(max_retries=3, delay=2):
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception:
            retries += 1
            if retries == max_retries:
                raise Exception("Failed to connect to DB")
            time.sleep(delay)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(255) UNIQUE NOT NULL, hashed_password VARCHAR(255) NOT NULL, role VARCHAR(50) NOT NULL DEFAULT 'user', api_key VARCHAR(255) NOT NULL)")
    from app.auth import get_password_hash
    admin_hashed_password = get_password_hash("admin")
    user_hashed_password = get_password_hash("user")
    admin_api_key = generate_api_key()
    user_api_key = generate_api_key()
    cursor.execute("INSERT INTO users (username, hashed_password, role, api_key) VALUES (%s, %s, %s, %s)", ("admin", admin_hashed_password, "admin", admin_api_key))
    cursor.execute("INSERT INTO users (username, hashed_password, role, api_key) VALUES (%s, %s, %s, %s)", ("user", user_hashed_password, "user", user_api_key))
    cursor.execute("DROP TABLE IF EXISTS images")
    cursor.execute("CREATE TABLE images (id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, description TEXT, status SMALLINT DEFAULT 1 CHECK (status IN (0,1)), file_path VARCHAR(255) NOT NULL)")
    conn.commit()
    conn.close()
