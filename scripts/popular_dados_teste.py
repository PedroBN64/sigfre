# scripts/popular_dados_teste.py
import sqlite3
import random
from datetime import datetime, timedelta
from database.db import conectar

def popular_funcionarios():
    """Popula a tabela de funcionários com 78 registros de teste alinhados com a classificação do PDF"""
    
    # Lista de nomes realistas
    nomes_masculinos = [
        "João Silva", "Pedro Santos", "Carlos Oliveira", "Antônio Costa", "Paulo Souza",
        "Lucas Fernandes", "Marcos Pereira", "Ricardo Almeida", "Fernando Lima", "Roberto Martins",
        "Daniel Rodrigues", "Eduardo Barbosa", "Miguel Carvalho", "Rafael Ferreira", "Bruno Rocha",
        "Fábio Nascimento", "Gustavo Mendes", "Leonardo Duarte", "Alexandre Moreira", "André Castro",
        "Sérgio Cardoso", "Maurício Neves", "Vinícius Ramos", "Diego Pinto", "Thiago Lopes",
        "Felipe Andrade", "Rodrigo Xavier", "Juliano Teixeira", "César Moura", "Márcio Freitas"
    ]
    
    nomes_femininos = [
        "Maria Oliveira", "Ana Santos", "Juliana Costa", "Patrícia Souza", "Camila Lima",
        "Fernanda Silva", "Amanda Pereira", "Letícia Rodrigues", "Beatriz Alves", "Gabriela Martins",
        "Carolina Ferreira", "Larissa Barbosa", "Mariana Carvalho", "Isabela Rocha", "Tatiane Nascimento",
        "Vanessa Mendes", "Priscila Duarte", "Jéssica Moreira", "Natália Castro", "Débora Cardoso",
        "Simone Neves", "Renata Ramos", "Cristina Pinto", "Elaine Lopes", "Sueli Andrade",
        "Luciana Xavier", "Monique Teixeira", "Viviane Moura", "Rosângela Freitas", "Adriana Santos",
        "Cláudia Oliveira", "Sandra Costa", "Regina Souza", "Lúcia Lima", "Tânia Silva",
        "Mônica Pereira", "Cíntia Rodrigues", "Rita Alves", "Alice Martins", "Helena Ferreira",
        "Laura Barbosa", "Valéria Carvalho", "Irene Rocha", "Noemi Nascimento", "Elisa Mendes"
    ]
    
    # Cargos específicos para cada grupo do PDF
    cargos_educacao_infantil = ["Professor Educação Infantil"]
    cargos_peb1 = [
        "Professor PEB I", 
        "Professor de Musica", 
        "Professor de ED. Física", 
        "Professor de Artes", 
        "Professor de Inglês"
    ]
    cargos_outros = [
        "Coordenador Pedagógico", "Diretor", "Vice-Diretor", "Secretário Escolar", 
        "Auxiliar Administrativo", "Merendeira", "Serviços Gerais", "Zelador", 
        "Monitor", "Bibliotecário", "Psicólogo Escolar", "Fonoaudiólogo"
    ]
    
    # Todos os cargos combinados
    todos_cargos = cargos_educacao_infantil + cargos_peb1 + cargos_outros
    
    # Tipos de contrato - distribuídos estrategicamente
    contratos_clt = ["CLT"]
    contratos_outros = ["Estatutário", "Temporário", "Estagiário"]
    
    # Cargas horárias
    cargas_horarias = ["20h", "30h", "40h", "44h"]
    
    conn = conectar()
    cursor = conn.cursor()
    
    # Limpar tabela existente
    cursor.execute("DELETE FROM funcionarios")
    
    funcionarios = []
    id_counter = 1
    
    # Distribuição estratégica para criar os 5 grupos do PDF
    total_funcionarios = len(nomes_masculinos) + len(nomes_femininos)
    
    # Grupo 1: EFETIVO CLT - Professor Educação Infantil (15%)
    num_grupo1 = int(total_funcionarios * 0.15)
    # Grupo 2: EFETIVO CLT - Professor PEB I (20%)
    num_grupo2 = int(total_funcionarios * 0.20)
    # Grupo 3: CONTRATO - Professor Educação Infantil (15%)
    num_grupo3 = int(total_funcionarios * 0.15)
    # Grupo 4: CONTRATO - Professor PEB I (20%)
    num_grupo4 = int(total_funcionarios * 0.20)
    # Grupo 5: Funcionários - outros cargos (30%)
    num_grupo5 = total_funcionarios - (num_grupo1 + num_grupo2 + num_grupo3 + num_grupo4)
    
    print("📊 DISTRIBUIÇÃO ESTRATÉGICA DE FUNCIONÁRIOS:")
    print(f"  • EFETIVO CLT - Professor Educação Infantil: {num_grupo1}")
    print(f"  • EFETIVO CLT - Professor PEB I: {num_grupo2}")
    print(f"  • CONTRATO - Professor Educação Infantil: {num_grupo3}")
    print(f"  • CONTRATO - Professor PEB I: {num_grupo4}")
    print(f"  • Funcionários (outros cargos): {num_grupo5}")
    
    # Combinar todos os nomes
    todos_nomes = nomes_masculinos + nomes_femininos
    random.shuffle(todos_nomes)
    
    # Grupo 1: EFETIVO CLT - Professor Educação Infantil
    for i in range(num_grupo1):
        if i < len(todos_nomes):
            nome = todos_nomes.pop(0)
            rg = f"MG-{random.randint(10000000, 99999999)}"
            cargo = random.choice(cargos_educacao_infantil)
            contrato = "CLT"
            carga_horaria = random.choice(cargas_horarias)
            
            funcionarios.append((id_counter, nome, rg, cargo, contrato, carga_horaria))
            id_counter += 1
    
    # Grupo 2: EFETIVO CLT - Professor PEB I
    for i in range(num_grupo2):
        if i < len(todos_nomes):
            nome = todos_nomes.pop(0)
            rg = f"MG-{random.randint(10000000, 99999999)}"
            cargo = random.choice(cargos_peb1)
            contrato = "CLT"
            carga_horaria = random.choice(cargas_horarias)
            
            funcionarios.append((id_counter, nome, rg, cargo, contrato, carga_horaria))
            id_counter += 1
    
    # Grupo 3: CONTRATO - Professor Educação Infantil
    for i in range(num_grupo3):
        if i < len(todos_nomes):
            nome = todos_nomes.pop(0)
            rg = f"MG-{random.randint(10000000, 99999999)}"
            cargo = random.choice(cargos_educacao_infantil)
            contrato = random.choice(contratos_outros)
            carga_horaria = random.choice(cargas_horarias)
            
            funcionarios.append((id_counter, nome, rg, cargo, contrato, carga_horaria))
            id_counter += 1
    
    # Grupo 4: CONTRATO - Professor PEB I
    for i in range(num_grupo4):
        if i < len(todos_nomes):
            nome = todos_nomes.pop(0)
            rg = f"MG-{random.randint(10000000, 99999999)}"
            cargo = random.choice(cargos_peb1)
            contrato = random.choice(contratos_outros)
            carga_horaria = random.choice(cargas_horarias)
            
            funcionarios.append((id_counter, nome, rg, cargo, contrato, carga_horaria))
            id_counter += 1
    
    # Grupo 5: Funcionários - outros cargos
    for i in range(num_grupo5):
        if i < len(todos_nomes):
            nome = todos_nomes.pop(0)
            rg = f"MG-{random.randint(10000000, 99999999)}"
            cargo = random.choice(cargos_outros)
            contrato = random.choice(contratos_clt + contratos_outros)  # Pode ser qualquer contrato
            carga_horaria = random.choice(cargas_horarias)
            
            funcionarios.append((id_counter, nome, rg, cargo, contrato, carga_horaria))
            id_counter += 1
    
    # Inserir no banco
    cursor.executemany(
        "INSERT INTO funcionarios (id, nome, rg, cargo, contrato, carga_horaria) VALUES (?, ?, ?, ?, ?, ?)",
        funcionarios
    )
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(funcionarios)} funcionários inseridos com sucesso!")
    
    # Mostrar distribuição real
    print("\n📈 DISTRIBUIÇÃO REAL CRIADA:")
    conn = conectar()
    cursor = conn.cursor()
    
    # Contar por grupo
    cursor.execute("""
        SELECT 
            CASE 
                WHEN cargo = 'Professor Educação Infantil' AND contrato = 'CLT' THEN 'EFETIVO CLT - Professor Educação Infantil'
                WHEN cargo IN ('Professor PEB I', 'Professor de Musica', 'Professor de ED. Física', 'Professor de Artes', 'Professor de Inglês') AND contrato = 'CLT' THEN 'EFETIVO CLT - Professor PEB I'
                WHEN cargo = 'Professor Educação Infantil' AND contrato != 'CLT' THEN 'CONTRATO - Professor Educação Infantil'
                WHEN cargo IN ('Professor PEB I', 'Professor de Musica', 'Professor de ED. Física', 'Professor de Artes', 'Professor de Inglês') AND contrato != 'CLT' THEN 'CONTRATO - Professor PEB I'
                ELSE 'Funcionários'
            END as grupo,
            COUNT(*) as quantidade
        FROM funcionarios 
        GROUP BY grupo
        ORDER BY grupo
    """)
    
    distribuicao_real = cursor.fetchall()
    for grupo, quantidade in distribuicao_real:
        print(f"  • {grupo}: {quantidade}")
    
    conn.close()
    
    return [f[0] for f in funcionarios]  # Retorna lista de IDs

