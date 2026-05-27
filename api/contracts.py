from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_db
from api.auth import get_current_company

router = APIRouter()


class ContractIn(BaseModel):
    project_id: Optional[int] = None
    title: str
    file_url: Optional[str] = None
    contract_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = "active"


# ── Contracts CRUD ───────────────────────────────────────────────────────────

@router.get("/")
async def list_contracts(company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT c.*, p.name as project_name
           FROM contracts c
           LEFT JOIN projects p ON p.id = c.project_id
           WHERE c.company_id=$1
           ORDER BY c.created_at DESC""",
        company["id"]
    )
    return [dict(r) for r in rows]


@router.get("/{contract_id}")
async def get_contract(contract_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """SELECT c.*, p.name as project_name
           FROM contracts c
           LEFT JOIN projects p ON p.id = c.project_id
           WHERE c.id=$1 AND c.company_id=$2""",
        contract_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Contract not found")
    return dict(row)


@router.post("/")
async def create_contract(body: ContractIn, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """INSERT INTO contracts (company_id, project_id, title, file_url, contract_type,
           start_date, end_date, status)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8) RETURNING *""",
        company["id"], body.project_id, body.title, body.file_url, body.contract_type,
        body.start_date, body.end_date, body.status
    )
    return dict(row)


@router.put("/{contract_id}")
async def update_contract(contract_id: int, body: ContractIn,
                          company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """UPDATE contracts SET project_id=$1, title=$2, file_url=$3, contract_type=$4,
           start_date=$5, end_date=$6, status=$7
           WHERE id=$8 AND company_id=$9 RETURNING *""",
        body.project_id, body.title, body.file_url, body.contract_type,
        body.start_date, body.end_date, body.status, contract_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Contract not found")
    return dict(row)


@router.delete("/{contract_id}")
async def delete_contract(contract_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    await db.execute(
        "DELETE FROM contracts WHERE id=$1 AND company_id=$2", contract_id, company["id"]
    )
    return {"ok": True}


@router.patch("/{contract_id}/status")
async def update_contract_status(contract_id: int, status: str,
                                 company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """UPDATE contracts SET status=$1
           WHERE id=$2 AND company_id=$3 RETURNING *""",
        status, contract_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Contract not found")
    return dict(row)
