import aiohttp
import asyncio
import os
import aiofiles
import re
from app.config.config import config

async def wait_for_server():
    url = f'http://127.0.0.1:{config.APP_PORT}/'
    async with aiohttp.ClientSession() as session:
        for _ in range(10):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        print("Server is ready!")
                        return True
            except aiohttp.ClientConnectorError:
                print("Waiting for server...")
                await asyncio.sleep(2)
        raise Exception("Server did not start in time")

async def get_token(session, username="admin", password="admin"):
    url = f'http://127.0.0.1:{config.APP_PORT}/auth/login'
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT api_key FROM users WHERE username = %s", (username,))
    api_key = cursor.fetchone()["api_key"]
    conn.close()
    headers = {"apikey": api_key}
    data = {'username': username, 'password': password}
    async with session.post(url, data=data, headers=headers) as response:
        if response.status == 200:
            result = await response.json()
            return result['access_token'], api_key
        else:
            raise Exception(f"Failed to get token: {response.status}")

async def upload_image(session, file_path, token, api_key):
    url = f'http://127.0.0.1:{config.APP_PORT}/images/'
    filename = os.path.basename(file_path)
    data = aiohttp.FormData()
    data.add_field('name', filename)
    async with aiofiles.open(file_path, 'rb') as f:
        data.add_field('file', await f.read(), filename=filename, content_type='image/jpeg')
    headers = {"Authorization": f"Bearer {token}", "apikey": api_key}
    async with session.post(url, data=data, headers=headers) as response:
        if response.status == 200:
            print(f"Uploaded: {filename}")
        else:
            print(f"Error: {filename} ({response.status})")

async def upload_all_images():
    if not os.path.exists(config.SOURCE_IMAGES_DIR):
        print(f"Directory not found: {config.SOURCE_IMAGES_DIR}")
        return
    await wait_for_server()
    files = [f for f in os.listdir(config.SOURCE_IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    files.sort(key=lambda x: int(re.search(r'(\d+)', x).group(0)) if re.search(r'(\d+)', x) else float('inf'))
    async with aiohttp.ClientSession() as session:
        token, api_key = await get_token(session)
        for filename in files:
            await upload_image(session, os.path.join(config.SOURCE_IMAGES_DIR, filename), token, api_key)

if __name__ == "__main__":
    from app.database.database import get_db_connection
    asyncio.run(upload_all_images())
