# scripts/executar_teste.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.popular_dados_teste import executar_populacao_completa

if __name__ == "__main__":
    executar_populacao_completa()
    
    # Perguntar se quer gerar o PDF
    resposta = input("\n📄 Deseja gerar o PDF agora? (s/n): ")
    if resposta.lower() == 's':
        from reports.gerar_pdf import gerar_folha
        print("\n🔄 Gerando PDF...")
        gerar_folha(8, 2024, output="folha_teste_78_funcionarios.pdf")
        print("✅ PDF gerado com sucesso!")