from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_db
from api.auth import get_current_company

router = APIRouter()


class PaymentIn(BaseModel):
    project_id: Optional[int] = None
    amount: float
    payment_type: str  # advance, milestone, final
    payment_date: Optional[date] = None
    due_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[str] = "pending"


# ── Client Payments CRUD ─────────────────────────────────────────────────────

@router.get("/")
async def list_payments(company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT cp.*, p.name as project_name
           FROM client_payments cp
           LEFT JOIN projects p ON p.id = cp.project_id
           WHERE cp.company_id=$1
           ORDER BY cp.payment_date DESC, cp.created_at DESC""",
        company["id"]
    )
    return [dict(r) for r in rows]


@router.get("/{payment_id}")
async def get_payment(payment_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """SELECT cp.*, p.name as project_name
           FROM client_payments cp
           LEFT JOIN projects p ON p.id = cp.project_id
           WHERE cp.id=$1 AND cp.company_id=$2""",
        payment_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Payment not found")
    return dict(row)


@router.post("/")
async def create_payment(body: PaymentIn, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """INSERT INTO client_payments (company_id, project_id, amount, payment_type,
           payment_date, due_date, description, status)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8) RETURNING *""",
        company["id"], body.project_id, body.amount, body.payment_type,
        body.payment_date or date.today(), body.due_date, body.description, body.status
    )
    return dict(row)


@router.put("/{payment_id}")
async def update_payment(payment_id: int, body: PaymentIn,
                        company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """UPDATE client_payments SET project_id=$1, amount=$2, payment_type=$3,
           payment_date=$4, due_date=$5, description=$6, status=$7
           WHERE id=$8 AND company_id=$9 RETURNING *""",
        body.project_id, body.amount, body.payment_type, body.payment_date,
        body.due_date, body.description, body.status, payment_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Payment not found")
    return dict(row)


@router.delete("/{payment_id}")
async def delete_payment(payment_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    await db.execute(
        "DELETE FROM client_payments WHERE id=$1 AND company_id=$2", payment_id, company["id"]
    )
    return {"ok": True}


@router.patch("/{payment_id}/status")
async def update_payment_status(payment_id: int, status: str,
                                company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """UPDATE client_payments SET status=$1
           WHERE id=$2 AND company_id=$3 RETURNING *""",
        status, payment_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Payment not found")
    return dict(row)


# ── Payment Summary ───────────────────────────────────────────────────────────

@router.get("/summary/overview")
async def payment_summary(company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """SELECT
             COALESCE(SUM(amount) FILTER (WHERE status='paid'), 0) as total_received,
             COALESCE(SUM(amount) FILTER (WHERE status='pending'), 0) as pending_amount,
             COALESCE(SUM(amount) FILTER (WHERE status='overdue'), 0) as overdue_amount
           FROM client_payments
           WHERE company_id=$1""",
        company["id"]
    )
    
    # Pending payments due soon (within 7 days)
    upcoming = await db.fetch(
        """SELECT cp.*, p.name as project_name
           FROM client_payments cp
           LEFT JOIN projects p ON p.id = cp.project_id
           WHERE cp.company_id=$1
           AND cp.status='pending'
           AND cp.due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
           ORDER BY cp.due_date""",
        company["id"]
    )
    
    # Overdue payments
    overdue = await db.fetch(
        """SELECT cp.*, p.name as project_name
           FROM client_payments cp
           LEFT JOIN projects p ON p.id = cp.project_id
           WHERE cp.company_id=$1
           AND cp.status='pending'
           AND cp.due_date < CURRENT_DATE
           ORDER BY cp.due_date""",
        company["id"]
    )
    
    return {
        **dict(row),
        "upcoming_payments": [dict(r) for r in upcoming],
        "overdue_payments": [dict(r) for r in overdue]
    }


@router.get("/by-project/{project_id}")
async def get_project_payments(project_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT * FROM client_payments
           WHERE company_id=$1 AND project_id=$2
           ORDER BY payment_date DESC""",
        company["id"], project_id
    )
    return [dict(r) for r in rows]
