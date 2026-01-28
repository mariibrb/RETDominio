import streamlit as st
import pandas as pd
import io
import re

def processar_ret_dominio(file):
    # Leitura do arquivo enviado
    bytes_data = file.getvalue()
    try:
        content = bytes_data.decode('utf-8')
    except:
        content = bytes_data.decode('latin-1')
        
    lines = content.split('\n')
    processed_rows = []
    current_percent = ""

    for line in lines:
        # Tenta identificar o separador (vírgula ou ponto e vírgula)
        if ';' in line:
            parts = line.split(';')
        else:
            parts = line.split(',')
            
        parts = [p.strip().replace('"', '') for p in parts]
        line_str = " ".join(parts)

        # 1. Captura o Percentual de Recolhimento
        if "Percentual de recolhimento efetivo:" in line_str:
            match = re.search(r"(\d+[\.,]\d+)", line_str)
            if match:
                current_percent = match.group(1).replace(',', '.')
            processed_rows.append(parts)
            continue

        # 2. Identifica Linhas de Itens (Produtos)
        try:
            # Verifica se a primeira coluna é uma data ou o código de data do Excel
            val_0 = parts[0].replace('.0', '')
            if val_0.isdigit() and float(val_0) > 40000:
                doc = parts[1].replace('.0', '')
                produto = parts[10] if len(parts) > 10 else ""
                
                # Garante as 22 colunas do seu modelo
                while len(parts) < 22: parts.append("")
                
                # Coluna G (índice 6): ID Único
                parts[6] = f"{doc}-{produto}"
                # Coluna H (índice 7): Percentual
                parts[7] = current_percent
                
                processed_rows.append(parts)
                continue
        except:
            pass

        # 3. Linhas de Total
        if "Total:" in line_str or "Total saídas:" in line_str:
            while len(parts) < 22: parts.append("")
            parts[5] = "-"
            parts[7] = current_percent
            processed_rows.append(parts)
        else:
            processed_rows.append(parts)

    return pd.DataFrame(processed_rows)

# --- Interface Streamlit ---
st.set_page_config(page_title="Conversor RET Nascel", layout="wide")

st.title("📊 Conversor RET - Formato Excel (.xlsx)")
st.markdown("Gera o arquivo com as colunas de ID e Percentual para auditoria fiscal.")

uploaded_file = st.file_uploader("Suba o relatório da Domínio", type=None)

if uploaded_file:
    try:
        df_final = processar_ret_dominio(uploaded_file)
        
        # Gerando o Excel em memória (Buffer)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # header=False para manter o layout original do seu sistema
            df_final.to_excel(writer, index=False, header=False, sheet_name='Aba Python')
            writer.close()
        
        st.success("✅ Excel gerado com sucesso!")
        
        st.download_button(
            label="📥 Baixar Planilha Excel (.xlsx)",
            data=output.getvalue(),
            file_name=f"AUDITORIA_{uploaded_file.name.split('.')[0]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.write("### Prévia do que foi gerado:")
        st.dataframe(df_final.head(30))
        
    except Exception as e:
        st.error(f"Erro ao converter: {e}")
