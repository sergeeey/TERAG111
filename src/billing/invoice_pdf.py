"""
Генерация PDF инвойсов для TERAG
"""

import logging
from datetime import datetime
from typing import Optional
from pathlib import Path
from io import BytesIO

logger = logging.getLogger(__name__)

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning("weasyprint not available, PDF generation will use fallback")

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab not available")


def generate_invoice_pdf_html(invoice_data: dict) -> bytes:
    """
    Генерация PDF инвойса через HTML (weasyprint)
    
    Args:
        invoice_data: Данные инвойса
        
    Returns:
        PDF bytes
    """
    if not WEASYPRINT_AVAILABLE:
        raise ImportError("weasyprint is required for PDF generation")
    
    # HTML шаблон инвойса
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.6;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .invoice-title {{
                font-size: 24pt;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .invoice-info {{
                margin: 20px 0;
            }}
            .info-row {{
                margin: 5px 0;
            }}
            .section {{
                margin: 20px 0;
            }}
            .section-title {{
                font-weight: bold;
                font-size: 14pt;
                margin-bottom: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            .total-row {{
                font-weight: bold;
                font-size: 14pt;
            }}
            .footer {{
                margin-top: 40px;
                text-align: center;
                font-size: 10pt;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="invoice-title">INVOICE</div>
            <div>TERAG AI-REPS System</div>
        </div>
        
        <div class="invoice-info">
            <div class="info-row"><strong>Invoice ID:</strong> {invoice_data.get('invoice_id', 'N/A')}</div>
            <div class="info-row"><strong>Client ID:</strong> {invoice_data.get('client_id', 'N/A')}</div>
            <div class="info-row"><strong>Period:</strong> {invoice_data.get('period_start', 'N/A')} - {invoice_data.get('period_end', 'N/A')}</div>
            <div class="info-row"><strong>Due Date:</strong> {invoice_data.get('due_date', 'N/A')}</div>
            <div class="info-row"><strong>Status:</strong> {invoice_data.get('status', 'N/A')}</div>
        </div>
        
        <div class="section">
            <div class="section-title">Usage Summary</div>
            <table>
                <thead>
                    <tr>
                        <th>Query Type</th>
                        <th>Count</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {_generate_usage_rows(invoice_data.get('usage_summary', []))}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="total-row">
                <div style="text-align: right;">
                    <strong>Total Amount: {invoice_data.get('currency', 'USD')} {invoice_data.get('total_amount', 0):.2f}</strong>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p>TERAG - Traceable Reasoning Architecture Graph</p>
        </div>
    </body>
    </html>
    """
    
    # Генерируем PDF
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()
    
    return pdf_bytes


def _generate_usage_rows(usage_summary: list) -> str:
    """Генерация строк таблицы использования"""
    if not usage_summary:
        return "<tr><td colspan='4'>No usage data</td></tr>"
    
    rows = []
    for item in usage_summary:
        rows.append(f"""
            <tr>
                <td>{item.get('query_type', 'N/A')}</td>
                <td>{item.get('count', 0)}</td>
                <td>{item.get('currency', 'USD')} {item.get('unit_price', 0):.2f}</td>
                <td>{item.get('currency', 'USD')} {item.get('total', 0):.2f}</td>
            </tr>
        """)
    
    return "\n".join(rows)


def generate_invoice_pdf_reportlab(invoice_data: dict) -> bytes:
    """
    Генерация PDF инвойса через reportlab (fallback)
    
    Args:
        invoice_data: Данные инвойса
        
    Returns:
        PDF bytes
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab is required for PDF generation")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    
    # Стили
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#000000'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Содержимое
    story = []
    
    # Заголовок
    story.append(Paragraph("INVOICE", title_style))
    story.append(Paragraph("TERAG AI-REPS System", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Информация об инвойсе
    invoice_info = [
        ['Invoice ID:', invoice_data.get('invoice_id', 'N/A')],
        ['Client ID:', invoice_data.get('client_id', 'N/A')],
        ['Period:', f"{invoice_data.get('period_start', 'N/A')} - {invoice_data.get('period_end', 'N/A')}"],
        ['Due Date:', invoice_data.get('due_date', 'N/A')],
        ['Status:', invoice_data.get('status', 'N/A')],
    ]
    
    info_table = Table(invoice_info, colWidths=[60*mm, 120*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Таблица использования
    usage_data = [['Query Type', 'Count', 'Unit Price', 'Total']]
    usage_summary = invoice_data.get('usage_summary', [])
    
    for item in usage_summary:
        usage_data.append([
            item.get('query_type', 'N/A'),
            str(item.get('count', 0)),
            f"{item.get('currency', 'USD')} {item.get('unit_price', 0):.2f}",
            f"{item.get('currency', 'USD')} {item.get('total', 0):.2f}"
        ])
    
    usage_table = Table(usage_data, colWidths=[60*mm, 30*mm, 40*mm, 40*mm])
    usage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    story.append(usage_table)
    story.append(Spacer(1, 20))
    
    # Итоговая сумма
    total_text = f"<b>Total Amount: {invoice_data.get('currency', 'USD')} {invoice_data.get('total_amount', 0):.2f}</b>"
    story.append(Paragraph(total_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Футер
    footer_text = f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}<br/>TERAG - Traceable Reasoning Architecture Graph"
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Генерируем PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_invoice_pdf(invoice_data: dict, method: str = "auto") -> bytes:
    """
    Генерация PDF инвойса
    
    Args:
        invoice_data: Данные инвойса (dict с полями invoice_id, client_id, total_amount, etc.)
        method: Метод генерации ("auto", "weasyprint", "reportlab")
        
    Returns:
        PDF bytes
        
    Raises:
        ImportError: Если нет доступных библиотек для генерации PDF
    """
    if method == "auto":
        if WEASYPRINT_AVAILABLE:
            method = "weasyprint"
        elif REPORTLAB_AVAILABLE:
            method = "reportlab"
        else:
            raise ImportError("No PDF generation library available. Install weasyprint or reportlab.")
    
    if method == "weasyprint":
        if not WEASYPRINT_AVAILABLE:
            raise ImportError("weasyprint is not installed")
        return generate_invoice_pdf_html(invoice_data)
    elif method == "reportlab":
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is not installed")
        return generate_invoice_pdf_reportlab(invoice_data)
    else:
        raise ValueError(f"Unknown method: {method}")
