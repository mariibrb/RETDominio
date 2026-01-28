import streamlit as st
import pandas as pd
import io

def processar_relatorio_ret(file):
    # Lendo o CSV nº 4 (ponto e vírgula como separador padrão do Excel/Domínio)
    # Usamos dtype=str para não perder zeros à esquerda ou formatar números precocemente
    df = pd.read_csv(file, sep=';', encoding='latin-1', dtype=str, header=None)

    # Variáveis de controle para replicação dos blocos
    percentual_atual = ""
    dados_processados = []

    for index, row in df.iterrows():
        linha_lista = row.tolist()
        texto_linha = " ".join([str(val) for val in linha_lista if pd.notna(val)])

        # Lógica de identificação e replicação dos blocos (1.3, 6, 14)
        if "recolhimento efetivo:" in texto_linha or "Percentual de" in texto_linha:
            if "1,30" in texto_linha:
                percentual_atual = "1,30"
            elif "6,00" in texto_linha:
                percentual_atual = "6,00"
            elif "14,00" in texto_linha:
                percentual_atual = "14,00"

        # Adiciona o percentual do bloco na última coluna (Replicação)
        linha_lista.append(percentual_atual)

        # Lógica de Concatenar (Exemplo: Coluna 3 + Coluna 4 que costumam ser CFOP/Produto)
        # Ajustado para manter a integridade fiscal conforme sua regra
        if pd.notna(linha_lista[3]) and pd.notna(linha_lista[4]):
            concatenado = f"{linha_lista[3]} - {linha_lista[4]}"
            linha_lista.insert(5, concatenado) # Insere a nova coluna concatenada
        else:
            linha_lista.insert(5, "")

        dados_processados.append(linha_lista)

    # Criando o DataFrame final
    df_final = pd.DataFrame(dados_processados)

    # Gerando o arquivo Excel em memória (Buffer)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, header=False)
    
    return output.getvalue()

# Interface Streamlit
st.set_page_config(page_title="Auditoria RET - Domínio", layout="wide")
st.title("Processador de Crédito Presumido (RET)")

upped_file = st.file_uploader("Envie o CSV gerado pelo sistema (Arquivo nº 4)", type=["csv"])

if upped_file is not None:
    with st.spinner("Processando hierarquia fiscal e blocos..."):
        try:
            resultado = processar_relatorio_ret(upped_file)
            
            if resultado:
                st.success("Arquivo processado com sucesso! Percentuais 1.3, 6 e 14 replicados.")
                st.download_button(
                    label="📥 Baixar Excel Processado",
                    data=resultado,
                    file_name="RET_Processado_Final.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Erro ao processar: {e}")

st.divider()
st.caption("Nota: Este script mantém a integridade total dos dados originais e apenas expande a análise de blocos.")
