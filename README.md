# Configuración del Proyecto FastAPI

## 1️⃣ Clonar el repositorio
```sh
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_PROYECTO>
```

## 2️⃣ Crear y activar el entorno virtual

### En Windows (PowerShell o CMD)
```sh
python -m venv venv
.\venv\Scripts\Activate
```

### En Linux/macOS (Bash)
```sh
python3 -m venv venv
source venv/bin/activate
```

## 3️⃣ Instalar dependencias
```sh
pip install -r requirements.txt
```

## 4️⃣ Crear el archivo `.env`
Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:
```sh
DB_HOST=
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=
APP_HOST=0.0.0.0
APP_PORT=8000
UPLOAD_DIR=uploads
SOURCE_IMAGES_DIR=
```

## 5️⃣ Ejecutar la aplicación con Uvicorn

### En Windows (PowerShell o CMD)
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### En Linux/macOS (Bash)
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
## Desplegar con Docker Compose 

Construya y ejecute los contenedores en modo detached:
```sh
DB_USER=<usuario> DB_PASSWORD=<contraseña> DB_NAME=<nombre> docker-compose up --build -d
```
Esto inicia los servicios definidos.

### Subir Imágenes con el Script d
```sh
chmod +x upload_images.sh
```
### Ejecute el script con parámetros personalizados:
```sh
./upload_images.sh -u <URL_DE_LA_API> -p <RUTA_DEL_DIRECTORIO_DE_IMAGENES>
```
