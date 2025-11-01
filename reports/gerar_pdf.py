# reports/gerar_pdf.py
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import os
import calendar
from database.db import conectar
from datetime import datetime

def validar_mes_ano(mes, ano):
    try:
        mes, ano = int(mes), int(ano)
        if not (1 <= mes <= 12 and 2020 <= ano <= 2030):
            return False, None, None, None
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        return True, mes, ano, ultimo_dia
    except:
        return False, None, None, None

def formatar_justificativa(data, justificativa, detalhes):
    """Formata a justificativa de forma inteligente"""
    data_formatada = f"{data[:2]}/{data[3:5]}"
    
    if justificativa == "Licença-Prêmio" and detalhes:
        return f"Licença-Prêmio ({detalhes})"
    
    elif justificativa == "FH" and detalhes:
        return f"FH ({data_formatada} - {detalhes})"
    
    elif justificativa in ["AM", "AB", "SOL", "INJ"]:
        return f"{justificativa} ({data_formatada})"
    
    elif justificativa == "TRE":
        return f"TRE ({data_formatada})"
    
    elif justificativa == "Folga Aniversário":
        return f"Folga Aniv. ({data_formatada})"
    
    elif justificativa == "Atestado":
        return f"Atestado ({data_formatada})"
    
    elif justificativa == "Falta Justificada":
        return f"Falta Justif. ({data_formatada})"
    
    else:
        if detalhes:
            return f"{justificativa} ({data_formatada} - {detalhes})"
        else:
            return f"{justificativa} ({data_formatada})"

def classificar_funcionarios(funcionarios):
    """Classifica os funcionários nos grupos especificados"""
    
    # Professores PEB I
    cargos_peb1 = [
        "Professor PEB I", "Professor de Musica", "Professor de ED. Física", 
        "Professor de Artes", "Professor de Inglês"
    ]
    
    grupos = {
        "EFETIVO CLT - Professor Educação Infantil": [],
        "EFETIVO CLT - Professor PEB I": [],
        "CONTRATO - Professor Educação Infantil": [],
        "CONTRATO - Professor PEB I": [],
        "Funcionários": []
    }
    
    for func in funcionarios:
        id_func, nome, rg, cargo, contrato, carga_horaria = func
        
        # Verificar se é professor de Educação Infantil
        if "Educação Infantil" in cargo:
            if contrato == "CLT":
                grupos["EFETIVO CLT - Professor Educação Infantil"].append(func)
            else:
                grupos["CONTRATO - Professor Educação Infantil"].append(func)
        
        # Verificar se é professor PEB I
        elif any(cargo_peb in cargo for cargo_peb in cargos_peb1):
            if contrato == "CLT":
                grupos["EFETIVO CLT - Professor PEB I"].append(func)
            else:
                grupos["CONTRATO - Professor PEB I"].append(func)
        
        # Outros funcionários (não professores)
        else:
            grupos["Funcionários"].append(func)
    
    return grupos

