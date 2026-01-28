import streamlit as st
import pandas as pd
import io
import re

def processar_relatorio_dominio_ret(file_buffer):
    """
    Localiza o percentual na Coluna I e o replica nas linhas abaixo 
    dentro da mesma coluna até encontrar o próximo bloco.
    """
    try:
        # Lendo o CSV original
        df = pd.read_csv(file_buffer, sep=';', encoding='latin-1', dtype=str, header=None)
    except Exception:
        file_buffer.seek(0)
        df = pd.read_csv(file_buffer, sep=None, engine='python', dtype=str, header=None)

    percentual_atual = ""
    linhas_finais = []
    
    # Regex para capturar o valor numérico (ex: 1,30)
    padrao_aliquota = re.compile(r'(\d+,\d+)')

    for index, row in df.iterrows():
        linha = row.tolist()
        
        # Transformamos a linha em texto para busca de gatilhos
        linha_texto = " ".join([str(x) for x in linha if pd.notna(x)])

        # 1. IDENTIFICAÇÃO DO PERCENTUAL (Geralmente na Coluna A ou B o texto aparece)
        if "Percentual de recolhimento efetivo" in linha_texto:
            # Busca o valor na Coluna I (índice 8) conforme a imagem
            valor_coluna_i = str(linha[8]) if len(linha) > 8 else ""
            busca = padrao_aliquota.search(valor_coluna_i)
            if busca:
                percentual_atual = busca.group(1)

        # 2. REPLICAÇÃO NA COLUNA I (Índice 8)
        # Se a linha for de dados (ex: começa com data na coluna A), aplicamos o percentual
        # Usamos uma verificação simples: se a coluna A tem algo que parece data
        if len(linha) > 8 and str(linha[0])[0:2].isdigit():
            # Só preenche se a célula estiver vazia ou for para manter o padrão
            if pd.isna(linha[8]) or str(linha[8]).strip() == "" or str(linha[8]) == "nan":
                linha[8] = percentual_atual

        linhas_finais.append(linha)

    # DataFrame Final
    df_final = pd.DataFrame(linhas_finais)

    # Exportação para Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, header=False, sheet_name='RET_Auditado')
        
        workbook = writer.book
        worksheet = writer.sheets['RET_Auditado']
        format_texto = workbook.add_format({'align': 'left'})
        
        # Ajuste de largura para visualização
        if len(df_final.columns) > 10:
            worksheet.set_column(0, 0, 12, format_texto)   # Data
            worksheet.set_column(8, 8, 15, format_texto)   # Coluna I (Percentual)
            worksheet.set_column(10, 10, 45, format_texto) # Coluna K (Produto)

    return output.getvalue()

# Interface Streamlit (Mantida conforme seus padrões)
st.set_page_config(page_title="Auditoria RET - Domínio", layout="wide")
st.title("Relatório de Crédito Presumido - RET")

upped_file = st.file_uploader("Arraste o CSV nº 4 aqui", type=["csv"])

if upped_file is not None:
    with st.spinner("Processando..."):
        try:
            excel_out = processar_relatorio_dominio_ret(upped_file)
            st.success("Boooooa! Percentual replicado na Coluna I conforme a imagem.")
            st.download_button(
                label="📥 Baixar Excel Ajustado",
                data=excel_out,
                file_name="RET_Ajuste_Fino.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
