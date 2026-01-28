import streamlit as st
import pandas as pd
import io
import re

def process_raw_data(string_data):
    """Processa o texto puro seguindo as regras da Mariana (ID e Percentual)"""
    lines = string_data.split('\n')
    processed_lines = []
    current_percent = None
    
    for line in lines:
        line = line.replace('\r', '').strip()
        if not line: continue
        
        parts = line.split(',')
        # Se não houver vírgula, tenta ponto e vírgula (comum em CSVs brasileiros)
        if len(parts) < 5:
            parts = line.split(';')
            
        parts = [p.strip() for p in parts]
        
        # 1. Identifica o Percentual
        if "Percentual de recolhimento efetivo:" in line:
            match = re.search(r"(\d+\.?\d*)", line)
            if match:
                current_percent = match.group(1)
            processed_lines.append(line)
            continue

        # 2. Processa linhas de Produtos
        try:
            # Verifica se a primeira coluna é a data (formato numérico ou string)
            if parts[0] and len(parts) > 10:
                doc = parts[1]
                prod_desc = parts[10]
                
                # Criando o ID: Documento-Produto (Índice 6)
                parts[6] = f"{doc}-{prod_desc}"
                # Inserindo o Percentual (Índice 7)
                parts[7] = current_percent if current_percent else ""
                
                processed_lines.append(",".join(parts))
                continue
        except (ValueError, IndexError):
            pass

        # 3. Totais e Cabeçalhos
        if "Total:" in line or "DÉBITOS PELAS SAÍDAS" in line:
            if len(parts) > 7:
                parts[5] = "-"
                parts[7] = current_percent if current_percent else ""
            processed_lines.append(",".join(parts))
        else:
            processed_lines.append(line)
            
    return "\n".join(processed_lines)

# --- Interface Streamlit ---
st.set_page_config(page_title="Conversor RET Domínio", layout="wide")
st.title("📂 Conversor RET - Direto da Domínio")

uploaded_file = st.file_uploader("Suba o arquivo EXATAMENTE como saiu do sistema", type=None)

if uploaded_file is not None:
    try:
        # Pega os bytes do arquivo
        content = uploaded_file.getvalue()
        
        # ESTRATÉGIA DE LEITURA:
        # 1. Tenta ler como texto puro (Se for o CSV 'disfarçado')
        try:
            raw_text = content.decode('utf-8')
        except:
            try:
                raw_text = content.decode('latin-1')
            except:
                # 2. Se falhar, tenta forçar a leitura como uma tabela (se for o falso XLS)
                df_temp = pd.read_html(io.BytesIO(content))[0]
                raw_text = df_temp.to_csv(index=False)

        # Processa as regras da Mariana
        result = process_raw_data(raw_text)
        
        st.success("✅ Arquivo reconhecido e processado!")
        
        st.download_button(
            label="📥 Baixar Relatório Formatado",
            data=result,
            file_name=f"FINAL_{uploaded_file.name}.csv",
            mime="text/csv"
        )
        
        st.text_area("Prévia do arquivo convertido:", value=result[:2000], height=300)

    except Exception as e:
        st.error(f"Erro ao interpretar o formato da Domínio: {e}")
        st.info("Este erro ocorre porque o sistema exporta um arquivo que não é um Excel padrão. Tentei converter automaticamente, mas o formato é muito específico.")

st.sidebar.warning("⚠️ Não é necessário abrir o arquivo no Excel antes de subir.")
