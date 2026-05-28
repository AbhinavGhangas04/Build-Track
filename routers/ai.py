from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_db
from routers.auth import get_current_company
import statistics

router = APIRouter()

class PredictionRequest(BaseModel):
    project_id: Optional[int] = None
    prediction_type: str

class MaterialEstimationRequest(BaseModel):
    project_id: int
    area: float
    construction_type: str

@router.post("/predict/expense")
async def predict_expense(body: PredictionRequest, company=Depends(get_current_company), db=Depends(get_db)):
    try:
        rows = await db.fetch(
            """SELECT bill_date, amount, category FROM bills
               WHERE company_id=$1 AND bill_type='expense'
               AND bill_date >= CURRENT_DATE - INTERVAL '6 months'""",
            company["id"]
        )
        if not rows:
            return {"prediction": 0, "confidence": 0, "message": "Insufficient historical data"}
        monthly_totals = {}
        for row in rows:
            month_key = row["bill_date"].strftime("%Y-%m")
            monthly_totals[month_key] = monthly_totals.get(month_key, 0) + float(row["amount"])
        monthly_values = list(monthly_totals.values())
        if len(monthly_values) >= 3:
            recent_avg = statistics.mean(monthly_values[-3:])
            earlier_avg = statistics.mean(monthly_values[:-3]) if len(monthly_values) > 3 else recent_avg
            trend_factor = recent_avg / earlier_avg if earlier_avg > 0 else 1.0
            predicted = recent_avg * trend_factor
            std_dev = statistics.stdev(monthly_values) if len(monthly_values) > 1 else 0
            mean = statistics.mean(monthly_values)
            confidence = max(0, min(100, 100 - (std_dev / mean * 100))) if mean > 0 else 0
        else:
            predicted = statistics.mean(monthly_values)
            confidence = 50
            trend_factor = 1.0
        return {
            "predicted_monthly_expense": round(predicted, 2),
            "confidence": round(confidence, 2),
            "historical_average": round(statistics.mean(monthly_values), 2),
            "trend": "increasing" if trend_factor > 1.05 else "stable" if trend_factor > 0.95 else "decreasing"
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Prediction failed: {str(e)}")

@router.post("/estimate/material")
async def estimate_materials(body: MaterialEstimationRequest, company=Depends(get_current_company), db=Depends(get_db)):
    area = body.area
    construction_type = body.construction_type.lower()
    ratios = {
        "residential": {"cement": (0.5, "bags", 350), "steel": (4.0, "kg", 60), "sand": (1.8, "cubic_ft", 30), "bricks": (10.0, "pieces", 8)},
        "commercial":  {"cement": (0.6, "bags", 350), "steel": (5.5, "kg", 60), "sand": (2.0, "cubic_ft", 30), "bricks": (8.0, "pieces", 8)},
        "industrial":  {"cement": (0.7, "bags", 350), "steel": (6.0, "kg", 60), "sand": (2.2, "cubic_ft", 30), "bricks": (6.0, "pieces", 8)},
    }.get(construction_type, {"cement": (0.5, "bags", 350), "steel": (4.0, "kg", 60)})
    estimates = []
    total_cost = 0
    for material, (qty_ratio, unit, price) in ratios.items():
        quantity = round(qty_ratio * area, 2)
        cost = round(quantity * price, 2)
        total_cost += cost
        estimates.append({"material": material, "quantity": quantity, "unit": unit, "unit_price": price, "estimated_cost": cost})
    contingency = round(total_cost * 0.1, 2)
    return {"construction_type": construction_type, "area": area, "material_estimates": estimates,
            "total_material_cost": total_cost, "contingency": contingency, "total_estimated_cost": total_cost + contingency}

@router.get("/insights")
async def get_smart_insights(company=Depends(get_current_company), db=Depends(get_db)):
    insights = []
    low_stock = await db.fetch(
        """SELECT name, remaining_quantity, total_quantity FROM materials
           WHERE company_id=$1 AND total_quantity > 0
           AND (remaining_quantity / total_quantity) < 0.2 LIMIT 5""",
        company["id"]
    )
    if low_stock:
        insights.append({"type": "alert", "title": "Material Shortage Alert",
                         "message": f"{len(low_stock)} materials are running low.", "data": [dict(r) for r in low_stock]})
    pending_payments = await db.fetchval(
        "SELECT COUNT(*) FROM client_payments WHERE company_id=$1 AND status='pending'", company["id"]
    )
    if pending_payments > 5:
        insights.append({"type": "info", "title": "Multiple Pending Payments",
                         "message": f"You have {pending_payments} pending client payments.", "data": {"count": pending_payments}})
    return {"insights": insights, "generated_at": date.today().isoformat()}