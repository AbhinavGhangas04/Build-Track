from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db
from api.auth import get_current_company

router = APIRouter()


class NotificationIn(BaseModel):
    title: str
    message: Optional[str] = None
    type: str  # payment, material, labour, general
    project_id: Optional[int] = None


# ── Notifications CRUD ───────────────────────────────────────────────────────

@router.get("/")
async def list_notifications(company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT n.*, p.name as project_name
           FROM notifications n
           LEFT JOIN projects p ON p.id = n.project_id
           WHERE n.company_id=$1
           ORDER BY n.created_at DESC
           LIMIT 50""",
        company["id"]
    )
    return [dict(r) for r in rows]


@router.get("/unread")
async def list_unread_notifications(company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT n.*, p.name as project_name
           FROM notifications n
           LEFT JOIN projects p ON p.id = n.project_id
           WHERE n.company_id=$1 AND n.is_read=FALSE
           ORDER BY n.created_at DESC""",
        company["id"]
    )
    return [dict(r) for r in rows]


@router.get("/{notification_id}")
async def get_notification(notification_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """SELECT n.*, p.name as project_name
           FROM notifications n
           LEFT JOIN projects p ON p.id = n.project_id
           WHERE n.id=$1 AND n.company_id=$2""",
        notification_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Notification not found")
    return dict(row)


@router.post("/")
async def create_notification(body: NotificationIn, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """INSERT INTO notifications (company_id, title, message, type, project_id)
           VALUES ($1,$2,$3,$4,$5) RETURNING *""",
        company["id"], body.title, body.message, body.type, body.project_id
    )
    return dict(row)


@router.patch("/{notification_id}/read")
async def mark_as_read(notification_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """UPDATE notifications SET is_read=TRUE
           WHERE id=$1 AND company_id=$2 RETURNING *""",
        notification_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Notification not found")
    return dict(row)


@router.patch("/mark-all-read")
async def mark_all_as_read(company=Depends(get_current_company), db=Depends(get_db)):
    await db.execute(
        "UPDATE notifications SET is_read=TRUE WHERE company_id=$1", company["id"]
    )
    return {"ok": True}


@router.delete("/{notification_id}")
async def delete_notification(notification_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    await db.execute(
        "DELETE FROM notifications WHERE id=$1 AND company_id=$2", notification_id, company["id"]
    )
    return {"ok": True}


# ── Notification Summary ─────────────────────────────────────────────────────

@router.get("/summary/count")
async def notification_summary(company=Depends(get_current_company), db=Depends(get_db)):
    unread_count = await db.fetchval(
        "SELECT COUNT(*) FROM notifications WHERE company_id=$1 AND is_read=FALSE",
        company["id"]
    )
    return {"unread_count": unread_count}
