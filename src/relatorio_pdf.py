from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
from datetime import datetime
import os

PRIMARY = HexColor("#10012c")
SECONDARY = HexColor("#2ED3C6")
ACCENT = HexColor("#F5B301")
TEXT = HexColor("#1F1F1F")

def formatar_data_br(data):
    if isinstance(data, (datetime,)):
        return data.strftime("%d/%m/%Y")
    try:
        return datetime.fromisoformat(str(data)).strftime("%d/%m/%Y")
    except:
        return str(data)

def formatar_valor_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_relatorio_pdf(rows, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    def header():
        c.setFillColor(PRIMARY)
        c.rect(0, height - 3*cm, width, 3*cm, fill=True, stroke=False)

        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"img","logo.png")
        if os.path.exists(logo_path):
            c.drawImage(
                logo_path,
                1.0*cm,
                height - 3.0*cm,
                width=3*cm,
                height=3*cm,
            )

        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont("Helvetica-Bold", 24)
        c.drawString(4*cm, height - 1.8*cm, "Relatório de Gastos")

        c.setFillColor(SECONDARY)
        c.setFont("Helvetica", 9)
        c.drawRightString(
            width - 2.0*cm,
            height - 2.5*cm,
            datetime.now().strftime("%d/%m/%Y %H:%M")
        )

    header()

    # ===== Cabeçalho da tabela =====
    y = height - 4*cm
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(TEXT)

    c.drawString(2*cm, y, "Categoria")
    c.drawString(6*cm, y, "Data")
    c.drawString(9*cm, y, "Observação")
    c.drawRightString(width - 2*cm, y, "Valor")

    y -= 0.4*cm
    c.setStrokeColor(SECONDARY)
    c.line(2*cm, y, width - 2*cm, y)
    y -= 0.3*cm

    # ===== Dados =====
    c.setFont("Helvetica", 9)
    total = 0

    for valor, categoria, data, raw_texto in rows:
        if y < 2.5*cm:
            c.showPage()
            header()
            y = height - 4*cm
            c.setFont("Helvetica", 9)

        c.drawString(2*cm, y, categoria[:20])
        c.drawString(6*cm, y, formatar_data_br(data))
        c.drawString(9*cm, y, raw_texto.strip()[:60])
        c.drawRightString(width - 2*cm, y, formatar_valor_br(valor))

        y -= 0.45*cm
        total += valor

    # ===== Total =====
    y -= 0.5*cm
    c.setStrokeColor(SECONDARY)
    c.line(2*cm, y, width - 2*cm, y)

    y -= 0.5*cm
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(ACCENT)
    c.drawRightString(
        width - 2*cm,
        y,
        f"Total: {formatar_valor_br(total)}"
    )

    # ===== Rodapé =====
    c.setFillColor(HexColor("#777777"))
    c.setFont("Helvetica", 10)
    c.drawCentredString(
        width / 2,
        1.5*cm,
        "Gerado automaticamente pelo ByteGasto"
    )

    c.save()