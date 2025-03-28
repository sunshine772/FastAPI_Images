import psycopg2
from psycopg2.extras import RealDictCursor
from app.config.config import config
import time
import traceback

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
            print(f"ConexiÃ³n exitosa a la base de datos: {config.DB_NAME} en {config.DB_HOST}")
            return conn
        except Exception as e:
            retries += 1
            print(f"Intento {retries}/{max_retries} fallido: {str(e)}")
            traceback.print_exc()
            if retries == max_retries:
                raise Exception(f"Error al conectar a la base de datos tras {max_retries} intentos: {str(e)}")
            time.sleep(delay)

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS imagenes')
        cursor.execute('CREATE TABLE imagenes (id SERIAL PRIMARY KEY, nombre VARCHAR(255) NOT NULL, descripcion TEXT, estado SMALLINT DEFAULT 1 CHECK (estado IN (0,1)), foto VARCHAR(255) NOT NULL)')
        conn.commit()
        conn.close()
        print("Tabla 'imagenes' creada en PostgreSQL.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {str(e)}")
        traceback.print_exc()
        raise
