from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_db
from routers.auth import get_current_company

router = APIRouter()

class ProjectIn(BaseModel):
    name: str
    client: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    contract_value: Optional[float] = 0
    budget: Optional[float] = 0
    progress: Optional[int] = 0
    status: Optional[str] = "active"

@router.get("/")
async def list_projects(company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        "SELECT * FROM projects WHERE company_id=$1 ORDER BY created_at DESC",
        company["id"]
    )
    return [dict(r) for r in rows]

@router.post("/")
async def create_project(body: ProjectIn, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """INSERT INTO projects (company_id, name, client, start_date, end_date,
           contract_value, budget, progress, status)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9) RETURNING *""",
        company["id"], body.name, body.client, body.start_date,
        body.end_date, body.contract_value, body.budget, body.progress, body.status
    )
    return dict(row)

@router.put("/{project_id}")
async def update_project(project_id: int, body: ProjectIn,
                         company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """UPDATE projects SET name=$1, client=$2, start_date=$3, end_date=$4,
           contract_value=$5, budget=$6, progress=$7, status=$8
           WHERE id=$9 AND company_id=$10 RETURNING *""",
        body.name, body.client, body.start_date, body.end_date,
        body.contract_value, body.budget, body.progress, body.status,
        project_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Project not found")
    return dict(row)

@router.delete("/{project_id}")
async def delete_project(project_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    await db.execute(
        "DELETE FROM projects WHERE id=$1 AND company_id=$2", project_id, company["id"]
    )
    return {"ok": True}