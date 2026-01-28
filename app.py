import streamlit as st
import pandas as pd
import re
import io

def processar_texto_sujo(conteudo_bruto):
    # Tenta decodificar o binário para texto ignorando erros de caracteres estranhos
    try:
        texto = conteudo_bruto.decode('utf-8', errors='ignore')
    except:
        texto = conteudo_bruto.decode('latin-1', errors='ignore')

    # Remove caracteres nulos e lixo eletrônico que causam o erro de BOF
    texto_limpo = texto.replace('\x00', '').replace('\x01', '').replace('\x02', '')
    
    lines = texto_limpo.split('\n')
    processed_rows = []
    current_percent = None
    
    for line in lines:
        # Divide por vírgula ou tabulação (comum em arquivos de sistema)
        parts = re.split(r'[,;]|\t', line)
        parts = [p.strip() for p in parts if p.strip() or p == ""]
        
        if len(parts) < 2: continue
        
        line_full = " ".join(parts)
        
        # 1. Identifica o Percentual
        if "Percentual de recolhimento efetivo:" in line_full:
            match = re.search(r"(\d+\.?\d*)", line_full)
            if match:
                current_percent = match.group(1)
            processed_rows.append(parts)
            continue

        # 2. Processa Itens (Hierarquia Fiscal)
        try:
            # Verifica se a primeira coluna tem cara de data ou número de série (46024...)
            if parts[0] and (len(parts[0]) >= 5) and len(parts) > 10:
                doc = parts[1]
                # No arquivo cru, o produto costuma estar na coluna 10
                prod_desc = parts[10] if len(parts) > 10 else "PRODUTO"
                
                # Garante que a linha tenha espaço para o ID e Percentual
                while len(parts) < 12: parts.append("")
                
                # Criando ID: Doc-Produto (Coluna G/Índice 6)
                parts[6] = f"{doc}-{prod_desc}"
                # Inserindo Percentual (Coluna H/Índice 7)
                parts[7] = current_percent if current_percent else ""
                
                processed_rows.append(parts)
                continue
        except:
            pass

        processed_rows.append(parts)
            
    return pd.DataFrame(processed_rows)

# --- Interface Streamlit ---
st.set_page_config(page_title="Conversor RET Domínio", layout="wide")
st.title("📂 Conversor RET - Força Bruta (Lê arquivo cru)")

file = st.file_uploader("Suba o arquivo EXATAMENTE como saiu da Domínio")

if file:
    try:
        # Lê os bytes puros do arquivo para não dar erro de formato
        bytes_data = file.read()
        
        with st.spinner('Limpando sujeira do arquivo e aplicando regras...'):
            df_final = processar_texto_sujo(bytes_data)
        
        if not df_final.empty:
            st.success("✅ Arquivo processado!")
            
            csv_ready = df_final.to_csv(index=False, header=False)
            st.download_button(
                label="📥 Baixar CSV para Python",
                data=csv_ready,
                file_name=f"PROCESSADO_{file.name}.csv",
                mime="text/csv"
            )
            
            st.write("### 🔍 Prévia do que o Python extraiu:")
            st.dataframe(df_final.head(30))
        else:
            st.error("O arquivo subiu, mas não consegui extrair dados. Verifique se ele não está vazio.")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")

st.sidebar.info("Esta versão lê o código binário do arquivo diretamente, ignorando os bloqueios de formato do Excel.")
