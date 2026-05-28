from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_db
from routers.auth import get_current_company

router = APIRouter()

class ReportRequest(BaseModel):
    project_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    report_type: str

@router.get("/dashboard/analytics")
async def dashboard_analytics(company=Depends(get_current_company), db=Depends(get_db)):
    financials = await db.fetchrow(
        """SELECT
             COALESCE(SUM(amount) FILTER (WHERE bill_type='income'), 0) as total_income,
             COALESCE(SUM(amount) FILTER (WHERE bill_type='expense'), 0) as total_expense
           FROM bills WHERE company_id=$1""",
        company["id"]
    )
    active_projects = await db.fetchval(
        "SELECT COUNT(*) FROM projects WHERE company_id=$1 AND status='active'", company["id"]
    )
    total_workers = await db.fetchval(
        "SELECT COUNT(*) FROM workers WHERE company_id=$1", company["id"]
    )
    pending_payments = await db.fetchval(
        "SELECT COALESCE(SUM(amount), 0) FROM client_payments WHERE company_id=$1 AND status='pending'",
        company["id"]
    )
    recent_activity = await db.fetch(
        """SELECT b.*, p.name as project_name FROM bills b
           LEFT JOIN projects p ON p.id = b.project_id
           WHERE b.company_id=$1 ORDER BY b.created_at DESC LIMIT 10""",
        company["id"]
    )
    return {
        "financials": dict(financials),
        "active_projects": active_projects,
        "total_workers": total_workers,
        "pending_payments": float(pending_payments),
        "recent_activity": [dict(r) for r in recent_activity]
    }

@router.get("/dashboard/monthly-trends")
async def monthly_trends(company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT TO_CHAR(bill_date, 'YYYY-MM') as month,
             COALESCE(SUM(amount) FILTER (WHERE bill_type='income'), 0) as income,
             COALESCE(SUM(amount) FILTER (WHERE bill_type='expense'), 0) as expense
           FROM bills WHERE company_id=$1
           AND bill_date >= CURRENT_DATE - INTERVAL '12 months'
           GROUP BY TO_CHAR(bill_date, 'YYYY-MM') ORDER BY month""",
        company["id"]
    )
    return [dict(r) for r in rows]

@router.get("/dashboard/category-breakdown")
async def category_breakdown(company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT category, COALESCE(SUM(amount), 0) as total
           FROM bills WHERE company_id=$1 AND bill_type='expense'
           GROUP BY category ORDER BY total DESC""",
        company["id"]
    )
    return [dict(r) for r in rows]