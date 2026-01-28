import pdfplumber
import pandas as pd
import streamlit as st
import io

def converter_pdf_para_excel(pdf_file, excel_path):
    all_data = []
    
    # Abre o arquivo vindo do Streamlit (BytesIO)
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                df_page = pd.DataFrame(table[1:], columns=table[0])
                all_data.append(df_page)
    
    if all_data:
        df_final = pd.concat(all_data, ignore_index=True)
        df_final = df_final.astype(str)
        
        # Cria um buffer para o Excel para permitir o download no Streamlit
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, index=False)
        return output.getvalue()
    else:
        return None

# Interface Streamlit
st.title("Conversor de PDF RET")

uploaded_file = st.file_uploader("Escolha o arquivo PDF", type="pdf")

if uploaded_file is not None:
    # Chama a função passando o arquivo carregado
    excel_data = converter_pdf_para_excel(uploaded_file, "Relatorio_Convertido.xlsx")
    
    if excel_data:
        st.success("Conversão concluída!")
        st.download_button(
            label="Baixar Excel",
            data=excel_data,
            file_name="Relatorio_Convertido.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Nenhuma tabela encontrada no PDF.")
