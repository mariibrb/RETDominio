import streamlit as st
import pandas as pd
import io
import re

def processar_relatorio_ret(file):
    # Tenta ler o arquivo da Domínio de várias formas (XLS ou CSV)
    content = file.getvalue()
    df_input = None

    # Tenta ler como Excel primeiro (formatos XLS ou XLSX)
    try:
        df_input = pd.read_excel(io.BytesIO(content), header=None, engine='xlrd')
    except:
        try:
            df_input = pd.read_excel(io.BytesIO(content), header=None, engine='openpyxl')
        except:
            # Se falhar, tenta ler como CSV/Texto com diferentes codificações
            for enc in ['utf-8', 'latin-1', 'cp1252', 'utf-16']:
                try:
                    text_content = content.decode(enc)
                    # Detecta separador , ou ;
                    sep = ';' if ';' in text_content.split('\n')[10] else ','
                    df_input = pd.read_csv(io.StringIO(text_content), sep=sep, header=None, engine='python')
                    break
                except:
                    continue

    if df_input is None:
        return None

    processed_rows = []
    current_percent = ""

    # Transformamos o DataFrame em lista para processar linha a linha com precisão
    # Mantendo a hierarquia e regras de agregação
    data = df_input.fillna("").astype(str).values.tolist()

    for row in data:
        # Limpeza básica e identificação do conteúdo da linha
        row_clean = [str(x).strip() for x in row]
        line_full_text = " ".join(row_clean)

        # 1. Identifica e "guarda" o Percentual de recolhimento da seção
        if "Percentual de recolhimento efetivo:" in line_full_text:
            match = re.search(r"(\d+[\.,]\d+)", line_full_text)
            if match:
                current_percent = match.group(1).replace(',', '.')
            processed_rows.append(row_clean)
            continue

        # 2. Identifica Linhas de Itens (Produtos)
        # Verificamos se a primeira coluna parece uma data do Excel (ex: 46024.0)
        try:
            primeira_celula = row_clean[0].replace('.0', '')
            if primeira_celula.isdigit() and int(primeira_celula) > 40000:
                doc = row_clean[1].replace('.0', '')
                produto = row_clean[10]

                # Garante que a linha tenha colunas suficientes (padrão 22 colunas)
                while len(row_clean) < 22: row_clean.append("")

                # REGRAS DA MARIANA (Aba Python):
                # Coluna G (índice 6): ID Único (Documento-Produto)
                row_clean[6] = f"{doc}-{produto}"
                # Coluna H (índice 7): Percentual replicado
                row_clean[7] = current_percent
                
                processed_rows.append(row_clean)
                continue
        except (ValueError, IndexError):
            pass

        # 3. Tratamento de Linhas de Total e Sub-totais
        if "Total:" in line_full_text or "Total saídas:" in line_full_text:
            while len(row_clean) < 22: row_clean.append("")
            # Coluna F (índice 5): Adiciona o "-" conforme solicitado
            row_clean[5] = "-"
            # Coluna H (índice 7): Adiciona o percentual da seção
            row_clean[7] = current_percent
            processed_rows.append(row_clean)
        else:
            # Mantém as demais linhas (cabeçalhos, apuração geral, etc) íntegras
            processed_rows.append(row_clean)

    return pd.DataFrame(processed_rows)

# --- Interface Streamlit ---
st.set_page_config(page_title="Conversor RET Nascel", layout="wide", page_icon="⚖️")

st.title("⚖️ Conversor de Relatório RET (Domínio -> Python)")
st.markdown("""
**Instruções:**
1. Carregue o arquivo XLS ou CSV do relatório de Crédito Presumido.
2. O sistema aplicará as regras de ID Único e repetição de Percentuais.
3. O download será um arquivo **Excel (.xlsx)** pronto para análise.
""")

# Removida restrição de tipo para evitar erros de MIME type do Windows
uploaded_file = st.file_uploader("Arraste o arquivo da Domínio aqui", type=None)

if uploaded_file:
    try:
        with st.spinner('Processando regras fiscais e gerando Excel...'):
            df_result = processar_relatorio_ret(uploaded_file)
            
            if df_result is not None:
                # Criando o arquivo Excel real em memória
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_result.to_excel(writer, index=False, header=False, sheet_name='Aba Python')
                
                st.success("✅ Conversão concluída com sucesso!")
                
                # Botão de Download para o formato EXCEL (.xlsx)
                st.download_button(
                    label="📥 Baixar Planilha de Auditoria (.xlsx)",
                    data=output.getvalue(),
                    file_name=f"AUDITORIA_RET_{uploaded_file.name.split('.')[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Conferência visual rápida
                st.divider()
                st.write("### 🔍 Prévia dos Dados Processados")
                st.dataframe(df_result.head(100))
            else:
                st.error("Não foi possível decifrar o conteúdo do arquivo. Verifique se ele não está corrompido.")

    except Exception as e:
        st.error(f"Ocorreu um erro técnico: {e}")
        st.info("Dica: Certifique-se de que o arquivo não está aberto em outro programa durante o upload.")
