from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_db
from api.auth import get_current_company

router = APIRouter()


class DailyLogIn(BaseModel):
    project_id: Optional[int] = None
    log_date: Optional[date] = None
    weather: Optional[str] = None
    activities: Optional[str] = None
    issues: Optional[str] = None
    progress: Optional[int] = 0


# ── Daily Logs CRUD ─────────────────────────────────────────────────────────

@router.get("/")
async def list_daily_logs(
    project_id: Optional[int] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    query = """SELECT dl.*, p.name as project_name
              FROM daily_logs dl
              LEFT JOIN projects p ON p.id = dl.project_id
              WHERE dl.company_id=$1"""
    params = [company["id"]]
    
    if project_id:
        query += " AND dl.project_id=$2"
        params.append(project_id)
    if from_date:
        query += f" AND dl.log_date >= ${len(params) + 1}"
        params.append(from_date)
    if to_date:
        query += f" AND dl.log_date <= ${len(params) + 1}"
        params.append(to_date)
    
    query += " ORDER BY dl.log_date DESC"
    
    rows = await db.fetch(query, *params)
    return [dict(r) for r in rows]


@router.get("/{log_id}")
async def get_daily_log(log_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """SELECT dl.*, p.name as project_name
           FROM daily_logs dl
           LEFT JOIN projects p ON p.id = dl.project_id
           WHERE dl.id=$1 AND dl.company_id=$2""",
        log_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Daily log not found")
    return dict(row)


@router.post("/")
async def create_daily_log(body: DailyLogIn, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """INSERT INTO daily_logs (company_id, project_id, log_date, weather, activities,
           issues, progress)
           VALUES ($1,$2,$3,$4,$5,$6,$7) RETURNING *""",
        company["id"], body.project_id, body.log_date or date.today(),
        body.weather, body.activities, body.issues, body.progress
    )
    return dict(row)


@router.put("/{log_id}")
async def update_daily_log(log_id: int, body: DailyLogIn,
                          company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """UPDATE daily_logs SET project_id=$1, log_date=$2, weather=$3, activities=$4,
           issues=$5, progress=$6
           WHERE id=$7 AND company_id=$8 RETURNING *""",
        body.project_id, body.log_date, body.weather, body.activities,
        body.issues, body.progress, log_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Daily log not found")
    return dict(row)


@router.delete("/{log_id}")
async def delete_daily_log(log_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    await db.execute(
        "DELETE FROM daily_logs WHERE id=$1 AND company_id=$2", log_id, company["id"]
    )
    return {"ok": True}


@router.get("/by-project/{project_id}")
async def get_project_logs(project_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT * FROM daily_logs
           WHERE company_id=$1 AND project_id=$2
           ORDER BY log_date DESC""",
        company["id"], project_id
    )
    return [dict(r) for r in rows]


@router.get("/by-date/{log_date}")
async def get_log_by_date(log_date: date, company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT dl.*, p.name as project_name
           FROM daily_logs dl
           LEFT JOIN projects p ON p.id = dl.project_id
           WHERE dl.company_id=$1 AND dl.log_date=$2""",
        company["id"], log_date
    )
    return [dict(r) for r in rows]
