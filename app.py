import streamlit as st
import pandas as pd
import io
import re

def robust_read(file):
    """Tenta ler o arquivo da Domínio de várias formas diferentes."""
    content = file.getvalue()
    
    # 1. Tenta como Excel antigo (XLS)
    try:
        return pd.read_excel(io.BytesIO(content), engine='xlrd', header=None)
    except: pass
        
    # 2. Tenta como Excel moderno (XLSX)
    try:
        return pd.read_excel(io.BytesIO(content), engine='openpyxl', header=None)
    except: pass

    # 3. Tenta como HTML (Muitos XLS da Domínio são na verdade HTML)
    try:
        dfs = pd.read_html(io.BytesIO(content))
        if dfs: return dfs[0]
    except: pass

    # 4. Tenta como CSV (Auto-detectando o separador , ou ;)
    for enc in ['utf-8', 'latin-1', 'cp1252']:
        try:
            text = content.decode(enc)
            return pd.read_csv(io.StringIO(text), sep=None, engine='python', header=None)
        except: continue
        
    return None

def transform_data(df):
    """Aplica as regras da Mariana: ID Único e Percentual."""
    if df is None: return None
    
    # Converte tudo para string para evitar erros de tipagem
    data = df.astype(str).values.tolist()
    processed_rows = []
    current_percent = ""
    
    for row in data:
        # Limpeza básica (remove 'nan' e espaços extras)
        row = [x.strip() if x != "nan" else "" for x in row]
        line_str = " ".join(row)
        
        # 1. Captura o percentual vigente (Ex: 1.3, 6.0, 14.0)
        if "Percentual de recolhimento efetivo:" in line_str:
            match = re.search(r"(\d+[\.,]\d+)", line_str)
            if match:
                current_percent = match.group(1).replace(',', '.')
            processed_rows.append(row)
            continue
            
        # 2. Processa linhas de dados (Produtos)
        # Identificamos pelo número de data do Excel (> 40000) na primeira coluna
        try:
            val_0 = row[0].replace('.0', '')
            if val_0.isdigit() and int(val_0) > 40000:
                doc = row[1].replace('.0', '')
                produto = row[10]
                
                # Garante que a linha tenha colunas suficientes
                while len(row) < 22: row.append("")
                
                # Aplica as suas regras:
                row[6] = f"{doc}-{produto}" # Coluna G: ID (Doc-Produto)
                row[7] = current_percent     # Coluna H: Percentual
                
                processed_rows.append(row)
                continue
        except: pass
            
        # 3. Trata linhas de Total (coloca o '-' e o percentual)
        if "Total:" in line_str or "Total saídas:" in line_str:
            while len(row) < 22: row.append("")
            row[5] = "-"
            row[7] = current_percent
            processed_rows.append(row)
        else:
            processed_rows.append(row)
            
    return pd.DataFrame(processed_rows)

# Interface do App
st.set_page_config(page_title="Conversor RET Domínio", layout="wide", page_icon="📊")

st.title("📊 Conversor Regime Especial (RET) - Domínio Sistemas")
st.markdown("""
Suba o arquivo original extraído do sistema. O conversor irá criar as chaves de busca e 
organizar os percentuais automaticamente para o seu uso em Python.
""")

uploaded_file = st.file_uploader("Arraste o arquivo original (XLS ou CSV)", type=None)

if uploaded_file:
    with st.spinner('Processando arquivo...'):
        df_raw = robust_read(uploaded_file)
        
        if df_raw is not None:
            df_final = transform_data(df_raw)
            
            st.success("✅ Arquivo processado com sucesso!")
            
            # Preparação para download
            csv_buffer = io.StringIO()
            df_final.to_csv(csv_buffer, index=False, header=False)
            
            st.download_button(
                label="📥 Baixar Arquivo Convertido (CSV)",
                data=csv_buffer.getvalue(),
                file_name=f"convertido_{uploaded_file.name}.csv",
                mime="text/csv"
            )
            
            st.write("### 🔍 Prévia dos dados (Visualização)")
            st.dataframe(df_final.head(50))
        else:
            st.error("❌ Não foi possível ler o arquivo. O formato parece ser incompatível.")
