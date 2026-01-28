import streamlit as st
import pandas as pd
import io
import re

def processar_relatorio_dominio_ret(file_buffer):
    """
    Processa o RET mantendo o limite de colunas original do CSV.
    Replica a alíquota na Coluna J e mantém o Produto na Coluna K.
    """
    try:
        # Lendo o CSV com separador ';'
        df = pd.read_csv(file_buffer, sep=';', encoding='latin-1', dtype=str, header=None)
    except Exception:
        file_buffer.seek(0)
        df = pd.read_csv(file_buffer, sep=None, engine='python', dtype=str, header=None)

    # Identificamos quantas colunas o arquivo original realmente tem
    total_colunas_originais = len(df.columns)
    
    percentual_atual = ""
    linhas_finais = []
    
    # Regex para capturar alíquota (ex: 4,00)
    padrao_aliquota = re.compile(r'(\d+,\d+)')

    for index, row in df.iterrows():
        linha = row.tolist()
        linha_texto = " ".join([str(x) for x in linha if pd.notna(x)])

        # 1. IDENTIFICAÇÃO DINÂMICA DO PERCENTUAL
        if "recolhimento efetivo" in linha_texto.lower() or "Percentual de" in linha_texto:
            busca = padrao_aliquota.search(linha_texto)
            if busca:
                percentual_atual = busca.group(1)

        # 2. REPLICAÇÃO NA COLUNA J (Índice 9)
        # Verificamos se a coluna J existe antes de tentar gravar
        if total_colunas_originais > 9:
            linha[9] = percentual_atual

        # 3. MANUTENÇÃO DO PRODUTO (Índice 10 / Coluna K)
        # Não criamos coluna de concatenação ao final para não exceder o limite original.
        # Caso precise da concatenação, ela deve substituir uma coluna existente 
        # ou ser feita por você manualmente depois, como você mencionou.
        
        linhas_finais.append(linha)

    # Criando DataFrame final com o mesmo número de colunas do original
    df_final = pd.DataFrame(linhas_finais)

    # Exportação para Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # index=False e header=False para não criar linhas/colunas extras
        df_final.to_excel(writer, index=False, header=False, sheet_name='RET_Auditado')
        
        workbook = writer.book
        worksheet = writer.sheets['RET_Auditado']
        format_texto = workbook.add_format({'align': 'left'})
        
        # Ajuste de largura apenas nas colunas que já existem
        if total_colunas_originais > 10:
            worksheet.set_column(8, 8, 12, format_texto)  # CFOP
            worksheet.set_column(9, 9, 10, format_texto)  # Alíquota (Coluna J)
            worksheet.set_column(10, 10, 40, format_texto) # Produto (Coluna K)

    return output.getvalue()

# Interface Streamlit
st.set_page_config(page_title="Auditoria RET - Domínio", layout="wide")
st.title("Relatório de Crédito Presumido - RET")

upped_file = st.file_uploader("Arraste o CSV nº 4 aqui", type=["csv"])

if upped_file is not None:
    with st.spinner("Processando..."):
        try:
            excel_out = processar_relatorio_dominio_ret(upped_file)
            st.success("Arquivo processado! Estrutura original de colunas mantida.")
            st.download_button(
                label="📥 Baixar Excel Ajustado",
                data=excel_out,
                file_name="RET_Dominio_Original_Colunas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
