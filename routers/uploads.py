import os
import time
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Optional
from database import get_db
from routers.auth import get_current_company

router = APIRouter()

UPLOAD_DIR = "/tmp/uploads"
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
    unique_filename = f"{company['id']}_{timestamp}_{safe_filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    file_url = f"/uploads/{unique_filename}"
    row = await db.fetchrow(
        """INSERT INTO uploads (company_id, project_id, file_name, file_url, file_type)
           VALUES ($1,$2,$3,$4,$5) RETURNING *""",
        company["id"], project_id, file.filename, file_url, file.content_type
    )
    return dict(row)

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
        "SELECT file_url FROM uploads WHERE id=$1 AND company_id=$2", upload_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "File not found")
    await db.execute("DELETE FROM uploads WHERE id=$1 AND company_id=$2", upload_id, company["id"])
    return {"ok": True}