def popular_faltas(funcionario_ids, mes=8, ano=2024):
    """Popula a tabela de frequência com faltas variadas"""
    
    # Justificativas disponíveis
    justificativas = ["AM", "AB", "TRE", "SOL", "INJ", "FH", "Folga Aniversário", "Atestado", "Falta Justificada", "Licença-Prêmio"]
    
    conn = conectar()
    cursor = conn.cursor()
    
    # Limpar tabela existente (opcional)
    cursor.execute("DELETE FROM frequencia")
    
    # Verificar se coluna detalhes existe
    try:
        cursor.execute("PRAGMA table_info(frequencia)")
        colunas = [col[1] for col in cursor.fetchall()]
        if 'detalhes' not in colunas:
            cursor.execute("ALTER TABLE frequencia ADD COLUMN detalhes TEXT")
    except:
        pass
    
    total_faltas = 0
    ultimo_dia = 31 if mes in [1, 3, 5, 7, 8, 10, 12] else 30
    
    for func_id in funcionario_ids:
        # Definir probabilidade de ter faltas (80% dos funcionários terão faltas)
        if random.random() > 0.2:
            # Número de faltas para este funcionário (1 a 8 faltas)
            num_faltas = random.randint(1, 8)
            
            dias_com_falta = random.sample(range(1, ultimo_dia + 1), num_faltas)
            
            for dia in dias_com_falta:
                data = f"{dia:02d}/{mes:02d}/{ano}"
                justificativa = random.choice(justificativas)
                detalhes = None
                
                # Adicionar detalhes específicos para algumas justificativas
                if justificativa == "FH":
                    # Gerar horas de falta
                    horas = random.choice([1, 2, 3, 4])
                    minutos = random.choice([0, 15, 30, 45])
                    if minutos > 0:
                        detalhes = f"{horas}h{minutos}min"
                    else:
                        detalhes = f"{horas}h"
                
                elif justificativa == "Licença-Prêmio":
                    # Licença de 3 a 10 dias
                    duracao = random.randint(3, 10)
                    data_inicio = datetime(ano, mes, dia)
                    data_fim = data_inicio + timedelta(days=duracao-1)
                    detalhes = f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
                    # Para licença, marcar apenas o primeiro dia
                
                elif justificativa == "Folga Aniversário":
                    # Folga no dia do aniversário (gerar data aleatória no mês)
                    dia_aniversario = random.randint(1, ultimo_dia)
                    data = f"{dia_aniversario:02d}/{mes:02d}/{ano}"
                
                # Inserir falta
                cursor.execute(
                    "INSERT INTO frequencia (funcionario_id, data, justificativa, detalhes) VALUES (?, ?, ?, ?)",
                    (func_id, data, justificativa, detalhes)
                )
                total_faltas += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ {total_faltas} faltas inseridas com sucesso!")

