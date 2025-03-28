from dotenv import load_dotenv
import os

load_dotenv()  # Carga .env si existe

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_NAME = os.getenv('DB_NAME', 'dismac')
    APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.getenv('APP_PORT', '8000'))
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')
    SOURCE_IMAGES_DIR = os.getenv('SOURCE_IMAGES_DIR', 'uploads')

config = Config()

# DepuraciÃ³n
print(f"ConfiguraciÃ³n cargada: DB_HOST={config.DB_HOST}, DB_PORT={config.DB_PORT}, DB_USER={config.DB_USER}, DB_NAME={config.DB_NAME}")
