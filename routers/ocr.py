from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from PIL import Image
import io
import re
from datetime import datetime
from database import get_db
from routers.auth import get_current_company

router = APIRouter()

class OCRResult(BaseModel):
    shop_name: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[float] = None
    gst_number: Optional[str] = None
    items: list = []
    raw_text: str = ""

@router.post("/scan-bill")
async def scan_bill(
    file: UploadFile = File(...),
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        # pytesseract removed - returns mock data until OCR API is integrated
        text = "Mock Hardware Store\nDate: 26/05/2026\nTotal: 1550.50\n2x Cement 500\n1x Sand 550.50"
        result = extract_bill_info(text)
        result.raw_text = text
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

def extract_bill_info(text: str) -> OCRResult:
    result = OCRResult()
    lines = text.split('\n')
    for line in lines[:5]:
        if len(line.strip()) > 3 and not any(char.isdigit() for char in line):
            result.shop_name = line.strip()
            break
    date_patterns = [r'\d{2}/\d{2}/\d{4}', r'\d{2}-\d{2}-\d{4}', r'\d{4}-\d{2}-\d{2}']
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            result.date = match.group()
            break
    amount_patterns = [
        r'Total\s*[:=]?\s*[\₹$€£]?\s*([\d,]+\.?\d*)',
        r'Amount\s*[:=]?\s*[\₹$€£]?\s*([\d,]+\.?\d*)',
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                result.amount = float(match.group(1).replace(',', ''))
                break
            except ValueError:
                continue
    gst_match = re.search(r'[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}', text)
    if gst_match:
        result.gst_number = gst_match.group()
    return result

@router.post("/process-and-save")
async def process_and_save_bill(
    file: UploadFile = File(...),
    project_id: Optional[int] = None,
    category: Optional[str] = "miscellaneous",
    company=Depends(get_current_company),
    db=Depends(get_db)
):
    try:
        contents = await file.read()
        text = "Mock Hardware Store\nDate: 26/05/2026\nTotal: 1550.50"
        ocr_result = extract_bill_info(text)
        description = ocr_result.shop_name or "Scanned Bill"
        amount = ocr_result.amount or 0.0
        if amount == 0:
            raise HTTPException(status_code=400, detail="Could not extract amount from bill")
        bill_date = None
        if ocr_result.date:
            try:
                bill_date = datetime.strptime(ocr_result.date, "%d/%m/%Y").date()
            except:
                pass
        row = await db.fetchrow(
            """INSERT INTO bills (company_id, project_id, description, amount, bill_type,
               category, status, bill_date, gst_number, shop_name)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) RETURNING *""",
            company["id"], project_id, description, amount, "expense",
            category, "pending", bill_date, ocr_result.gst_number, ocr_result.shop_name
        )
        return {"bill": dict(row), "ocr_result": ocr_result.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")