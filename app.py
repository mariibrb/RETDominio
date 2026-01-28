import streamlit as st
import pandas as pd
import io
import re

def processar_relatorio_dominio_ret(file_buffer):
    """
    Processa o RET usando o Índice 6 (Coluna G) para concatenação, 
    liberando espaço para a réplica da alíquota no Índice 8 (Coluna I).
    """
    try:
        df = pd.read_csv(file_buffer, sep=';', encoding='latin-1', dtype=str, header=None)
    except Exception:
        file_buffer.seek(0)
        df = pd.read_csv(file_buffer, sep=None, engine='python', dtype=str, header=None)

    percentual_atual = ""
    col_index_aliquota = None
    linhas_finais = []
    padrao_aliquota = re.compile(r'(\d+,\d+)')

    for index, row in df.iterrows():
        linha = row.tolist()
        linha_texto = " ".join([str(x) for x in linha if pd.notna(x)])

        # 1. IDENTIFICAÇÃO DO PERCENTUAL (Normalmente na Coluna I / Índice 8)
        if "Percentual de recolhimento efetivo" in linha_texto:
            for i, celula in enumerate(linha):
                if pd.notna(celula):
                    match = padrao_aliquota.search(str(celula))
                    if match:
                        percentual_atual = match.group(1)
                        col_index_aliquota = i # Identifica onde o 1,30 está
                        break

        # 2. PROCESSAMENTO DAS LINHAS DE DADOS
        primeira_celula = str(linha[0]).strip()
        if len(primeira_celula) >= 8 and primeira_celula[0:2].isdigit() and "/" in primeira_celula:
            
            # A) REPLICAÇÃO DA ALÍQUOTA (Garante que não suma!)
            if percentual_atual and col_index_aliquota is not None:
                if len(linha) > col_index_aliquota:
                    linha[col_index_aliquota] = percentual_atual

            # B) CONCATENAÇÃO NO ÍNDICE 6 (Coluna G) - Uma antes da H/I
            if len(linha) > 10:
                valor_b = str(linha[1]) if pd.notna(linha[1]) and str(linha[1]) != "nan" else ""
                valor_produto = str(linha[10]) if pd.notna(linha[10]) and str(linha[10]) != "nan" else ""
                
                # Preenche a Coluna G (Índice 6) para não bater na réplica da alíquota
                linha[6] = f"{valor_b} - {valor_produto}".strip(" -")

        linhas_finais.append(linha)

    df_final = pd.DataFrame(linhas_finais)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, header=False, sheet_name='RET_Auditado')
        workbook = writer.book
        worksheet = writer.sheets['RET_Auditado']
        format_texto = workbook.add_format({'align': 'left'})
        
        total_cols = len(df_final.columns)
        if total_cols > 10:
            worksheet.set_column(6, 6, 30, format_texto)  # Concatenação (G)
            worksheet.set_column(8, 8, 12, format_texto)  # Alíquota (I)
            worksheet.set_column(10, 10, 45, format_texto) # Produto (K)

    return output.getvalue()

# Interface Streamlit permanece íntegra conforme sua orientação
st.set_page_config(page_title="Auditoria RET - Domínio", layout="wide")
st.title("Relatório de Crédito Presumido - RET")

upped_file = st.file_uploader("Arraste o CSV nº 4 aqui", type=["csv"])

if upped_file is not None:
    with st.spinner("Ajustando colunas G, H e I..."):
        try:
            excel_out = processar_relatorio_dominio_ret(upped_file)
            st.success("Agora sim! Concatenação na G, Alíquota na I e Produto na K.")
            st.download_button(
                label="📥 Baixar Excel Ajustado",
                data=excel_out,
                file_name="RET_Dominio_Final_G_I.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
