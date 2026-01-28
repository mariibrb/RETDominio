import streamlit as st
import pandas as pd
import pdfplumber
import io
import re

def processar_pdf_nascel(pdf_file):
    dados_finais = []
    percentual_atual_str = ""
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            # Extração de tabela com tolerância para não perder colunas de valores à direita
            tabela = page.extract_table({
                "vertical_strategy": "text", 
                "horizontal_strategy": "text",
                "snap_tolerance": 3,
            })
            
            if not tabela:
                continue

            for row in tabela:
                # Limpeza e normalização
                row_clean = [str(item).strip() if item else "" for item in row]
                line_text = " ".join(row_clean)
                
                if not any(row_clean) or "Página:" in line_text:
                    continue

                # Criamos a estrutura de 22 colunas (índices 0 a 21) da sua Aba Python
                linha_excel = [""] * 22

                # 1. CAPTURA DO PERCENTUAL (Ex: 1,30)
                if "Percentual de recolhimento efetivo:" in line_text:
                    match = re.search(r"(\d+[\.,]\d+)", line_text)
                    if match:
                        # AJUSTE FINO: Usar vírgula conforme solicitado
                        percentual_atual_str = match.group(1).replace('.', ',')
                    
                    linha_excel[0] = "Percentual de recolhimento efetivo:"
                    linha_excel[7] = percentual_atual_str # Na linha do título, fica na Col H
                    dados_finais.append(linha_excel)
                    continue

                # 2. CABEÇALHO (Linha 7 do seu modelo)
                if "Documento" in line_text and "Acumulador" in line_text:
                    linha_excel[0] = "Data"
                    linha_excel[1] = "Documento"
                    linha_excel[5] = "Acumulador"
                    linha_excel[6] = "ID Único"
                    linha_excel[7] = "Percentual"
                    linha_excel[8] = "CFOP"
                    linha_excel[10] = "Produto"
                    linha_excel[12] = "Tipo do produto"
                    linha_excel[14] = "Valor produto"
                    linha_excel[15] = "Valor contábil"
                    linha_excel[16] = "Base cálculo"
                    linha_excel[17] = "Isentas"
                    linha_excel[21] = "Valor ICMS"
                    dados_finais.append(linha_excel)
                    continue

                # 3. LINHAS DE DADOS (Itens)
                if len(row_clean) >= 5 and re.match(r"\d{2}/\d{2}/\d{4}", row_clean[0]):
                    data_orig = row_clean[0]
                    doc_orig  = row_clean[1]
                    acum_orig = row_clean[2]
                    
                    # Separa CFOP e Produto (Tratando o hífen ex: 6-106 para 6106)
                    cfop_prod_raw = row_clean[3]
                    cfop_match = re.match(r"^(\d-?\d{3})", cfop_prod_raw)
                    cfop = cfop_match.group(1).replace('-', '') if cfop_match else ""
                    desc_produto = cfop_prod_raw.replace(cfop_match.group(0), "").strip() if cfop_match else cfop_prod_raw
                    
                    # MAPEAMENTO EXATO ABA PYTHON:
                    linha_excel[0] = data_orig           # Col A
                    linha_excel[1] = doc_orig            # Col B
                    linha_excel[5] = acum_orig           # Col F
                    linha_excel[6] = f"{doc_orig}-{desc_produto}" # Col G: ID Único
                    linha_excel[7] = percentual_atual_str # Col H: Percentual (1,3)
                    linha_excel[8] = cfop                # Col I: CFOP
                    linha_excel[10] = desc_produto       # Col K: Produto
                    
                    # Colunas de Valores (Conforme o arquivo de exemplo Aba 1)
                    if len(row_clean) >= 10:
                        linha_excel[12] = row_clean[4]   # Col M: Tipo
                        linha_excel[14] = row_clean[6]   # Col O: Valor produto
                        linha_excel[15] = row_clean[7]   # Col P: Valor contábil
                        linha_excel[16] = row_clean[8]   # Col Q: Base cálculo
                        linha_excel[17] = row_clean[9]   # Col R: Isentas
                        linha_excel[21] = row_clean[-1]  # Col V: Valor ICMS
                    
                    dados_finais.append(linha_excel)
                    continue

                # 4. TRATAMENTO DE TOTAIS (As "pequenas mudanças" cruciais)
                if "Total:" in line_text or "Total saídas:" in line_text:
                    linha_excel[0] = line_text
                    linha_excel[5] = "-"                  # Col F: Sinal de total
                    linha_excel[6] = percentual_atual_str # Col G: Percentual no Total (Pula uma coluna)
                    
                    # Mapeamento de valores do total
                    if len(row_clean) >= 4:
                        linha_excel[14] = row_clean[-4]   # Total Produto
                        linha_excel[15] = row_clean[-3]   # Total Contábil
                        linha_excel[16] = row_clean[-2]   # Total Base
                        linha_excel[21] = row_clean[-1]   # Total ICMS
                    dados_finais.append(linha_excel)
                else:
                    # Demais linhas mantêm o texto na primeira coluna
                    linha_excel[0] = line_text
                    dados_finais.append(linha_excel)

    return pd.DataFrame(dados_finais)

# --- App Streamlit ---
st.set_page_config(page_title="PDF para Aba Python", layout="wide")

st.title("⚖️ Conversor Nascel: PDF -> Excel (Aba Python)")
st.info("Este conversor respeita o mapeamento exato de colunas e as regras de Totais da sua Aba Python.")

pdf_file = st.file_uploader("Suba o PDF ORIGINAL da Domínio", type=["pdf"])

if pdf_file:
    try:
        with st.spinner('Lendo PDF e mapeando colunas...'):
            df_final = processar_pdf_nascel(pdf_file)
            
            if not df_final.empty:
                # Gerando Excel Real (.xlsx)
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, header=False, sheet_name='Aba Python')
                
                st.success("✅ Excel gerado seguindo fielmente a Aba Python!")
                st.download_button(
                    label="📥 Baixar Planilha (.xlsx)",
                    data=buffer.getvalue(),
                    file_name=f"ABA_PYTHON_{pdf_file.name.split('.')[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.divider()
                st.write("### 🔍 Conferência Visual (Mapeamento de Auditoria)")
                st.dataframe(df_final.head(100))
            else:
                st.error("Não foi possível extrair dados. O PDF está no formato original?")
    except Exception as e:
        st.error(f"Erro no processamento: {e}")
