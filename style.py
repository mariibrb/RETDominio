import streamlit as st

def aplicar_estilo_rihanna():
    """
    Aplica o visual Rihanna: Elegância, Contraste e Luxo.
    """
    st.markdown(
        """
        <style>
        /* FUNDO E TEXTO PRINCIPAL */
        .stApp {
            background-color: #000000;
            color: #FFFFFF;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* TÍTULOS EM DOURADO (Diamond Style) */
        h1, h2, h3 {
            color: #D4AF37 !important;
            text-transform: uppercase;
            letter-spacing: 3px;
            text-shadow: 2px 2px 4px #1A1A1A;
        }

        /* BOTÃO DE DOWNLOAD (O Stunna Lip Paint) */
        div.stButton > button {
            background-color: #D4AF37;
            color: #000000;
            border-radius: 50px;
            border: 2px solid #D4AF37;
            font-weight: bold;
            padding: 0.6rem 2rem;
            transition: 0.5s;
        }

        div.stButton > button:hover {
            background-color: #FFFFFF;
            border-color: #FFFFFF;
            box-shadow: 0px 0px 20px #D4AF37;
            transform: scale(1.02);
        }

        /* ÁREA DE UPLOAD (O Primer) */
        section[data-testid="stFileUploadDropzone"] {
            background-color: #1A1A1A;
            border: 2px dashed #D4AF37 !important;
            border-radius: 15px;
        }

        /* MENSAGENS DE SUCESSO */
        div[data-testid="stNotification"] {
            background-color: #1A1A1A;
            color: #D4AF37;
            border: 1px solid #D4AF37;
        }
        
        /* BARRA DE PROGRESSO */
        .stProgress > div > div > div > div {
            background-color: #D4AF37;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
