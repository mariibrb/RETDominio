import streamlit as st
import pandas as pd
import io
import re

def process_dominio_ret(file):
    # Lendo o arquivo cru (convertendo bytes para string)
    string_data = file.getvalue().decode("utf-8")
    lines = string_data.split('\n')
    
    processed_lines = []
    current_percent = None
    
    # Cabeçalhos identificados na aba Python
    header_cols = [
        "Data", "Documento", "Col3", "Col4", "Col5", "Acumulador", 
        "Documento-Produto", "Percentual_Rec", "CFOP", "Col10", 
        "Produto", "Col12", "Tipo_Produto", "Col14", "Valor_Produto", 
        "Valor_Contabil", "Base_Calculo", "Isentas", "Col19", "Col20", 
        "Col21", "Valor_ICMS"
    ]

    for line in lines:
        parts = line.split(',')
        # Limpeza básica de espaços
        parts = [p.strip() for p in parts]
        
        # 1. Identifica e captura o Percentual de recolhimento atual
        if "Percentual de recolhimento efetivo:" in line:
            # Tenta encontrar o número (1.3, 6.0, 14.0, etc)
            match = re.search(r"(\d+\.?\d*)", line)
            if match:
                current_percent = match.group(1)
            processed_lines.append(line) # Mantém a linha original conforme aba Python
            continue

        # 2. Processa linhas de dados (que começam com data/número e tem CFOP na posição 9/10)
        # Verificando se a linha parece ser de um produto (ex: começa com 46024.0)
        try:
            if parts[0] and float(parts[0]) > 40000 and len(parts) > 10:
                doc = parts[1]
                prod_desc = parts[10]
                
                # Criando o ID: Documento-Produto (Coluna G/6)
                parts[6] = f"{doc}-{prod_desc}"
                
                # Inserindo o Percentual na Coluna H/7
                parts[7] = current_percent if current_percent else ""
                
                processed_lines.append(",".join(parts))
                continue
        except (ValueError, IndexError):
            pass

        # 3. Tratamento especial para linhas de Total ou Cabeçalhos repetidos
        if "Total:" in line or "DÉBITOS PELAS SAÍDAS" in line:
            # Na aba Python, as linhas de Total também ganham o marcador '-' e o percentual
            if len(parts) > 7:
                parts[5] = "-"
                parts[7] = current_percent if current_percent else ""
            processed_lines.append(",".join(parts))
        else:
            # Mantém as outras linhas (Cabeçalhos, Resumos de Apuração) como estão
            processed_lines.append(line)

    return "\n".join(processed_lines)

# Interface Streamlit
st.set_page_config(page_title="Conversor RET Domínio", layout="wide")

st.title("📂 Conversor Relatório RET - Domínio Sistemas")
st.markdown("""
Este conversor automatiza a preparação do relatório de Crédito Presumido para análise em Python.
* **Adiciona ID único:** `Documento-Produto`
* **Replica o Percentual:** Em todas as linhas de itens.
* **Preserva a estrutura:** Mantém os blocos de apuração fiscal.
""")

uploaded_file = st.file_uploader("Arraste o arquivo .csv extraído da Domínio aqui", type=["csv"])

if uploaded_file is not None:
    try:
        # Processamento
        result_csv = process_dominio_ret(uploaded_file)
        
        st.success("Arquivo processado com sucesso!")
        
        # Botão de Download
        st.download_button(
            label="📥 Baixar Arquivo para Python",
            data=result_csv,
            file_name=f"PROCESSADO_{uploaded_file.name}",
            mime="text/csv",
        )
        
        # Visualização prévia (Primeiras 50 linhas para conferência visual)
        with st.expander("Visualizar prévia dos dados processados"):
            st.text(result_csv[:5000]) # Mostra o início do arquivo

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

st.divider()
st.info("💡 Dica: O arquivo gerado segue rigorosamente o padrão de IDs e repetição de percentuais que você aprovou.")
