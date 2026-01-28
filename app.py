import streamlit as st
import pandas as pd
import io
import re

def processar_relatorio_dominio_ret(file_buffer):
    """
    Processa o relatório de Crédito Presumido capturando dinamicamente 
    qualquer alíquota de recolhimento efetivo e replicando-a.
    """
    try:
        # Lendo o arquivo CSV nº 4 com separador ';' e mantendo integridade de strings
        df = pd.read_csv(file_buffer, sep=';', encoding='latin-1', dtype=str, header=None)
    except Exception:
        file_buffer.seek(0)
        df = pd.read_csv(file_buffer, sep=None, engine='python', dtype=str, header=None)

    percentual_atual = ""
    linhas_finais = []

    # Regex para encontrar números com vírgula (ex: 1,30 ou 15,25)
    padrao_aliquota = re.compile(r'(\d+,\d+)')

    for index, row in df.iterrows():
        linha = row.tolist()
        linha_texto = " ".join([str(x) for x in linha if pd.notna(x)])

        # IDENTIFICAÇÃO DINÂMICA DO BLOCO
        # Se a linha contiver a palavra-chave, extraímos o número que vier nela
        if "recolhimento efetivo" in linha_texto.lower() or "Percentual de" in linha_texto:
            busca = padrao_aliquota.search(linha_texto)
            if busca:
                percentual_atual = busca.group(1)

        # --- REGRAS DE INTEGRIDADE E POSICIONAMENTO ---
        
        # Garante que a linha tenha colunas suficientes para os novos dados
        while len(linha) < 12:
            linha.append("")

        # REPLICAÇÃO NA COLUNA J (Abaixo da coluna I - Base de Cálculo)
        # O valor capturado dinamicamente preenche o índice 9
        linha[9] = percentual_atual

        # CONCATENAÇÃO NA COLUNA K (CFOP + Produto)
        # Mantém a regra de unir Coluna D (3) e Coluna E (4)
        col_d = str(linha[3]) if pd.notna(linha[3]) and str(linha[3]) != "nan" else ""
        col_e = str(linha[4]) if pd.notna(linha[4]) and str(linha[4]) != "nan" else ""
        
        if col_d or col_e:
            # Concatena preservando a clareza para auditoria
            linha[10] = f"{col_d} - {col_e}".strip(" -")
        else:
            linha[10] = ""

        linhas_finais.append(linha)

    # Reconstrução do DataFrame sem simplificações
    df_final = pd.DataFrame(linhas_finais)

    # Geração do Excel com ajuste de layout
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, header=False, sheet_name='Relatorio_Auditado')
        
        workbook = writer.book
        worksheet = writer.sheets['Relatorio_Auditado']
        
        # Formatação básica para legibilidade
        format_texto = workbook.add_format({'align': 'left'})
        for i, col in enumerate(df_final.columns):
            worksheet.set_column(i, i, 18, format_texto)

    return output.getvalue()

# Interface Streamlit
st.set_page_config(page_title="Auditoria RET - Domínio", layout="wide")
st.title("Processador de Crédito Presumido (RET)")
st.subheader("Extração Dinâmica de Alíquotas e Blocos")

uploaded_file = st.file_uploader("Envie o CSV (Arquivo nº 4)", type=["csv"])

if uploaded_file is not None:
    with st.spinner("Analisando estrutura fiscal e alíquotas..."):
        try:
            excel_data = processar_relatorio_dominio_ret(uploaded_file)
            
            st.success("Processamento concluído! As alíquotas foram identificadas e replicadas na Coluna J.")
            st.download_button(
                label="📥 Baixar Relatório Processado",
                data=excel_data,
                file_name="Auditoria_RET_Dinamico.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

st.divider()
st.info("A lógica de concatenação está na Coluna K e a replicação de alíquotas na Coluna J.")
