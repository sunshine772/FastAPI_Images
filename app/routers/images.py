from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Response
from app.database.database import get_db_connection
from app.config.config import config
import os
import aiofiles
from typing import Optional

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/")
async def create_image(nombre: str = Form(...), descripcion: Optional[str] = Form(None), file: UploadFile = File(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO imagenes (nombre, descripcion, estado, foto) VALUES (%s, %s, %s, %s) RETURNING id", (nombre, descripcion, 1, ""))
    new_image = cursor.fetchone()
    file_extension = os.path.splitext(file.filename)[1]
    file_location = f"{config.UPLOAD_DIR}/imagen_{new_image['id']}{file_extension}"
    async with aiofiles.open(file_location, 'wb') as buffer:
        content = await file.read()
        await buffer.write(content)
    cursor.execute("UPDATE imagenes SET foto = %s WHERE id = %s", (file_location, new_image['id']))
    cursor.execute("SELECT * FROM imagenes WHERE id = %s", (new_image['id'],))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    print(f"Imagen subida: {result['nombre']} - Ruta: {result['foto']}")
    return result

@router.get("/")
async def read_images():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM imagenes")
    images = cursor.fetchall()
    conn.close()
    return images

@router.get("/{image_id}")
async def read_image(image_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM imagenes WHERE id = %s", (image_id,))
    image = cursor.fetchone()
    conn.close()
    if image is None:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return image

@router.get("/foto/{image_id}")
async def get_image_file(image_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT foto FROM imagenes WHERE id = %s", (image_id,))
    image = cursor.fetchone()
    conn.close()
    if image is None or not os.path.exists(image['foto']):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    async with aiofiles.open(image['foto'], 'rb') as f:
        content = await f.read()
    return Response(content=content, media_type="image/jpeg")

@router.put("/{image_id}")
async def update_image(image_id: int, nombre: str = Form(...), descripcion: Optional[str] = Form(None), estado: int = Form(...), file: Optional[UploadFile] = File(None)):
    if estado not in [0, 1]:
        raise HTTPException(status_code=400, detail="El estado debe ser 0 o 1")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT foto FROM imagenes WHERE id = %s", (image_id,))
    old_image = cursor.fetchone()
    if old_image is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    file_location = old_image['foto']
    if file:
        file_extension = os.path.splitext(file.filename)[1]
        file_location = f"{config.UPLOAD_DIR}/imagen_{image_id}{file_extension}"
        async with aiofiles.open(file_location, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)
        if os.path.exists(old_image['foto']) and old_image['foto'] != file_location:
            os.remove(old_image['foto'])
    cursor.execute("UPDATE imagenes SET nombre = %s, descripcion = %s, estado = %s, foto = %s WHERE id = %s RETURNING *", (nombre, descripcion, estado, file_location, image_id))
    updated_image = cursor.fetchone()
    conn.commit()
    conn.close()
    return updated_image

@router.delete("/{image_id}")
async def delete_image(image_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT foto FROM imagenes WHERE id = %s", (image_id,))
    image = cursor.fetchone()
    if image is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    if os.path.exists(image['foto']):
        os.remove(image['foto'])
    cursor.execute("DELETE FROM imagenes WHERE id = %s", (image_id,))
    conn.commit()
    conn.close()
    return {"message": "Imagen eliminada"}

@router.get("/habilitar/{image_id}")
async def enable_image(image_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE imagenes SET estado = 1 WHERE id = %s RETURNING *", (image_id,))
    updated_image = cursor.fetchone()
    conn.commit()
    conn.close()
    if updated_image is None:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return updated_image

@router.get("/deshabilitar/{image_id}")
async def disable_image(image_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE imagenes SET estado = 0 WHERE id = %s RETURNING *", (image_id,))
    updated_image = cursor.fetchone()
    conn.commit()
    conn.close()
    if updated_image is None:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return updated_image
