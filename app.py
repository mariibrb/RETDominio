import streamlit as st
import pandas as pd
import io
import re

def processar_relatorio_dominio_ret(file_buffer):
    """
    Processa o RET inserindo uma nova coluna de concatenação antes do produto.
    Mantém o produto original intacto, agora deslocado uma coluna para a direita.
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

        # 1. IDENTIFICAÇÃO DO PERCENTUAL (Mesma lógica anterior)
        if "Percentual de recolhimento efetivo" in linha_texto:
            for i, celula in enumerate(linha):
                if pd.notna(celula):
                    match = padrao_aliquota.search(str(celula))
                    if match:
                        percentual_atual = match.group(1)
                        col_index_aliquota = i
                        break

        # 2. PROCESSAMENTO DAS LINHAS DE DADOS
        primeira_celula = str(linha[0]).strip()
        if len(primeira_celula) >= 8 and primeira_celula[0:2].isdigit() and "/" in primeira_celula:
            
            # A) REPLICAÇÃO DA ALÍQUOTA
            if percentual_atual and col_index_aliquota is not None:
                if len(linha) > col_index_aliquota:
                    linha[col_index_aliquota] = percentual_atual

            # B) CONCATENAÇÃO E INSERÇÃO DE COLUNA
            # Pegamos B (Índice 1) e o Produto (Índice 10)
            if len(linha) > 10:
                valor_b = str(linha[1]) if pd.notna(linha[1]) and str(linha[1]) != "nan" else ""
                valor_produto = str(linha[10]) if pd.notna(linha[10]) and str(linha[10]) != "nan" else ""
                
                resultado_concat = f"{valor_b} - {valor_produto}".strip(" -")
                
                # INSERE a concatenação na posição 10. 
                # O produto que estava na 10 vira 11 automaticamente.
                linha.insert(10, resultado_concat)
        else:
            # Para linhas que não são de dados (cabeçalhos), 
            # inserimos uma célula vazia para manter o alinhamento das colunas
            if len(linha) > 10:
                linha.insert(10, "")

        linhas_finais.append(linha)

    df_final = pd.DataFrame(linhas_finais)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, header=False, sheet_name='RET_Auditado')
        workbook = writer.book
        worksheet = writer.sheets['RET_Auditado']
        format_texto = workbook.add_format({'align': 'left'})
        
        total_cols = len(df_final.columns)
        if total_cols > 11:
            worksheet.set_column(0, total_cols - 1, 12, format_texto)
            worksheet.set_column(10, 10, 30, format_texto) # Coluna da Concatenação
            worksheet.set_column(11, 11, 45, format_texto) # Coluna do Produto (Intacta)

    return output.getvalue()

# Interface Streamlit
st.set_page_config(page_title="Auditoria RET - Domínio", layout="wide")
st.title("Relatório de Crédito Presumido - RET")

upped_file = st.file_uploader("Arraste o CSV nº 4 aqui", type=["csv"])

if upped_file is not None:
    with st.spinner("Inserindo coluna e processando..."):
        try:
            excel_out = processar_relatorio_dominio_ret(upped_file)
            st.success("Boooooa! Agora a concatenação está antes e o produto continua igual.")
            st.download_button(
                label="📥 Baixar Excel com Nova Coluna",
                data=excel_out,
                file_name="RET_Dominio_Colunas_Ajustadas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
