from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from database import get_db
from routers.auth import get_current_company

router = APIRouter()

class WorkerIn(BaseModel):
    name: str
    role: Optional[str] = None
    project_id: Optional[int] = None

class AttendanceEntry(BaseModel):
    worker_id: int
    status: str

class AttendanceBulk(BaseModel):
    date: Optional[date] = None
    entries: List[AttendanceEntry]

@router.get("/workers")
async def list_workers(company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT w.*, p.name as project_name
           FROM workers w
           LEFT JOIN projects p ON p.id = w.project_id
           WHERE w.company_id=$1 ORDER BY w.name""",
        company["id"]
    )
    return [dict(r) for r in rows]

@router.post("/workers")
async def add_worker(body: WorkerIn, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        "INSERT INTO workers (company_id, name, role, project_id) VALUES ($1,$2,$3,$4) RETURNING *",
        company["id"], body.name, body.role, body.project_id
    )
    return dict(row)

@router.put("/workers/{worker_id}")
async def update_worker(worker_id: int, body: WorkerIn,
                        company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """UPDATE workers SET name=$1, role=$2, project_id=$3
           WHERE id=$4 AND company_id=$5 RETURNING *""",
        body.name, body.role, body.project_id, worker_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Worker not found")
    return dict(row)

@router.delete("/workers/{worker_id}")
async def delete_worker(worker_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    await db.execute(
        "DELETE FROM workers WHERE id=$1 AND company_id=$2", worker_id, company["id"]
    )
    return {"ok": True}

@router.get("/attendance")
async def get_attendance(
    att_date: Optional[date] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    if att_date:
        rows = await db.fetch(
            """SELECT a.*, w.name as worker_name, w.role
               FROM attendance a JOIN workers w ON w.id=a.worker_id
               WHERE a.company_id=$1 AND a.date=$2""",
            company["id"], att_date
        )
    elif month and year:
        rows = await db.fetch(
            """SELECT a.*, w.name as worker_name, w.role
               FROM attendance a JOIN workers w ON w.id=a.worker_id
               WHERE a.company_id=$1
                 AND EXTRACT(MONTH FROM a.date)=$2
                 AND EXTRACT(YEAR FROM a.date)=$3
               ORDER BY a.date, w.name""",
            company["id"], month, year
        )
    else:
        rows = await db.fetch(
            """SELECT a.*, w.name as worker_name, w.role
               FROM attendance a JOIN workers w ON w.id=a.worker_id
               WHERE a.company_id=$1 AND a.date=CURRENT_DATE""",
            company["id"]
        )
    return [dict(r) for r in rows]

@router.post("/attendance")
async def mark_attendance(body: AttendanceBulk,
                          company=Depends(get_current_company), db=Depends(get_db)):
    att_date = body.date or date.today()
    results = []
    for entry in body.entries:
        row = await db.fetchrow(
            """INSERT INTO attendance (worker_id, company_id, date, status)
               VALUES ($1,$2,$3,$4)
               ON CONFLICT (worker_id, date)
               DO UPDATE SET status=EXCLUDED.status
               RETURNING *""",
            entry.worker_id, company["id"], att_date, entry.status
        )
        results.append(dict(row))
    return results

@router.get("/attendance/summary")
async def attendance_summary(company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """SELECT
             COUNT(*) FILTER (WHERE status='present')  AS present_today,
             COUNT(*) FILTER (WHERE status='absent')   AS absent_today,
             COUNT(*) FILTER (WHERE status='holiday')  AS on_leave_today
           FROM attendance
           WHERE company_id=$1 AND date=CURRENT_DATE""",
        company["id"]
    )
    total = await db.fetchval("SELECT COUNT(*) FROM workers WHERE company_id=$1", company["id"])
    return {**dict(row), "total_workers": total}