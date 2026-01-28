import streamlit as st
import pandas as pd
import io
import re

def processar_relatorio_dominio_ret(file_buffer):
    """
    Processa o RET replicando a alíquota na coluna correta e concatenando 
    os dados no Índice 10 conforme solicitado.
    """
    try:
        # Lendo o CSV original com separador ';' e mantendo tipos como string
        df = pd.read_csv(file_buffer, sep=';', encoding='latin-1', dtype=str, header=None)
    except Exception:
        file_buffer.seek(0)
        df = pd.read_csv(file_buffer, sep=None, engine='python', dtype=str, header=None)

    percentual_atual = ""
    col_index_aliquota = None
    linhas_finais = []
    
    # Regex para capturar o valor numérico (ex: 1,30)
    padrao_aliquota = re.compile(r'(\d+,\d+)')

    for index, row in df.iterrows():
        linha = row.tolist()
        
        # Transformamos a linha em texto para busca do gatilho
        linha_texto = " ".join([str(x) for x in linha if pd.notna(x)])

        # 1. IDENTIFICAÇÃO DINÂMICA DO PERCENTUAL E DA COLUNA
        if "Percentual de recolhimento efetivo" in linha_texto:
            for i, celula in enumerate(linha):
                if pd.notna(celula):
                    match = padrao_aliquota.search(str(celula))
                    if match:
                        percentual_atual = match.group(1)
                        col_index_aliquota = i
                        break

        # 2. PROCESSAMENTO DAS LINHAS DE DADOS (Identificadas por data na Coluna A)
        primeira_celula = str(linha[0]).strip()
        if len(primeira_celula) >= 8 and primeira_celula[0:2].isdigit() and "/" in primeira_celula:
            # A) Replicação do Percentual na Coluna Identificada
            if percentual_atual and col_index_aliquota is not None:
                if len(linha) > col_index_aliquota:
                    linha[col_index_aliquota] = percentual_atual

            # B) CONCATENAÇÃO NO ÍNDICE 10 (Conteúdo do Índice 2 + Índice 11)
            # Verificamos se os índices existem na linha atual
            if len(linha) > 11:
                valor_indice_2 = str(linha[2]) if pd.notna(linha[2]) and str(linha[2]) != "nan" else ""
                valor_indice_11 = str(linha[11]) if pd.notna(linha[11]) and str(linha[11]) != "nan" else ""
                
                # Realiza a concatenação e grava no Índice 10 (Coluna K)
                linha[10] = f"{valor_indice_2} - {valor_indice_11}".strip(" -")

        linhas_finais.append(linha)

    # DataFrame Final mantendo a estrutura original (sem colunas a mais)
    df_final = pd.DataFrame(linhas_finais)

    # Exportação para Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, header=False, sheet_name='RET_Auditado')
        
        workbook = writer.book
        worksheet = writer.sheets['RET_Auditado']
        format_texto = workbook.add_format({'align': 'left'})
        
        # Ajuste visual das colunas existentes
        total_cols = len(df_final.columns)
        if total_cols > 0:
            worksheet.set_column(0, total_cols - 1, 12, format_texto)
        if total_cols > 10:
            worksheet.set_column(10, 10, 50, format_texto) # Coluna K (Índice 10) agora mais larga

    return output.getvalue()

# Interface Streamlit
st.set_page_config(page_title="Auditoria RET - Domínio", layout="wide")
st.title("Relatório de Crédito Presumido - RET")

upped_file = st.file_uploader("Arraste o CSV nº 4 aqui", type=["csv"])

if upped_file is not None:
    with st.spinner("Realizando concatenação e ajuste fino..."):
        try:
            excel_out = processar_relatorio_dominio_ret(upped_file)
            st.success("Perfeito! Índice 10 atualizado com a concatenação solicitada.")
            st.download_button(
                label="📥 Baixar Excel Finalizado",
                data=excel_out,
                file_name="RET_Dominio_Final_Concatenado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
