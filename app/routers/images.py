from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Response, Depends
from app.database.database import get_db_connection
from app.config.config import config
from app.auth import get_current_user, get_admin_user
import os
import aiofiles
from typing import Optional

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/")
async def create_image(name: str = Form(...), description: Optional[str] = Form(None), file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO images (name, description, status, file_path) VALUES (%s, %s, %s, %s) RETURNING id", (name, description, 1, ""))
    new_image = cursor.fetchone()
    file_extension = os.path.splitext(file.filename)[1]
    file_location = f"{config.UPLOAD_DIR}/image_{new_image['id']}{file_extension}"
    async with aiofiles.open(file_location, 'wb') as buffer:
        content = await file.read()
        await buffer.write(content)
    cursor.execute("UPDATE images SET file_path = %s WHERE id = %s", (file_location, new_image['id']))
    cursor.execute("SELECT * FROM images WHERE id = %s", (new_image['id'],))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result

@router.get("/")
async def read_images(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images")
    images = cursor.fetchall()
    conn.close()
    return images

@router.get("/{image_id}")
async def read_image(image_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images WHERE id = %s", (image_id,))
    image = cursor.fetchone()
    conn.close()
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.get("/file/{image_id}")
async def get_image_file(image_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM images WHERE id = %s", (image_id,))
    image = cursor.fetchone()
    conn.close()
    if image is None or not os.path.exists(image['file_path']):
        raise HTTPException(status_code=404, detail="Image not found")
    async with aiofiles.open(image['file_path'], 'rb') as f:
        content = await f.read()
    return Response(content=content, media_type="image/jpeg")

@router.put("/{image_id}", dependencies=[Depends(get_admin_user)])
async def update_image(image_id: int, name: str = Form(...), description: Optional[str] = Form(None), status: int = Form(...), file: Optional[UploadFile] = File(None)):
    if status not in [0, 1]:
        raise HTTPException(status_code=400, detail="Status must be 0 or 1")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM images WHERE id = %s", (image_id,))
    old_image = cursor.fetchone()
    if old_image is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Image not found")
    file_location = old_image['file_path']
    if file:
        file_extension = os.path.splitext(file.filename)[1]
        file_location = f"{config.UPLOAD_DIR}/image_{image_id}{file_extension}"
        async with aiofiles.open(file_location, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)
        if os.path.exists(old_image['file_path']) and old_image['file_path'] != file_location:
            os.remove(old_image['file_path'])
    cursor.execute("UPDATE images SET name = %s, description = %s, status = %s, file_path = %s WHERE id = %s RETURNING *", (name, description, status, file_location, image_id))
    updated_image = cursor.fetchone()
    conn.commit()
    conn.close()
    return updated_image

@router.delete("/{image_id}", dependencies=[Depends(get_admin_user)])
async def delete_image(image_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM images WHERE id = %s", (image_id,))
    image = cursor.fetchone()
    if image is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Image not found")
    if os.path.exists(image['file_path']):
        os.remove(image['file_path'])
    cursor.execute("DELETE FROM images WHERE id = %s", (image_id,))
    conn.commit()
    conn.close()
    return {"message": "Image deleted"}

@router.get("/enable/{image_id}", dependencies=[Depends(get_admin_user)])
async def enable_image(image_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE images SET status = 1 WHERE id = %s RETURNING *", (image_id,))
    updated_image = cursor.fetchone()
    conn.commit()
    conn.close()
    if updated_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return updated_image

@router.get("/disable/{image_id}", dependencies=[Depends(get_admin_user)])
async def disable_image(image_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE images SET status = 0 WHERE id = %s RETURNING *", (image_id,))
    updated_image = cursor.fetchone()
    conn.commit()
    conn.close()
    if updated_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return updated_image
