from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_db
from api.auth import get_current_company

router = APIRouter()


class MaterialIn(BaseModel):
    name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    total_quantity: Optional[float] = 0
    unit_price: Optional[float] = 0
    supplier_name: Optional[str] = None
    supplier_phone: Optional[str] = None
    project_id: Optional[int] = None


class MaterialUsageIn(BaseModel):
    material_id: int
    quantity: float
    purpose: Optional[str] = None
    project_id: Optional[int] = None
    usage_date: Optional[date] = None


# ── Materials CRUD ───────────────────────────────────────────────────────────

@router.get("/")
async def list_materials(company=Depends(get_current_company), db=Depends(get_db)):
    rows = await db.fetch(
        """SELECT m.*, p.name as project_name
           FROM materials m
           LEFT JOIN projects p ON p.id = m.project_id
           WHERE m.company_id=$1
           ORDER BY m.name""",
        company["id"]
    )
    return [dict(r) for r in rows]


@router.get("/{material_id}")
async def get_material(material_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """SELECT m.*, p.name as project_name
           FROM materials m
           LEFT JOIN projects p ON p.id = m.project_id
           WHERE m.id=$1 AND m.company_id=$2""",
        material_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Material not found")
    return dict(row)


@router.post("/")
async def create_material(body: MaterialIn, company=Depends(get_current_company), db=Depends(get_db)):
    remaining = body.total_quantity
    row = await db.fetchrow(
        """INSERT INTO materials (company_id, project_id, name, category, unit,
           total_quantity, used_quantity, remaining_quantity, unit_price,
           supplier_name, supplier_phone)
           VALUES ($1,$2,$3,$4,$5,$6,0,$7,$8,$9,$10) RETURNING *""",
        company["id"], body.project_id, body.name, body.category, body.unit,
        body.total_quantity, remaining, body.unit_price,
        body.supplier_name, body.supplier_phone
    )
    return dict(row)


@router.put("/{material_id}")
async def update_material(material_id: int, body: MaterialIn,
                         company=Depends(get_current_company), db=Depends(get_db)):
    remaining = body.total_quantity
    row = await db.fetchrow(
        """UPDATE materials SET name=$1, category=$2, unit=$3, total_quantity=$4,
           remaining_quantity=$5, unit_price=$6, supplier_name=$7, supplier_phone=$8,
           project_id=$9
           WHERE id=$10 AND company_id=$11 RETURNING *""",
        body.name, body.category, body.unit, body.total_quantity, remaining,
        body.unit_price, body.supplier_name, body.supplier_phone, body.project_id,
        material_id, company["id"]
    )
    if not row:
        raise HTTPException(404, "Material not found")
    return dict(row)


@router.delete("/{material_id}")
async def delete_material(material_id: int, company=Depends(get_current_company), db=Depends(get_db)):
    await db.execute(
        "DELETE FROM materials WHERE id=$1 AND company_id=$2", material_id, company["id"]
    )
    return {"ok": True}


# ── Material Usage ───────────────────────────────────────────────────────────

@router.get("/usage/history")
async def get_usage_history(
    material_id: Optional[int] = None,
    project_id: Optional[int] = None,
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    query = """SELECT mu.*, m.name as material_name, p.name as project_name
              FROM material_usage mu
              JOIN materials m ON m.id = mu.material_id
              LEFT JOIN projects p ON p.id = mu.project_id
              WHERE mu.company_id=$1"""
    params = [company["id"]]
    
    if material_id:
        query += " AND mu.material_id=$2"
        params.append(material_id)
    elif project_id:
        query += " AND mu.project_id=$2"
        params.append(project_id)
    
    query += " ORDER BY mu.usage_date DESC"
    
    rows = await db.fetch(query, *params)
    return [dict(r) for r in rows]


@router.post("/usage")
async def record_usage(body: MaterialUsageIn, company=Depends(get_current_company), db=Depends(get_db)):
    # Record usage
    usage_row = await db.fetchrow(
        """INSERT INTO material_usage (company_id, material_id, project_id, quantity,
           usage_date, purpose)
           VALUES ($1,$2,$3,$4,$5,$6) RETURNING *""",
        company["id"], body.material_id, body.project_id, body.quantity,
        body.usage_date or date.today(), body.purpose
    )
    
    # Update material quantities
    await db.execute(
        """UPDATE materials SET used_quantity = used_quantity + $1,
           remaining_quantity = total_quantity - used_quantity - $1
           WHERE id=$2 AND company_id=$3""",
        body.quantity, body.material_id, company["id"]
    )
    
    return dict(usage_row)


# ── Summary ─────────────────────────────────────────────────────────────────

@router.get("/summary/overview")
async def materials_summary(company=Depends(get_current_company), db=Depends(get_db)):
    row = await db.fetchrow(
        """SELECT
             COUNT(*) as total_materials,
             COALESCE(SUM(total_quantity), 0) as total_quantity,
             COALESCE(SUM(used_quantity), 0) as total_used,
             COALESCE(SUM(remaining_quantity), 0) as total_remaining,
             COALESCE(SUM(total_quantity * unit_price), 0) as total_value
           FROM materials
           WHERE company_id=$1""",
        company["id"]
    )
    
    # Low stock alert (less than 20% remaining)
    low_stock = await db.fetch(
        """SELECT name, remaining_quantity, total_quantity, unit
           FROM materials
           WHERE company_id=$1
           AND total_quantity > 0
           AND (remaining_quantity / total_quantity) < 0.2
           ORDER BY (remaining_quantity / total_quantity)""",
        company["id"]
    )
    
    return {
        **dict(row),
        "low_stock_alerts": [dict(r) for r in low_stock]
    }
