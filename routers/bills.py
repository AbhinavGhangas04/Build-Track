from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_db
from routers.auth import get_current_company

router = APIRouter()

class BillIn(BaseModel):
    description: str
    amount: float
    bill_type: str
    status: Optional[str] = "pending"
    project_id: Optional[int] = None
    file_url: Optional[str] = None
    bill_date: Optional[date] = None
    remarks: Optional[str] = None

@router.get("/")
async def list_bills(company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT b.*, p.name as project_name
           FROM bills b
           LEFT JOIN projects p ON p.id = b.project_id
           WHERE b.company_id=$1
           ORDER BY b.bill_date DESC, b.created_at DESC""",
        company["id"]
    )
    return [dict(r) for r in rows]

@router.get("/summary")
async def summary(company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """SELECT
             COALESCE(SUM(amount) FILTER (WHERE bill_type='income'), 0)  AS total_earned,
             COALESCE(SUM(amount) FILTER (WHERE bill_type='expense'), 0) AS total_spent
           FROM bills WHERE company_id=$1""",
        company["id"]
    )
    return dict(row)

@router.post("/")
async def create_bill(body: BillIn, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """INSERT INTO bills (company_id, project_id, description, amount, bill_type,
           status, file_url, bill_date, remarks)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9) RETURNING *""",
        company["id"], body.project_id, body.description, body.amount,
        body.bill_type, body.status, body.file_url,
        body.bill_date or date.today(), body.remarks
    )
    return dict(row)

@router.put("/{bill_id}")
async def update_bill(bill_id: int, body: BillIn,
                      company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """UPDATE bills SET description=$1, amount=$2, bill_type=$3, status=$4,
           project_id=$5, file_url=$6, bill_date=$7, remarks=$8
           WHERE id=$9 AND company_id=$10 RETURNING *""",
        body.description, body.amount, body.bill_type, body.status,
        body.project_id, body.file_url, body.bill_date, body.remarks,
        bill_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Bill not found")
    return dict(row)

@router.delete("/{bill_id}")
async def delete_bill(bill_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    await db.execute(
        "DELETE FROM bills WHERE id=$1 AND company_id=$2", bill_id, company["id"]
    )
    return {"ok": True}