def gerar_grupo_pdf(grupo_nome, funcionarios_grupo, mes, ano, logo_path, output_dir):
    """Gera PDF para um grupo específico"""
    
    if not funcionarios_grupo:
        print(f"⚠️  Nenhum funcionário no grupo: {grupo_nome}")
        return None
    
    # Nome do arquivo baseado no grupo
    nome_arquivo = f"{grupo_nome.replace(' ', '_').replace('-', '_')}_{mes:02d}_{ano}.pdf"
    output_path = os.path.join(output_dir, nome_arquivo)
    
    # Configuração do documento
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2.0 * cm,
        bottomMargin=1.8 * cm
    )
    elements = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    titulo_style = ParagraphStyle(
        "TituloCentralizado",
        parent=styles["Title"],
        alignment=1,
        fontSize=14,
        leading=16,
        spaceAfter=8
    )
    
    grupo_style = ParagraphStyle(
        "GrupoStyle",
        parent=styles["Heading2"],
        alignment=1,
        fontSize=12,
        textColor=colors.darkblue,
        spaceAfter=12
    )
    
    # Estilo para células de observação
    obs_style = ParagraphStyle(
        "ObservacaoStyle",
        parent=styles["Normal"],
        fontSize=7,
        leading=8.5,
        alignment=0,
        wordWrap='LTR',
    )
    
    # Estilo para células normais
    celula_style = ParagraphStyle(
        "CelulaStyle", 
        parent=styles["Normal"],
        fontSize=8,
        leading=9,
        alignment=1,
    )

    # === LOGO ===
    if os.path.exists(logo_path):
        try:
            img = Image(logo_path, width=16 * cm, height=2.8 * cm)
            img.hAlign = "CENTER"
            elements.append(img)
            elements.append(Spacer(1, 10))
        except:
            pass

    # === TÍTULO PRINCIPAL ===
    mes_nome = [
        "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
        "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
    ][mes - 1]
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    
    titulo = Paragraph(
        f"<b>FOLHA DE PAGAMENTO - FUNCIONÁRIOS DA EMEIEF CEL NOGUEIRA COBRA</b>",
        titulo_style
    )
    elements.append(titulo)
    
    # === IDENTIFICAÇÃO DO GRUPO ===
    grupo_identificacao = Paragraph(
        f"<b>{grupo_nome.upper()}</b><br/>"
        f"<font size=11>MÊS DE REFERÊNCIA: 01/{str(mes).zfill(2)} a {ultimo_dia}/{str(mes).zfill(2)}/{ano} - {mes_nome}</font>",
        grupo_style
    )
    elements.append(grupo_identificacao)
    elements.append(Spacer(1, 15))

    # === DADOS DOS FUNCIONÁRIOS DO GRUPO ===
    conn = conectar()
    cursor = conn.cursor()
    
    dados = []
    for func in funcionarios_grupo:
        func_id = func[0]
        
        # Buscar faltas com detalhes
        cursor.execute("""
            SELECT data, justificativa, detalhes FROM frequencia 
            WHERE funcionario_id = ? 
            AND substr(data, 4, 2) = ? AND substr(data, 7, 4) = ?
            ORDER BY data
        """, (func_id, str(mes).zfill(2), str(ano)))
        faltas = cursor.fetchall()

        # Processar e agrupar justificativas
        justificativas_formatadas = []
        for data, justificativa, detalhes in faltas:
            just_formatada = formatar_justificativa(data, justificativa, detalhes)
            justificativas_formatadas.append(just_formatada)

        # Juntar todas as justificativas em uma string com quebras de linha
        if justificativas_formatadas:
            texto_observacoes = "<br/>".join(justificativas_formatadas)
        else:
            texto_observacoes = "FREQUENTE"

        dados.append({
            "nome": func[1] or "",
            "rg": func[2] or "",
            "cargo": func[3] or "",
            "contrato": func[4] or "",
            "carga_horaria": func[5] or "",
            "observacoes": texto_observacoes
        })
    conn.close()

    # === TABELA PRINCIPAL ===
    header = ["Nº", "Nome", "RG", "Cargo/Função", "Contrato", "Carga Horária", "Observações"]
    data = [header]
    
    for i, f in enumerate(dados, 1):
        # Usar Paragraph para permitir quebra de linha automática
        linha = [
            Paragraph(str(i), celula_style),
            Paragraph(f["nome"], celula_style),
            Paragraph(f["rg"], celula_style),
            Paragraph(f["cargo"], celula_style),
            Paragraph(f["contrato"], celula_style),
            Paragraph(f["carga_horaria"], celula_style),
            Paragraph(f["observacoes"], obs_style)
        ]
        data.append(linha)

    # Larguras das colunas otimizadas
    col_widths = [1.0 * cm, 5.5 * cm, 2.8 * cm, 4.0 * cm, 2.8 * cm, 2.8 * cm, 7.5 * cm]

    # Criar tabela
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Estilo da tabela com altura automática
    table_style = TableStyle([
        # Cabeçalho
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b5797")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        
        # Dados
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        
        # Alinhamento específico por coluna
        ("ALIGN", (0, 1), (0, -1), "CENTER"),
        ("ALIGN", (1, 1), (1, -1), "LEFT"),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
        ("ALIGN", (3, 1), (3, -1), "CENTER"),
        ("ALIGN", (4, 1), (4, -1), "CENTER"),
        ("ALIGN", (5, 1), (5, -1), "CENTER"),
        ("ALIGN", (6, 1), (6, -1), "LEFT"),
    ])
    
    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 20))

    # === LEGENDA DE ABREVIAÇÕES ===
    legenda_texto = """
    <b>LEGENDA:</b> AM (Atestado Médico), AB (Abono), TRE (Folga de Eleição), SOL (Solicitação), 
    INJ (Injustificada), FH (Falta Horas), Folga Aniv. (Folga Aniversário), Falta Justif. (Falta Justificada)
    """
    legenda = Paragraph(legenda_texto, ParagraphStyle(
        "LegendaStyle",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        alignment=0,
        textColor=colors.gray
    ))
    elements.append(legenda)
    elements.append(Spacer(1, 15))

    # === ASSINATURA ===
    data_atual = datetime.now()
    assinatura = Paragraph(
        f"Local e Data: __________, {data_atual.day} de {mes_nome.lower()} de {data_atual.year}<br/><br/>"
        "_________________________________________________________<br/>"
        "<b>Assinatura do Diretor</b>",
        ParagraphStyle(
            "AssinaturaStyle",
            parent=styles["Normal"],
            fontSize=10,
            alignment=1,
            spaceBefore=20
        )
    )
    elements.append(assinatura)

    # === GERAR PDF DO GRUPO ===
    try:
        doc.build(elements)
        print(f"✅ PDF gerado: {nome_arquivo}")
        return output_path
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF para {grupo_nome}: {e}")
        return None

