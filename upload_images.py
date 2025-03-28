import aiohttp
import asyncio
import os
import aiofiles
import re
import argparse
from app.config.config import config

async def upload_image(session, file_path, url):
    filename = os.path.basename(file_path)
    data = aiohttp.FormData()
    data.add_field('nombre', filename)
    async with aiofiles.open(file_path, 'rb') as f:
        data.add_field('file', await f.read(), filename=filename, content_type='image/jpeg')
    async with session.post(url, data=data) as response:
        if response.status == 200:
            print(f"Subida exitosa: {filename}")
        else:
            print(f"Error subiendo {filename}: {response.status} - {await response.text()}")

async def upload_all_images(url, source_dir):
    if not os.path.exists(source_dir):
        print(f"Error: La carpeta '{source_dir}' no existe.")
        return
    files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    files.sort(key=lambda x: int(re.search(r'(\d+)', x).group(0)) if re.search(r'(\d+)', x) else float('inf'))
    async with aiohttp.ClientSession() as session:
        for filename in files:
            await upload_image(session, os.path.join(source_dir, filename), url)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Subir imágenes a un servidor.")
    parser.add_argument('-u', '--url', type=str, default=f'http://127.0.0.1:{config.APP_PORT}/images/',
                        help="URL del servidor donde se subirán las imágenes (default: localhost del config)")
    parser.add_argument('-p', '--path', type=str, default=config.SOURCE_IMAGES_DIR,
                        help="Ruta de la carpeta con las imágenes (default: SOURCE_IMAGES_DIR del config)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(upload_all_images(args.url, args.path))