from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, timedelta
from database import get_db
from api.auth import get_current_company
import statistics

router = APIRouter()


class PredictionRequest(BaseModel):
    project_id: Optional[int] = None
    prediction_type: str  # expense, material, labour


class MaterialEstimationRequest(BaseModel):
    project_id: int
    area: float  # in square feet
    construction_type: str  # residential, commercial, industrial


# ── Expense Prediction ───────────────────────────────────────────────────────

@router.post("/predict/expense")
async def predict_expense(
    body: PredictionRequest,
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    """
    Predict future expenses based on historical data
    Uses simple statistical analysis and trend extrapolation
    """
    try:
        # Get historical expense data for the last 6 months
        rows = await db.fetch(
            """SELECT bill_date, amount, category
               FROM bills
               WHERE company_id=$1
               AND bill_type='expense'
               AND bill_date >= CURRENT_DATE - INTERVAL '6 months'""",
            company["id"]
        )
        
        if not rows:
            return {
                "prediction": 0,
                "confidence": 0,
                "message": "Insufficient historical data for prediction"
            }
        
        # Calculate monthly average
        monthly_totals = {}
        for row in rows:
            month_key = row["bill_date"].strftime("%Y-%m")
            if month_key not in monthly_totals:
                monthly_totals[month_key] = 0
            monthly_totals[month_key] += float(row["amount"])
        
        monthly_values = list(monthly_totals.values())
        
        # Calculate trend (simple linear regression approximation)
        if len(monthly_values) >= 3:
            recent_avg = statistics.mean(monthly_values[-3:])
            earlier_avg = statistics.mean(monthly_values[:-3]) if len(monthly_values) > 3 else recent_avg
            
            # Trend factor
            trend_factor = recent_avg / earlier_avg if earlier_avg > 0 else 1.0
            
            # Predict next month's expense
            predicted = recent_avg * trend_factor
            
            # Confidence based on data consistency
            std_dev = statistics.stdev(monthly_values) if len(monthly_values) > 1 else 0
            mean = statistics.mean(monthly_values)
            confidence = max(0, min(100, 100 - (std_dev / mean * 100))) if mean > 0 else 0
        else:
            predicted = statistics.mean(monthly_values)
            confidence = 50  # Low confidence with limited data
        
        # Category-wise prediction
        category_data = {}
        for row in rows:
            category = row["category"] or "miscellaneous"
            if category not in category_data:
                category_data[category] = []
            category_data[category].append(float(row["amount"]))
        
        category_predictions = {}
        for cat, values in category_data.items():
            if values:
                category_predictions[cat] = {
                    "average": statistics.mean(values),
                    "predicted_next_month": statistics.mean(values) * (trend_factor if len(monthly_values) >= 3 else 1.0)
                }
        
        return {
            "predicted_monthly_expense": round(predicted, 2),
            "confidence": round(confidence, 2),
            "historical_average": round(statistics.mean(monthly_values), 2),
            "category_breakdown": category_predictions,
            "trend": "increasing" if trend_factor > 1.05 else "stable" if trend_factor > 0.95 else "decreasing"
        }
        
    except Exception as e:
        raise HTTPException(500, detail=f"Prediction failed: {str(e)}")


# ── Material Estimation ───────────────────────────────────────────────────────

@router.post("/estimate/material")
async def estimate_materials(
    body: MaterialEstimationRequest,
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    """
    Estimate material requirements based on construction area and type
    Uses standard construction ratios
    """
    try:
        area = body.area
        construction_type = body.construction_type.lower()
        
        # Standard material ratios per square foot (approximate values)
        if construction_type == "residential":
            ratios = {
                "cement": {"quantity": 0.5, "unit": "bags", "price_per_unit": 350},
                "steel": {"quantity": 4.0, "unit": "kg", "price_per_unit": 60},
                "sand": {"quantity": 1.8, "unit": "cubic_ft", "price_per_unit": 30},
                "bricks": {"quantity": 10.0, "unit": "pieces", "price_per_unit": 8},
                "aggregate": {"quantity": 1.5, "unit": "cubic_ft", "price_per_unit": 35}
            }
        elif construction_type == "commercial":
            ratios = {
                "cement": {"quantity": 0.6, "unit": "bags", "price_per_unit": 350},
                "steel": {"quantity": 5.5, "unit": "kg", "price_per_unit": 60},
                "sand": {"quantity": 2.0, "unit": "cubic_ft", "price_per_unit": 30},
                "bricks": {"quantity": 8.0, "unit": "pieces", "price_per_unit": 8},
                "aggregate": {"quantity": 1.8, "unit": "cubic_ft", "price_per_unit": 35}
            }
        else:  # industrial
            ratios = {
                "cement": {"quantity": 0.7, "unit": "bags", "price_per_unit": 350},
                "steel": {"quantity": 6.0, "unit": "kg", "price_per_unit": 60},
                "sand": {"quantity": 2.2, "unit": "cubic_ft", "price_per_unit": 30},
                "bricks": {"quantity": 6.0, "unit": "pieces", "price_per_unit": 8},
                "aggregate": {"quantity": 2.0, "unit": "cubic_ft", "price_per_unit": 35}
            }
        
        # Calculate estimated quantities and costs
        estimates = []
        total_cost = 0
        
        for material, data in ratios.items():
            quantity = round(data["quantity"] * area, 2)
            cost = round(quantity * data["price_per_unit"], 2)
            total_cost += cost
            
            estimates.append({
                "material": material,
                "quantity": quantity,
                "unit": data["unit"],
                "unit_price": data["price_per_unit"],
                "estimated_cost": cost
            })
        
        # Add contingency (10%)
        contingency = round(total_cost * 0.1, 2)
        total_with_contingency = total_cost + contingency
        
        return {
            "construction_type": construction_type,
            "area": area,
            "material_estimates": estimates,
            "total_material_cost": total_cost,
            "contingency": contingency,
            "total_estimated_cost": total_with_contingency,
            "note": "These are approximate estimates. Actual requirements may vary based on design and specifications."
        }
        
    except Exception as e:
        raise HTTPException(500, detail=f"Estimation failed: {str(e)}")


# ── Smart Insights ───────────────────────────────────────────────────────────

@router.get("/insights")
async def get_smart_insights(company=Depends(get_current_company), db=Depends(get_db)):
    """
    Generate smart insights based on project data
    """
    insights = []
    
    # Check for unusual spending patterns
    expense_rows = await db.fetch(
        """SELECT category, amount, bill_date
           FROM bills
           WHERE company_id=$1
           AND bill_type='expense'
           AND bill_date >= CURRENT_DATE - INTERVAL '3 months'
           ORDER BY amount DESC
           LIMIT 20""",
        company["id"]
    )
    
    if expense_rows:
        amounts = [float(r["amount"]) for r in expense_rows]
        mean = statistics.mean(amounts)
        std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
        
        # Flag unusual expenses (more than 2 standard deviations from mean)
        unusual = [r for r in expense_rows if float(r["amount"]) > mean + 2 * std_dev]
        if unusual:
            insights.append({
                "type": "warning",
                "title": "Unusual Spending Detected",
                "message": f"Found {len(unusual)} expenses significantly higher than average. Review these transactions.",
                "data": [dict(r) for r in unusual[:3]]
            })
    
    # Check for material shortages
    low_stock = await db.fetch(
        """SELECT name, remaining_quantity, total_quantity
           FROM materials
           WHERE company_id=$1
           AND total_quantity > 0
           AND (remaining_quantity / total_quantity) < 0.2
           LIMIT 5""",
        company["id"]
    )
    
    if low_stock:
        insights.append({
            "type": "alert",
            "title": "Material Shortage Alert",
            "message": f"{len(low_stock)} materials are running low (less than 20% remaining). Consider reordering.",
            "data": [dict(r) for r in low_stock]
        })
    
    # Check for pending payments
    pending_payments = await db.fetchval(
        """SELECT COUNT(*)
           FROM client_payments
           WHERE company_id=$1 AND status='pending'""",
        company["id"]
    )
    
    if pending_payments > 5:
        insights.append({
            "type": "info",
            "title": "Multiple Pending Payments",
            "message": f"You have {pending_payments} pending client payments. Follow up to improve cash flow.",
            "data": {"count": pending_payments}
        })
    
    # Check project progress vs budget
    projects = await db.fetch(
        """SELECT p.name, p.budget, p.progress,
           COALESCE(SUM(b.amount) FILTER (WHERE b.bill_type='expense'), 0) as spent
           FROM projects p
           LEFT JOIN bills b ON b.project_id = p.id
           WHERE p.company_id=$1 AND p.status='active'
           GROUP BY p.id, p.name, p.budget, p.progress""",
        company["id"]
    )
    
    for proj in projects:
        budget = float(proj["budget"] or 0)
        spent = float(proj["spent"] or 0)
        progress = proj["progress"] or 0
        
        if budget > 0:
            budget_used_percent = (spent / budget) * 100
            if budget_used_percent > progress + 20:
                insights.append({
                    "type": "warning",
                    "title": "Budget Overrun Risk",
                    "message": f"Project '{proj['name']}' has used {budget_used_percent:.1f}% of budget but is only {progress}% complete.",
                    "data": {"project": proj["name"], "budget_used": budget_used_percent, "progress": progress}
                })
    
    return {
        "insights": insights,
        "generated_at": date.today().isoformat()
    }


# ── Expense Analysis ─────────────────────────────────────────────────────────

@router.get("/analysis/expense-patterns")
async def analyze_expense_patterns(company=Depends(get_current_company), db=Depends(get_db)):
    """
    Analyze expense patterns to identify trends and optimization opportunities
    """
    # Category-wise spending
    category_spending = await db.fetch(
        """SELECT category, COALESCE(SUM(amount), 0) as total, COUNT(*) as count
           FROM bills
           WHERE company_id=$1 AND bill_type='expense'
           GROUP BY category
           ORDER BY total DESC""",
        company["id"]
    )
    
    # Day of week analysis
    dow_spending = await db.fetch(
        """SELECT EXTRACT(DOW FROM bill_date) as day_of_week,
           COALESCE(SUM(amount), 0) as total
           FROM bills
           WHERE company_id=$1 AND bill_type='expense'
           GROUP BY EXTRACT(DOW FROM bill_date)
           ORDER BY day_of_week""",
        company["id"]
    )
    
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    dow_analysis = []
    for row in dow_spending:
        dow_analysis.append({
            "day": days[int(row["day_of_week"])],
            "total": float(row["total"])
        })
    
    # Monthly trend
    monthly_trend = await db.fetch(
        """SELECT TO_CHAR(bill_date, 'YYYY-MM') as month,
           COALESCE(SUM(amount), 0) as total
           FROM bills
           WHERE company_id=$1 AND bill_type='expense'
           AND bill_date >= CURRENT_DATE - INTERVAL '12 months'
           GROUP BY TO_CHAR(bill_date, 'YYYY-MM')
           ORDER BY month""",
        company["id"]
    )
    
    return {
        "category_breakdown": [dict(r) for r in category_spending],
        "day_of_week_analysis": dow_analysis,
        "monthly_trend": [dict(r) for r in monthly_trend]
    }