def gerar_folha_por_grupo(mes, ano, logo_path="assets/timbrado.png", output_dir="relatorios"):
    """Gera PDFs separados por grupos de funcionários"""
    
    valido, mes, ano, ultimo_dia = validar_mes_ano(mes, ano)
    if not valido:
        from CTkMessagebox import CTkMessagebox
        CTkMessagebox(title="Erro", message="Mês ou ano inválido!", icon="cancel")
        return

    # Criar diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Buscar todos os funcionários
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, rg, cargo, contrato, carga_horaria FROM funcionarios ORDER BY nome")
    funcionarios = cursor.fetchall()
    conn.close()
    
    if not funcionarios:
        print("❌ Nenhum funcionário encontrado no banco de dados!")
        return
    
    # Classificar funcionários nos grupos
    grupos = classificar_funcionarios(funcionarios)
    
    print(f"📊 CLASSIFICANDO {len(funcionarios)} FUNCIONÁRIOS EM GRUPOS:")
    print("=" * 60)
    
    # Gerar PDF para cada grupo
    pdfs_gerados = []
    for grupo_nome, funcionarios_grupo in grupos.items():
        print(f"📁 {grupo_nome}: {len(funcionarios_grupo)} funcionários")
        pdf_path = gerar_grupo_pdf(grupo_nome, funcionarios_grupo, mes, ano, logo_path, output_dir)
        if pdf_path:
            pdfs_gerados.append(pdf_path)
    
    print("=" * 60)
    print(f"🎉 GERADOS {len(pdfs_gerados)} PDFs EM: {os.path.abspath(output_dir)}")
    
    # Abrir o primeiro PDF gerado
    if pdfs_gerados:
        try:
            os.startfile(pdfs_gerados[0])
        except:
            import subprocess
            try:
                subprocess.run(['xdg-open', pdfs_gerados[0]], check=False)
            except:
                print(f"📄 PDFs disponíveis em: {output_dir}")

# Função original mantida para compatibilidade
def gerar_folha(mes, ano, logo_path="assets/timbrado.png", output="folha.pdf"):
    """Função original - gera um único PDF com todos os funcionários"""
    gerar_folha_por_grupo(mes, ano, logo_path, "relatorios")