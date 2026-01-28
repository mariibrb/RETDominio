import streamlit as st
import pandas as pd
import pdfplumber
import io
import re

def processar_pdf_para_excel(pdf_file):
    all_rows = []
    current_percent = ""
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            # Extraímos as tabelas da página
            tables = page.extract_tables()
            
            for table in tables:
                for row in table:
                    # Limpeza de dados nulos do PDF
                    row_clean = [str(item).strip() if item else "" for item in row]
                    line_text = " ".join(row_clean)
                    
                    # 1. Busca o Percentual de Recolhimento
                    if "Percentual de recolhimento efetivo:" in line_text:
                        match = re.search(r"(\d+[\.,]\d+)", line_text)
                        if match:
                            current_percent = match.group(1).replace(',', '.')
                        all_rows.append(row_clean)
                        continue
                    
                    # 2. Identifica Linhas de Produtos (Data no formato DD/MM/AAAA)
                    # No PDF a data vem formatada, diferente do Excel binário
                    if len(row_clean) > 5 and re.match(r"\d{2}/\d{2}/\d{2,4}", row_clean[0]):
                        doc = row_clean[1]
                        # Tentamos localizar a descrição (geralmente coluna 10 no seu modelo)
                        produto = row_clean[10] if len(row_clean) > 10 else "PRODUTO"
                        
                        # Garante as 22 colunas padrão
                        while len(row_clean) < 22: row_clean.append("")
                        
                        # REGRAS DA MARIANA:
                        row_clean[6] = f"{doc}-{produto}" # ID na Coluna G
                        row_clean[7] = current_percent     # % na Coluna H
                        
                        all_rows.append(row_clean)
                        continue

                    # 3. Totais
                    if "Total:" in line_text or "Total saídas:" in line_text:
                        while len(row_clean) < 22: row_clean.append("")
                        row_clean[5] = "-"
                        row_clean[7] = current_percent
                        all_rows.append(row_clean)
                    else:
                        all_rows.append(row_clean)

    return pd.DataFrame(all_rows)

# --- Interface Streamlit ---
st.set_page_config(page_title="Conversor RET PDF", layout="wide")

st.title("📄 Conversor Fiscal: PDF para Excel (.xlsx)")
st.subheader("Foco: Analista Fiscal Mariana | Nascel Contabilidade")

uploaded_pdf = st.file_uploader("Suba o PDF ORIGINAL da Domínio", type=["pdf"])

if uploaded_pdf:
    try:
        with st.spinner('Lendo tabelas do PDF e gerando ID Único...'):
            df_final = processar_pdf_para_excel(uploaded_pdf)
            
            if not df_final.empty:
                # Gerando o EXCEL REAL
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, header=False, sheet_name='Aba Python')
                
                st.success("✅ PDF processado com sucesso!")
                
                st.download_button(
                    label="📥 Baixar Planilha de Auditoria (.xlsx)",
                    data=output.getvalue(),
                    file_name=f"AUDITORIA_PDF_{uploaded_pdf.name.split('.')[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.divider()
                st.write("### 🔍 Prévia da Extração")
                st.dataframe(df_final.head(50))
            else:
                st.error("Não encontrei tabelas no PDF. O arquivo é o relatório original?")
    except Exception as e:
        st.error(f"Erro ao processar PDF: {e}")
