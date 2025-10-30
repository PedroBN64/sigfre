# reports/gerar_pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import os

def gerar_folha(mes, ano, dados, logo_path="assets/timbrado.png", output="folha.pdf"):
    doc = SimpleDocTemplate(output, pagesize=A4, topMargin=1.5*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Logo
    if os.path.exists(logo_path):
        try:
            img = Image(logo_path, width=15*cm, height=3*cm)
            img.hAlign = "CENTER"
            elements.append(img)
            elements.append(Spacer(1, 20))
        except:
            pass

    # Título
    titulo = Paragraph(
        "<font size=14><b>FOLHA DE PAGAMENTO FUNCIONÁRIOS DA “EMEIEF CEL NOGUEIRA COBRA”</b></font><br/>"
        f"<font size=11>MÊS de Referência: – De 01/{mes.zfill(2)} a 31/{mes.zfill(2)} – {ano}</font>",
        styles["Title"]
    )
    elements.append(titulo)
    elements.append(Spacer(1, 30))

    # Tabela
    header = ["Nº", "Nome", "RG", "Cargo", "Contrato", "Carga Horária", "Observações"]
    data = [header]
    for i, f in enumerate(dados, 1):
        obs = f["observacoes"] if f["observacoes"].strip() else "FREQUENTE"
        data.append([str(i), f["nome"], f["rg"], f["cargo"], f["contrato"], f["carga_horaria"], obs])

    table = Table(data, colWidths=[1.2*cm, 5*cm, 2.5*cm, 3*cm, 2.5*cm, 3*cm, 5*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1f6aa5")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),
        ("BOTTOMPADDING", (0,0), (-1,0), 12),
        ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#f8f9fa")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTSIZE", (0,1), (-1,-1), 9),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 60))

    # Assinatura
    elements.append(Paragraph("Local e Data: __________, ____ de ________________ de " + ano, styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("_________________________________________", styles["Normal"]))
    elements.append(Paragraph("Assinatura do Diretor", styles["Normal"]))

    doc.build(elements)

    # Abre o PDF
    try:
        os.startfile(output)
    except:
        print(f"PDF salvo em: {os.path.abspath(output)}")
