import os
import time
import mimetypes
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Optional
from database import get_db
from routers.auth import get_current_company

try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_ENABLED = bool(
        os.getenv('CLOUDINARY_CLOUD_NAME') and
        os.getenv('CLOUDINARY_API_KEY') and
        os.getenv('CLOUDINARY_API_SECRET')
    )
    if CLOUDINARY_ENABLED:
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
            secure=True,
        )
except ImportError:
    CLOUDINARY_ENABLED = False

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large. Max 10MB.")
    timestamp = int(time.time())
    safe_filename = file.filename.replace(" ", "_")

    if CLOUDINARY_ENABLED:
        public_id = f"buildtrack/{company['id']}/{timestamp}_{os.path.splitext(safe_filename)[0]}"
        upload_result = cloudinary.uploader.upload(
            contents,
            public_id=public_id,
            resource_type='auto',
            use_filename=False,
            unique_filename=False,
            overwrite=False,
        )
        file_url = upload_result.get('secure_url')
        storage_key = upload_result.get('public_id')
    else:
        unique_filename = f"{company['id']}_{timestamp}_{safe_filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        # Construct URL for streaming endpoint; use API path for Vercel compatibility
        file_url = f"/api/uploads/file/{unique_filename}"
        storage_key = unique_filename

    row = await db.fetchrow(
        """INSERT INTO uploads (company_id, project_id, file_name, file_url, file_type, storage_key)
           VALUES ($1,$2,$3,$4,$5,$6) RETURNING *""",
        company["id"], project_id, file.filename, file_url, file.content_type, storage_key
    )
    return dict(row)

@router.get("/file/{filename}")
async def serve_uploaded_file(filename: str, background_tasks: BackgroundTasks):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found on disk")
    content_type, _ = mimetypes.guess_type(file_path)
    media_type = content_type or 'application/octet-stream'
    file_handle = open(file_path, 'rb')
    background_tasks.add_task(file_handle.close)
    return StreamingResponse(file_handle, media_type=media_type)

@router.get("/")
async def list_uploads(project_id: Optional[int] = None,
                       company=Depends(get_current_company), db=Depends(get_db)):
    if project_id:
        rows = await db.fetch(
            "SELECT * FROM uploads WHERE company_id=$1 AND project_id=$2 ORDER BY uploaded_at DESC",
            company["id"], project_id
        )
    else:
        rows = await db.fetch(
            "SELECT * FROM uploads WHERE company_id=$1 ORDER BY uploaded_at DESC", company["id"]
        )
    return [dict(r) for r in rows]

@router.delete("/{upload_id}")
async def delete_upload(upload_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        "SELECT file_url, storage_key FROM uploads WHERE id=$1 AND company_id=$2", upload_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "File not found")
    storage_key = row["storage_key"]
    await db.execute("DELETE FROM uploads WHERE id=$1 AND company_id=$2", upload_id, company["id"])

    if CLOUDINARY_ENABLED and storage_key:
        try:
            cloudinary.uploader.destroy(storage_key, resource_type='auto')
        except Exception:
            pass
    else:
        file_name = os.path.basename(storage_key or '')
        file_path = os.path.join(UPLOAD_DIR, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    return {"ok": True}