def popular_justificativas_personalizadas():
    """Popula justificativas personalizadas no banco"""
    justificativas_personalizadas = [
        "Curso de Capacitação", "Viagem a Serviço", "Problemas Familiares", 
        "Consulta Médica", "Exames", "Doação de Sangue", "Casamento",
        "Nascimento de Filho", "Falecimento Familiar", "Acompanhamento Familiar"
    ]
    
    conn = conectar()
    cursor = conn.cursor()
    
    # Criar tabela se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS justificativas_personalizadas (
            id INTEGER PRIMARY KEY,
            nome TEXT UNIQUE
        )
    """)
    
    # Limpar e popular
    cursor.execute("DELETE FROM justificativas_personalizadas")
    
    for i, justificativa in enumerate(justificativas_personalizadas, 1):
        cursor.execute(
            "INSERT OR IGNORE INTO justificativas_personalizadas (id, nome) VALUES (?, ?)",
            (i, justificativa)
        )
    
    conn.commit()
    conn.close()
    
    print(f"✅ {len(justificativas_personalizadas)} justificativas personalizadas inseridas!")

def gerar_relatorio_estatisticas():
    """Gera um relatório com estatísticas dos dados inseridos"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Estatísticas de funcionários
    cursor.execute("SELECT COUNT(*) FROM funcionarios")
    total_funcionarios = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT cargo) FROM funcionarios")
    total_cargos = cursor.fetchone()[0]
    
    # Estatísticas de faltas
    cursor.execute("SELECT COUNT(*) FROM frequencia")
    total_faltas = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT funcionario_id) FROM frequencia")
    funcionarios_com_falta = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT justificativa, COUNT(*) as quantidade 
        FROM frequencia 
        GROUP BY justificativa 
        ORDER BY quantidade DESC
    """)
    distribuicao_justificativas = cursor.fetchall()
    
    # Distribuição por grupos do PDF
    cursor.execute("""
        SELECT 
            CASE 
                WHEN cargo = 'Professor Educação Infantil' AND contrato = 'CLT' THEN 'EFETIVO CLT - Professor Educação Infantil'
                WHEN cargo IN ('Professor PEB I', 'Professor de Musica', 'Professor de ED. Física', 'Professor de Artes', 'Professor de Inglês') AND contrato = 'CLT' THEN 'EFETIVO CLT - Professor PEB I'
                WHEN cargo = 'Professor Educação Infantil' AND contrato != 'CLT' THEN 'CONTRATO - Professor Educação Infantil'
                WHEN cargo IN ('Professor PEB I', 'Professor de Musica', 'Professor de ED. Física', 'Professor de Artes', 'Professor de Inglês') AND contrato != 'CLT' THEN 'CONTRATO - Professor PEB I'
                ELSE 'Funcionários'
            END as grupo,
            COUNT(*) as quantidade
        FROM funcionarios 
        GROUP BY grupo
        ORDER BY grupo
    """)
    distribuicao_grupos = cursor.fetchall()
    
    conn.close()
    
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE ESTATÍSTICAS - DADOS DE TESTE")
    print("="*60)
    print(f"👥 Total de funcionários: {total_funcionarios}")
    print(f"💼 Cargos distintos: {total_cargos}")
    print(f"📅 Total de faltas registradas: {total_faltas}")
    print(f"🎯 Funcionários com faltas: {funcionarios_com_falta}")
    print(f"📈 Média de faltas por funcionário: {total_faltas/total_funcionarios:.1f}")
    
    print("\n🏷️  Distribuição por grupos do PDF:")
    for grupo, quantidade in distribuicao_grupos:
        percentual = (quantidade / total_funcionarios) * 100
        print(f"   • {grupo}: {quantidade} ({percentual:.1f}%)")
    
    print("\n📋 Distribuição de justificativas:")
    for justificativa, quantidade in distribuicao_justificativas:
        percentual = (quantidade / total_faltas) * 100
        print(f"   • {justificativa}: {quantidade} ({percentual:.1f}%)")
    print("="*60)

def executar_populacao_completa():
    """Executa toda a população de dados de teste"""
    print("🚀 INICIANDO POPULAÇÃO DE DADOS DE TESTE...")
    print()
    
    # 1. Popular funcionários
    print("1. Populando tabela de funcionários...")
    funcionario_ids = popular_funcionarios()
    
    # 2. Popular justificativas personalizadas
    print("\n2. Populando justificativas personalizadas...")
    popular_justificativas_personalizadas()
    
    # 3. Popular faltas
    print("\n3. Populando tabela de frequência...")
    popular_faltas(funcionario_ids)
    
    # 4. Gerar relatório
    print("\n4. Gerando relatório estatístico...")
    gerar_relatorio_estatisticas()
    
    print("\n🎉 POPULAÇÃO CONCLUÍDA COM SUCESSO!")
    print("📄 Agora você pode gerar o PDF para testar com dados realistas.")

# Para executar diretamente
if __name__ == "__main__":
    executar_populacao_completa()