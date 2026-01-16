"""
FastAPI endpoints для биллинга TERAG
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, EmailStr

from src.billing.core import BillingCore
from src.billing.models import UsageMeter, Invoice, Client
from src.billing.database import get_billing_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/billing", tags=["billing"])


# Pydantic модели для запросов
class CreateClientRequest(BaseModel):
    name: str
    email: EmailStr
    billing_tier: str = "standard"
    currency: str = "USD"


class GenerateInvoiceRequest(BaseModel):
    client_id: str
    period_start: str  # ISO format
    period_end: str    # ISO format


# Dependency для получения BillingCore
def get_billing_core() -> BillingCore:
    """Dependency для получения BillingCore"""
    return BillingCore()


@router.post("/clients", response_model=Client)
async def create_client(
    request: CreateClientRequest,
    billing: BillingCore = Depends(get_billing_core)
):
    """
    Создать нового клиента
    
    Returns:
        Client объект
    """
    try:
        client = billing.create_client(
            name=request.name,
            email=request.email,
            billing_tier=request.billing_tier,
            currency=request.currency
        )
        return client
    except Exception as e:
        logger.error(f"Failed to create client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients/{client_id}", response_model=Client)
async def get_client(
    client_id: str,
    billing: BillingCore = Depends(get_billing_core)
):
    """
    Получить информацию о клиенте
    
    Args:
        client_id: ID клиента
    
    Returns:
        Client объект
    """
    db = get_billing_db()
    client_doc = db.clients_collection.find_one({"client_id": client_id})
    
    if not client_doc:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Преобразуем ObjectId в строку для JSON
    client_doc.pop("_id", None)
    return client_doc


@router.get("/clients/{client_id}/usage")
async def get_client_usage(
    client_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    billing: BillingCore = Depends(get_billing_core)
):
    """
    Получить использование клиента
    
    Args:
        client_id: ID клиента
        start_date: Начало периода (ISO format, опционально)
        end_date: Конец периода (ISO format, опционально)
    
    Returns:
        Список записей использования
    """
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        usage = billing.get_client_usage(client_id, start, end)
        
        # Преобразуем ObjectId в строки
        for record in usage:
            record.pop("_id", None)
        
        return {
            "client_id": client_id,
            "usage_count": len(usage),
            "total_cost": sum(r.get("cost_usd", 0.0) for r in usage),
            "usage": usage
        }
    except Exception as e:
        logger.error(f"Failed to get usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoices/generate", response_model=Invoice)
async def generate_invoice(
    request: GenerateInvoiceRequest,
    billing: BillingCore = Depends(get_billing_core)
):
    """
    Сгенерировать инвойс за период
    
    Args:
        request: Параметры генерации инвойса
    
    Returns:
        Invoice объект
    """
    try:
        period_start = datetime.fromisoformat(request.period_start)
        period_end = datetime.fromisoformat(request.period_end)
        
        invoice = billing.generate_invoice(
            client_id=request.client_id,
            period_start=period_start,
            period_end=period_end
        )
        return invoice
    except Exception as e:
        logger.error(f"Failed to generate invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """
    Получить инвойс по ID
    
    Args:
        invoice_id: ID инвойса
    
    Returns:
        Invoice объект
    """
    db = get_billing_db()
    invoice_doc = db.invoices_collection.find_one({"invoice_id": invoice_id})
    
    if not invoice_doc:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice_doc.pop("_id", None)
    return invoice_doc


@router.get("/clients/{client_id}/invoices")
async def get_client_invoices(
    client_id: str,
    status: Optional[str] = None,
    billing: BillingCore = Depends(get_billing_core)
):
    """
    Получить все инвойсы клиента
    
    Args:
        client_id: ID клиента
        status: Фильтр по статусу (опционально)
    
    Returns:
        Список инвойсов
    """
    try:
        invoices = billing.get_client_invoices(client_id, status)
        
        # Преобразуем ObjectId в строки
        for invoice in invoices:
            invoice.pop("_id", None)
        
        return {
            "client_id": client_id,
            "invoice_count": len(invoices),
            "invoices": invoices
        }
    except Exception as e:
        logger.error(f"Failed to get invoices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}/pdf")
async def get_invoice_pdf(
    invoice_id: str,
    billing: BillingCore = Depends(get_billing_core)
):
    """
    Получить PDF инвойса
    
    Args:
        invoice_id: ID инвойса
    
    Returns:
        PDF файл
    """
    from fastapi.responses import Response
    from src.billing.invoice_pdf import generate_invoice_pdf
    
    try:
        # Получаем инвойс
        db = get_billing_db()
        invoice_doc = db.invoices_collection.find_one({"invoice_id": invoice_id})
        
        if not invoice_doc:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Получаем usage summary для инвойса
        usage_records = list(
            db.usage_collection.find({
                "client_id": invoice_doc["client_id"],
                "timestamp": {
                    "$gte": invoice_doc["period_start"],
                    "$lte": invoice_doc["period_end"]
                }
            })
        )
        
        # Группируем по типу запроса
        usage_summary = {}
        for record in usage_records:
            query_type = record.get("query_type", "simple")
            if query_type not in usage_summary:
                usage_summary[query_type] = {"count": 0, "total": 0.0}
            usage_summary[query_type]["count"] += 1
            usage_summary[query_type]["total"] += record.get("cost_usd", 0.0)
        
        # Формируем данные для PDF
        invoice_data = {
            "invoice_id": invoice_doc.get("invoice_id"),
            "client_id": invoice_doc.get("client_id"),
            "period_start": invoice_doc.get("period_start").strftime("%Y-%m-%d") if invoice_doc.get("period_start") else "N/A",
            "period_end": invoice_doc.get("period_end").strftime("%Y-%m-%d") if invoice_doc.get("period_end") else "N/A",
            "due_date": invoice_doc.get("due_date").strftime("%Y-%m-%d") if invoice_doc.get("due_date") else "N/A",
            "status": invoice_doc.get("status", "draft"),
            "total_amount": invoice_doc.get("total_amount", 0.0),
            "currency": invoice_doc.get("currency", "USD"),
            "usage_summary": [
                {
                    "query_type": qtype,
                    "count": data["count"],
                    "unit_price": billing.tiers.get(qtype, 0.01),
                    "total": data["total"],
                    "currency": invoice_doc.get("currency", "USD")
                }
                for qtype, data in usage_summary.items()
            ]
        }
        
        # Генерируем PDF
        pdf_bytes = generate_invoice_pdf(invoice_data)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="invoice_{invoice_id}.pdf"'
            }
        )
    except ImportError as e:
        logger.error(f"PDF generation library not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="PDF generation is not available. Please install weasyprint or reportlab."
        )
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))