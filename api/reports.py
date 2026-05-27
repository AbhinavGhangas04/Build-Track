from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse
from database import get_db
from api.auth import get_current_company

router = APIRouter()


class ReportRequest(BaseModel):
    project_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    report_type: str  # expense, income, labour, material, profit_loss


# ── Excel Export ─────────────────────────────────────────────────────────────

@router.post("/export/excel")
async def export_excel(
    body: ReportRequest,
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    """
    Generate Excel report based on report type
    """
    try:
        if body.report_type == "expense":
            data = await get_expense_data(company["id"], body.project_id, body.from_date, body.to_date, db)
            df = pd.DataFrame(data)
            filename = "expense_report.xlsx"
        elif body.report_type == "income":
            data = await get_income_data(company["id"], body.project_id, body.from_date, body.to_date, db)
            df = pd.DataFrame(data)
            filename = "income_report.xlsx"
        elif body.report_type == "labour":
            data = await get_labour_data(company["id"], body.project_id, body.from_date, body.to_date, db)
            df = pd.DataFrame(data)
            filename = "labour_report.xlsx"
        elif body.report_type == "material":
            data = await get_material_data(company["id"], body.project_id, body.from_date, body.to_date, db)
            df = pd.DataFrame(data)
            filename = "material_report.xlsx"
        elif body.report_type == "profit_loss":
            data = await get_profit_loss_data(company["id"], body.project_id, body.from_date, body.to_date, db)
            df = pd.DataFrame(data)
            filename = "profit_loss_report.xlsx"
        else:
            raise HTTPException(400, "Invalid report type")
        
        # Generate Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(500, detail=f"Excel generation failed: {str(e)}")


async def get_expense_data(company_id, project_id, from_date, to_date, db):
    query = """SELECT b.*, p.name as project_name
               FROM bills b
               LEFT JOIN projects p ON p.id = b.project_id
               WHERE b.company_id=$1 AND b.bill_type='expense'"""
    params = [company_id]
    
    if project_id:
        query += " AND b.project_id=$2"
        params.append(project_id)
    if from_date:
        query += f" AND b.bill_date >= ${len(params) + 1}"
        params.append(from_date)
    if to_date:
        query += f" AND b.bill_date <= ${len(params) + 1}"
        params.append(to_date)
    
    query += " ORDER BY b.bill_date DESC"
    
    rows = await db.fetch(query, *params)
    return [dict(r) for r in rows]


async def get_income_data(company_id, project_id, from_date, to_date, db):
    query = """SELECT b.*, p.name as project_name
               FROM bills b
               LEFT JOIN projects p ON p.id = b.project_id
               WHERE b.company_id=$1 AND b.bill_type='income'"""
    params = [company_id]
    
    if project_id:
        query += " AND b.project_id=$2"
        params.append(project_id)
    if from_date:
        query += f" AND b.bill_date >= ${len(params) + 1}"
        params.append(from_date)
    if to_date:
        query += f" AND b.bill_date <= ${len(params) + 1}"
        params.append(to_date)
    
    query += " ORDER BY b.bill_date DESC"
    
    rows = await db.fetch(query, *params)
    return [dict(r) for r in rows]


async def get_labour_data(company_id, project_id, from_date, to_date, db):
    query = """SELECT lp.*, w.name as worker_name, p.name as project_name
               FROM labour_payments lp
               JOIN workers w ON w.id = lp.worker_id
               LEFT JOIN projects p ON p.id = lp.project_id
               WHERE lp.company_id=$1"""
    params = [company_id]
    
    if project_id:
        query += " AND lp.project_id=$2"
        params.append(project_id)
    if from_date:
        query += f" AND lp.payment_date >= ${len(params) + 1}"
        params.append(from_date)
    if to_date:
        query += f" AND lp.payment_date <= ${len(params) + 1}"
        params.append(to_date)
    
    query += " ORDER BY lp.payment_date DESC"
    
    rows = await db.fetch(query, *params)
    return [dict(r) for r in rows]


async def get_material_data(company_id, project_id, from_date, to_date, db):
    query = """SELECT m.*, p.name as project_name
               FROM materials m
               LEFT JOIN projects p ON p.id = m.project_id
               WHERE m.company_id=$1"""
    params = [company_id]
    
    if project_id:
        query += " AND m.project_id=$2"
        params.append(project_id)
    
    query += " ORDER BY m.name"
    
    rows = await db.fetch(query, *params)
    return [dict(r) for r in rows]


async def get_profit_loss_data(company_id, project_id, from_date, to_date, db):
    # Get income
    income_query = """SELECT COALESCE(SUM(amount), 0) as total_income
                      FROM bills
                      WHERE company_id=$1 AND bill_type='income'"""
    income_params = [company_id]
    
    if project_id:
        income_query += " AND project_id=$2"
        income_params.append(project_id)
    if from_date:
        income_query += f" AND bill_date >= ${len(income_params) + 1}"
        income_params.append(from_date)
    if to_date:
        income_query += f" AND bill_date <= ${len(income_params) + 1}"
        income_params.append(to_date)
    
    total_income = await db.fetchval(income_query, *income_params)
    
    # Get expenses
    expense_query = """SELECT COALESCE(SUM(amount), 0) as total_expense
                       FROM bills
                       WHERE company_id=$1 AND bill_type='expense'"""
    expense_params = [company_id]
    
    if project_id:
        expense_query += " AND project_id=$2"
        expense_params.append(project_id)
    if from_date:
        expense_query += f" AND bill_date >= ${len(expense_params) + 1}"
        expense_params.append(from_date)
    if to_date:
        expense_query += f" AND bill_date <= ${len(expense_params) + 1}"
        expense_params.append(to_date)
    
    total_expense = await db.fetchval(expense_query, *expense_params)
    
    profit = float(total_income) - float(total_expense)
    
    return [{
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "profit": profit,
        "profit_percentage": (profit / float(total_income) * 100) if total_income > 0 else 0
    }]


# ── Dashboard Analytics ───────────────────────────────────────────────────────

@router.get("/dashboard/analytics")
async def dashboard_analytics(
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    """
    Get comprehensive dashboard analytics
    """
    # Total income and expenses
    financials = await db.fetchrow(
        """SELECT
             COALESCE(SUM(amount) FILTER (WHERE bill_type='income'), 0) as total_income,
             COALESCE(SUM(amount) FILTER (WHERE bill_type='expense'), 0) as total_expense
           FROM bills WHERE company_id=$1""",
        company["id"]
    )
    
    # Active projects count
    active_projects = await db.fetchval(
        "SELECT COUNT(*) FROM projects WHERE company_id=$1 AND status='active'",
        company["id"]
    )
    
    # Total workers
    total_workers = await db.fetchval(
        "SELECT COUNT(*) FROM workers WHERE company_id=$1",
        company["id"]
    )
    
    # Pending payments
    pending_payments = await db.fetchval(
        """SELECT COALESCE(SUM(amount), 0)
           FROM client_payments
           WHERE company_id=$1 AND status='pending'""",
        company["id"]
    )
    
    # Material cost
    material_cost = await db.fetchval(
        """SELECT COALESCE(SUM(total_quantity * unit_price), 0)
           FROM materials
           WHERE company_id=$1""",
        company["id"]
    )
    
    # Labour cost this month
    labour_cost = await db.fetchval(
        """SELECT COALESCE(SUM(amount), 0)
           FROM labour_payments
           WHERE company_id=$1
           AND EXTRACT(MONTH FROM payment_date) = EXTRACT(MONTH FROM CURRENT_DATE)
           AND EXTRACT(YEAR FROM payment_date) = EXTRACT(YEAR FROM CURRENT_DATE)""",
        company["id"]
    )
    
    # Recent activity (last 10 bills)
    recent_activity = await db.fetch(
        """SELECT b.*, p.name as project_name
           FROM bills b
           LEFT JOIN projects p ON p.id = b.project_id
           WHERE b.company_id=$1
           ORDER BY b.created_at DESC
           LIMIT 10""",
        company["id"]
    )
    
    return {
        "financials": dict(financials),
        "active_projects": active_projects,
        "total_workers": total_workers,
        "pending_payments": float(pending_payments),
        "material_cost": float(material_cost),
        "labour_cost_this_month": float(labour_cost),
        "recent_activity": [dict(r) for r in recent_activity]
    }


@router.get("/dashboard/category-breakdown")
async def category_breakdown(
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    """
    Get expense breakdown by category
    """
    rows = await db.fetch(
        """SELECT category, COALESCE(SUM(amount), 0) as total
           FROM bills
           WHERE company_id=$1 AND bill_type='expense'
           GROUP BY category
           ORDER BY total DESC""",
        company["id"]
    )
    return [dict(r) for r in rows]


@router.get("/dashboard/monthly-trends")
async def monthly_trends(
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    """
    Get monthly income and expense trends for the last 12 months
    """
    rows = await db.fetch(
        """SELECT
             TO_CHAR(bill_date, 'YYYY-MM') as month,
             COALESCE(SUM(amount) FILTER (WHERE bill_type='income'), 0) as income,
             COALESCE(SUM(amount) FILTER (WHERE bill_type='expense'), 0) as expense
           FROM bills
           WHERE company_id=$1
           AND bill_date >= CURRENT_DATE - INTERVAL '12 months'
           GROUP BY TO_CHAR(bill_date, 'YYYY-MM')
           ORDER BY month""",
        company["id"]
    )
    return [dict(r) for r in rows]
