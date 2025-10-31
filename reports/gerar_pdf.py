# reports/gerar_pdf.py
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import os
import calendar
from database.db import conectar

def validar_mes_ano(mes, ano):
    try:
        mes, ano = int(mes), int(ano)
        if not (1 <= mes <= 12 and 2020 <= ano <= 2030):
            return False, None, None, None
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        return True, mes, ano, ultimo_dia
    except:
        return False, None, None, None

def gerar_folha(mes, ano, logo_path="assets/timbrado.png", output="folha.pdf"):
    valido, mes, ano, ultimo_dia = validar_mes_ano(mes, ano)
    if not valido:
        from CTkMessagebox import CTkMessagebox
        CTkMessagebox(title="Erro", message="Mês ou ano inválido!", icon="cancel")
        return

    # === CONFIGURAÇÃO DO DOCUMENTO ===
    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=2.0 * cm,
        bottomMargin=1.8 * cm
    )
    elements = []
    styles = getSampleStyleSheet()

    # Estilo personalizado para título
    titulo_style = ParagraphStyle(
        "TituloCentralizado",
        parent=styles["Title"],
        alignment=1,  # 0=left, 1=center, 2=right
        fontSize=15,
        leading=18
    )

    # === LOGO ===
    if os.path.exists(logo_path):
        try:
            img = Image(logo_path, width=17 * cm, height=3.0 * cm)
            img.hAlign = "CENTER"
            elements.append(img)
            elements.append(Spacer(1, 14))
        except:
            pass

    # === TÍTULO ===
    titulo = Paragraph(
        "<b>FOLHA DE PAGAMENTO FUNCIONÁRIOS DA “EMEIEF CEL NOGUEIRA COBRA”</b><br/>"
        f"<font size=12>MÊS DE REFERÊNCIA: – De 01/{str(mes).zfill(2)} a {ultimo_dia}/{str(mes).zfill(2)} – {ano}</font>",
        titulo_style
    )
    elements.append(titulo)
    elements.append(Spacer(1, 20))

    # === DADOS DOS FUNCIONÁRIOS ===
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, rg, cargo, contrato, carga_horaria FROM funcionarios")
    funcionarios = cursor.fetchall()

    dados = []
    for func in funcionarios:
        func_id = func[0]
        cursor.execute("""
            SELECT data, justificativa FROM frequencia 
            WHERE funcionario_id = ? 
            AND substr(data, 4, 2) = ? AND substr(data, 7, 4) = ?
            ORDER BY data
        """, (func_id, str(mes).zfill(2), str(ano)))
        faltas = cursor.fetchall()

        if not faltas:
            obs = "FREQUENTE"
        else:
            obs_list = [f"{j} ({d[:2]}/{d[3:5]})" for d, j in faltas]
            obs = ", ".join(obs_list)

        dados.append({
            "nome": func[1],
            "rg": func[2],
            "cargo": func[3],
            "contrato": func[4],
            "carga_horaria": func[5],
            "observacoes": obs
        })
    conn.close()

    # === TABELA ===
    header = ["Nº", "Nome", "RG", "Cargo/Função", "Contrato", "Carga Horária", "Observações"]
    data = [header]
    for i, f in enumerate(dados, 1):
        data.append([
            str(i), f["nome"], f["rg"], f["cargo"], f["contrato"],
            f["carga_horaria"], f["observacoes"]
        ])

    # 🔧 COLUNAS REAJUSTADAS (margens equilibradas)
    col_widths = [1.2 * cm, 6.0 * cm, 3.0 * cm, 4.2 * cm, 3.0 * cm, 3.2 * cm, 8.2 * cm]

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f6aa5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 1), (-1, -1), 9.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 45))

    # === ASSINATURA ===
    assinatura = f"""
    Local e Data: __________,____ de _______________ de {ano}<br/><br/>
    _________________________________________________<br/>
    Assinatura do Diretor
    """
    elements.append(Paragraph(assinatura, styles["Normal"]))

    # === GERAR PDF ===
    doc.build(elements)

    try:
        os.startfile(output)
    except:
        print(f"PDF salvo em: {os.path.abspath(output)}")
