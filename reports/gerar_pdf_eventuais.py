# reports/gerar_pdf_eventuais.py
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
    """Valida mês e ano"""
    try:
        mes, ano = int(mes), int(ano)
        if not (1 <= mes <= 12 and 2020 <= ano <= 2030):
            return False, None, None, None
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        return True, mes, ano, ultimo_dia
    except:
        return False, None, None, None

def obter_dados_professores_eventuais(mes, ano):
    """Obtém dados dos professores eventuais e suas aulas do mês"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Buscar professores eventuais com aulas no mês
    cursor.execute('''
        SELECT 
            pe.id,
            pe.nome,
            SUM(ae.quantidade_aulas) as total_aulas
        FROM professores_eventuais pe
        INNER JOIN aulas_eventuais ae ON pe.id = ae.professor_eventual_id
        WHERE substr(ae.data_aula, 4, 2) = ? AND substr(ae.data_aula, 7, 4) = ?
        GROUP BY pe.id, pe.nome
        HAVING total_aulas > 0
        ORDER BY pe.nome
    ''', (f"{mes:02d}", str(ano)))
    
    professores = cursor.fetchall()
    
    # Para cada professor, buscar detalhes das aulas
    dados_professores = []
    for professor in professores:
        professor_id, nome, total_aulas = professor
        
        # Buscar aulas detalhadas do professor
        cursor.execute('''
            SELECT 
                professor_substituido,
                data_aula,
                turmas,
                quantidade_aulas,
                observacoes
            FROM aulas_eventuais 
            WHERE professor_eventual_id = ?
            AND substr(data_aula, 4, 2) = ? AND substr(data_aula, 7, 4) = ?
            ORDER BY data_aula
        ''', (professor_id, f"{mes:02d}", str(ano)))
        
        aulas = cursor.fetchall()
        
        dados_professores.append({
            'id': professor_id,
            'nome': nome,
            'total_aulas': total_aulas,
            'aulas': aulas
        })
    
    conn.close()
    return dados_professores

def formatar_data_abreviada(data):
    """Formata data para DD/MM"""
    try:
        return f"{data[:2]}/{data[3:5]}"
    except:
        return data

def gerar_relatorio_eventuais_pdf(mes, ano, logo_path="assets/timbrado.png", output_dir="relatorios_eventuais"):
    """Gera PDF com relatório de professores eventuais"""
    
    valido, mes, ano, ultimo_dia = validar_mes_ano(mes, ano)
    if not valido:
        from CTkMessagebox import CTkMessagebox
        CTkMessagebox(title="Erro", message="Mês ou ano inválido!", icon="cancel")
        return

    # Criar diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Obter dados dos professores
    dados_professores = obter_dados_professores_eventuais(mes, ano)
    
    if not dados_professores:
        from CTkMessagebox import CTkMessagebox
        CTkMessagebox(title="Aviso", message="Nenhum dado encontrado para o período selecionado!", icon="warning")
        return
    
    # Nome do arquivo
    mes_nome = [
        "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
        "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
    ][mes - 1]
    
    nome_arquivo = f"Relatorio_Professores_Eventuais_{mes:02d}_{ano}.pdf"
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
    
    periodo_style = ParagraphStyle(
        "PeriodoStyle",
        parent=styles["Heading2"],
        alignment=1,
        fontSize=12,
        textColor=colors.darkblue,
        spaceAfter=12
    )
    
    # Estilo para células
    celula_style = ParagraphStyle(
        "CelulaStyle", 
        parent=styles["Normal"],
        fontSize=8,
        leading=9,
        alignment=1,
    )
    
    celula_esquerda_style = ParagraphStyle(
        "CelulaEsquerdaStyle", 
        parent=styles["Normal"],
        fontSize=8,
        leading=9,
        alignment=0,
    )
    
    celula_total_style = ParagraphStyle(
        "CelulaTotalStyle", 
        parent=styles["Normal"],
        fontSize=9,
        leading=10,
        alignment=1,
        textColor=colors.white,
        fontName="Helvetica-Bold"
    )
    
    celula_total_nome_style = ParagraphStyle(
        "CelulaTotalNomeStyle", 
        parent=styles["Normal"],
        fontSize=9,
        leading=10,
        alignment=0,
        textColor=colors.white,
        fontName="Helvetica-Bold"
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
    titulo = Paragraph(
        f"<b>RELATÓRIO DE AULAS - PROFESSORES EVENTUAIS</b>",
        titulo_style
    )
    elements.append(titulo)
    
    # === PERÍODO ===
    periodo = Paragraph(
        f"<b>MÊS DE REFERÊNCIA: {mes_nome} {ano}</b>",
        periodo_style
    )
    elements.append(periodo)
    elements.append(Spacer(1, 15))

    # === CONSTRUIR TABELA ÚNICA ===
    # NOVA ORDEM DAS COLUNAS: Professor Eventual, Professor Substituído, Data, Turmas, Aulas
    header = ["Professor Eventual", "Professor Substituído", "Data", "Turmas", "Aulas"]
    data = [header]
    
    total_geral_aulas = 0
    linhas_totais = []  # Para armazenar os índices das linhas de total
    
    for professor in dados_professores:
        professor_nome = professor['nome']
        total_professor = 0
        primeira_linha = True
        
        # Adicionar cada aula do professor
        for aula in professor['aulas']:
            prof_substituido, data_aula, turmas, qtd_aulas, observacoes = aula
            total_professor += qtd_aulas
            
            # Na primeira linha, mostrar o nome do professor
            if primeira_linha:
                linha = [
                    Paragraph(professor_nome, celula_esquerda_style),
                    Paragraph(prof_substituido, celula_esquerda_style),
                    Paragraph(formatar_data_abreviada(data_aula), celula_style),
                    Paragraph(turmas, celula_esquerda_style),
                    Paragraph(str(qtd_aulas), celula_style)
                ]
                primeira_linha = False
            else:
                # Nas demais linhas, deixar o nome do professor em branco
                linha = [
                    Paragraph("", celula_esquerda_style),
                    Paragraph(prof_substituido, celula_esquerda_style),
                    Paragraph(formatar_data_abreviada(data_aula), celula_style),
                    Paragraph(turmas, celula_esquerda_style),
                    Paragraph(str(qtd_aulas), celula_style)
                ]
            
            data.append(linha)
        
        # Adicionar linha de TOTAL para este professor
        linha_total = [
            Paragraph(f"<b>{professor_nome}</b>", celula_total_nome_style),
            Paragraph("", celula_esquerda_style),
            Paragraph("", celula_style),
            Paragraph("<b>TOTAL</b>", celula_total_nome_style),
            Paragraph(f"<b>{total_professor}</b>", celula_total_style)
        ]
        data.append(linha_total)
        
        # Armazenar a linha de total para aplicar o estilo depois
        linhas_totais.append(len(data) - 1)
        
        total_geral_aulas += total_professor

    # === CRIAR TABELA ===
    # Ajustar larguras das colunas para nova ordem
    col_widths = [6.0 * cm, 6.0 * cm, 1.5 * cm, 4.0 * cm, 1.5 * cm]
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Estilo da tabela
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
        
        # Alinhamento específico por coluna (nova ordem)
        ("ALIGN", (0, 1), (0, -1), "LEFT"),    # Professor Eventual
        ("ALIGN", (1, 1), (1, -1), "LEFT"),    # Professor Substituído
        ("ALIGN", (2, 1), (2, -1), "CENTER"),  # Data
        ("ALIGN", (3, 1), (3, -1), "LEFT"),    # Turmas
        ("ALIGN", (4, 1), (4, -1), "CENTER"),  # Aulas
    ])
    
    # Aplicar background azul para todas as linhas de total
    for linha_total in linhas_totais:
        table_style.add('BACKGROUND', (0, linha_total), (-1, linha_total), colors.HexColor("#78b8e3"))
        table_style.add('TEXTCOLOR', (0, linha_total), (-1, linha_total), colors.white)
        table_style.add('FONTNAME', (0, linha_total), (-1, linha_total), "Helvetica-Bold")
    
    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 20))

    # === RESUMO GERAL MELHORADO ===
    total_professores = len(dados_professores)
    resumo_texto = f"""
    <b>RESUMO GERAL - {mes_nome} {ano}</b><br/>
    <b>Total de Professores Eventuais:</b> {total_professores}<br/>
    <b>Total de Aulas Ministradas:</b> {total_geral_aulas}
    """
    
    resumo = Paragraph(
        resumo_texto,
        ParagraphStyle(
            "ResumoStyle",
            parent=styles["Normal"],
            fontSize=11,
            alignment=1,
            textColor=colors.darkblue,
            spaceBefore=15,
            spaceAfter=25,
            borderPadding=10,
            backColor=colors.HexColor("#f8f9fa")
        )
    )
    elements.append(resumo)

    # === ASSINATURA ===
    data_atual = datetime.now()
    assinatura = Paragraph(
        f"Local e Data: BANANAL, {data_atual.day} de {mes_nome.lower()} de {data_atual.year}<br/><br/>"
        "_________________________________________________________<br/>"
        "<b>Assinatura do Diretor</b>",
        ParagraphStyle(
            "AssinaturaStyle",
            parent=styles["Normal"],
            fontSize=10,
            alignment=1,
            spaceBefore=30
        )
    )
    elements.append(assinatura)

    # === RODAPÉ COM INFORMAÇÕES ADICIONAIS ===
    rodape = Paragraph(
        f"<i>Relatório gerado automaticamente em {data_atual.strftime('%d/%m/%Y às %H:%M')}</i>",
        ParagraphStyle(
            "RodapeStyle",
            parent=styles["Normal"],
            fontSize=7,
            alignment=2,
            textColor=colors.gray,
            spaceBefore=10
        )
    )
    elements.append(rodape)

    # === GERAR PDF ===
    try:
        doc.build(elements)
        print(f"✅ PDF gerado: {nome_arquivo}")
        
        # Abrir o PDF automaticamente
        try:
            os.startfile(output_path)
        except:
            import subprocess
            try:
                subprocess.run(['xdg-open', output_path], check=False)
            except:
                print(f"📄 PDF disponível em: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        from CTkMessagebox import CTkMessagebox
        CTkMessagebox(title="Erro", message=f"Erro ao gerar PDF:\n{e}", icon="cancel")
        return None

# Função para integração com a interface
def gerar_relatorio_eventuais(mes, ano):
    """Função principal para gerar relatório de professores eventuais"""
    return gerar_relatorio_eventuais_pdf(mes, ano)