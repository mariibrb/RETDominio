import streamlit as st
import pandas as pd
import re
import io

def limpar_e_extrair(conteudo_bruto):
    # 1. Tenta decodificar o "binário" da Domínio de forma ampla
    # O 'replace' substitui símbolos estranhos por um espaço, limpando o caminho
    texto = conteudo_bruto.decode('latin-1', errors='replace')
    
    # Remove caracteres nulos e outros ruídos binários comuns no XLS da Domínio
    texto_limpo = texto.replace('\x00', '').replace('\x01', '')
    
    # Divide o texto em blocos baseando-se no que seriam as "células" do sistema
    # Arquivos da Domínio costumam usar muitos espaços ou caracteres de controle como separadores
    lines = texto_limpo.split('\r')
    if len(lines) < 5: lines = texto_limpo.split('\n')

    processed_rows = []
    current_percent = "0.0"

    for line in lines:
        # 2. Captura o Percentual de Recolhimento
        if "recolhimento efetivo" in line.lower():
            percent_match = re.search(r"(\d+[.,]\d+)", line)
            if percent_match:
                current_percent = percent_match.group(1).replace(',', '.')
            continue

        # 3. Identifica Linhas de Dados
        # Procuramos por: Documento (4-6 dígitos) + Descrição
        # A regex abaixo foca em capturar números de documentos típicos
        parts = re.split(r'\s{2,}', line.strip()) # Divide por grandes espaços
        parts = [p.strip() for p in parts if p.strip()]

        if len(parts) >= 3:
            # Tenta achar o número do documento (ex: 1177, 1181...)
            # Geralmente é o primeiro ou segundo número que aparece
            numeros = [p for p in parts if p.isdigit() and 3 <= len(p) <= 6]
            
            if numeros:
                doc = numeros[0]
                # A descrição do produto costuma ser a parte mais longa da linha
                descricoes = [p for p in parts if len(p) > 15]
                produto = descricoes[0] if descricoes else "PRODUTO NÃO IDENTIFICADO"

                # Monta a estrutura da Aba Python (22 colunas)
                row = [""] * 22
                row[0] = "DATA" # Placeholder (Data original fica difícil no binário)
                row[1] = doc
                row[6] = f"{doc}-{produto}" # ID Único: Documento-Produto
                row[7] = current_percent
                row[10] = produto
                
                # Captura valores (contém vírgula e números)
                valores = [p for p in parts if ',' in p and re.search(r'\d', p)]
                if len(valores) >= 2:
                    row[14] = valores[0] # Valor Produto
                    row[15] = valores[1] # Valor Contábil
                
                processed_rows.append(row)

    return pd.DataFrame(processed_rows)

# --- Interface Streamlit ---
st.set_page_config(page_title="Conversor RET Domínio", layout="wide")
st.title("📂 Conversor RET - Peneira Fiscal")
st.markdown("Esta versão ignora os erros de formato e 'peneira' o texto bruto do arquivo.")

file = st.file_uploader("Suba o arquivo XLS da Domínio aqui")

if file:
    try:
        conteudo = file.read()
        
        with st.spinner('Peneirando dados binários...'):
            df_final = limpar_e_extrair(conteudo)
            
        if not df_final.empty:
            st.success(f"✅ {len(df_final)} itens encontrados!")
            
            csv_ready = df_final.to_csv(index=False, header=False)
            st.download_button(
                label="📥 Baixar CSV Convertido",
                data=csv_ready,
                file_name=f"PROCESSADO_{file.name}.csv",
                mime="text/csv"
            )
            
            st.write("### 🔍 Prévia do ID e Percentual:")
            # Mostra as colunas principais para conferência da Mariana
            st.dataframe(df_final[[1, 6, 7, 10]].rename(columns={1: "Doc", 6: "ID Gerado", 7: "%", 10: "Produto"}))
        else:
            st.error("A peneira não encontrou dados. O arquivo pode estar em um formato binário muito fechado.")
            st.info("Dica: Tente extrair o relatório da Domínio como 'Relatório em Disco' ou 'CSV' se disponível.")

    except Exception as e:
        st.error(f"Erro: {e}")

st.sidebar.markdown("---")
st.sidebar.info("Lógica: Busca padrões de números de nota e descrições longas no meio do código binário.")
