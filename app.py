import streamlit as st
import pandas as pd
import io
import re

def processar_ret_dominio(file):
    # Lendo o conteúdo bruto do arquivo para ignorar o bloqueio de "MIME type"
    bytes_data = file.getvalue()
    
    # Tenta decodificar (Dominio costuma usar latin-1 ou utf-8)
    try:
        content = bytes_data.decode('utf-8')
    except:
        content = bytes_data.decode('latin-1')
        
    lines = content.split('\n')
    processed_rows = []
    current_percent = ""

    for line in lines:
        # Divide por vírgula (padrão do CSV da Domínio)
        parts = line.split(',')
        parts = [p.strip() for p in parts]
        line_str = " ".join(parts)

        # 1. Captura o Percentual de Recolhimento
        if "Percentual de recolhimento efetivo:" in line_str:
            match = re.search(r"(\d+[\.,]\d+)", line_str)
            if match:
                current_percent = match.group(1).replace(',', '.')
            processed_rows.append(parts)
            continue

        # 2. Identifica Linhas de Itens (Data no formato Excel ex: 46024.0)
        try:
            val_0 = parts[0].replace('.0', '')
            if val_0.isdigit() and float(val_0) > 40000:
                doc = parts[1].replace('.0', '')
                produto = parts[10]
                
                # Garante que a linha tenha colunas suficientes (22 colunas)
                while len(parts) < 22: parts.append("")
                
                # REGRAS DA MARIANA:
                # Coluna G (índice 6): ID Único (Documento-Produto)
                parts[6] = f"{doc}-{produto}"
                # Coluna H (índice 7): Percentual replicado
                parts[7] = current_percent
                
                processed_rows.append(parts)
                continue
        except:
            pass

        # 3. Tratamento de Totais
        if "Total:" in line_str or "Total saídas:" in line_str:
            while len(parts) < 22: parts.append("")
            parts[5] = "-"
            parts[7] = current_percent
            processed_rows.append(parts)
        else:
            processed_rows.append(parts)

    return pd.DataFrame(processed_rows)

# --- Interface Streamlit ---
st.set_page_config(page_title="Conversor RET Domínio", layout="wide", page_icon="📊")

st.title("📊 Conversor RET - Domínio Sistemas")
st.markdown(f"**Analista:** Mariana | **Nascel Contabilidade**")

# REMOVIDA A TRAVA DE TIPO (type=['csv']) para aceitar o arquivo do Excel
uploaded_file = st.file_uploader("Arraste o arquivo extraído da Domínio aqui", type=None)

if uploaded_file:
    with st.spinner('Processando regras fiscais...'):
        try:
            df_final = processar_ret_dominio(uploaded_file)
            
            st.success("✅ Arquivo processado com sucesso!")
            
            # Download do CSV
            csv_ready = df_final.to_csv(index=False, header=False)
            st.download_button(
                label="📥 Baixar CSV para Python",
                data=csv_ready,
                file_name=f"PYTHON_{uploaded_file.name}.csv",
                mime="text/csv"
            )
            
            st.divider()
            st.write("### 🔍 Conferência Visual (IDs e Percentuais)")
            st.dataframe(df_final.head(50))
            
        except Exception as e:
            st.error(f"Erro ao processar: {e}")
