import streamlit as st

def aplicar_estilo_rihanna():
    """
    Aplica o 'Fenty Glow' no seu app: fundo escuro luxuoso, 
    detalhes em dourado e fontes elegantes.
    """
    st.markdown(
        """
        <style>
        /* 1. FUNDO PRINCIPAL (A Pele do App) */
        .stApp {
            background-color: #000000;
            color: #FFFFFF;
        }

        /* 2. BARRA LATERAL (O Closet) */
        [data-testid="stSidebar"] {
            background-color: #1A1A1A;
            border-right: 2px solid #D4AF37;
        }

        /* 3. TÍTULOS (O Brilho/Diamond) */
        h1, h2, h3 {
            color: #D4AF37 !0important;
            font-family: 'Playfair Display', serif;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* 4. BOTÕES (O Batom/Fenty Stunna) */
        div.stButton > button {
            background-color: #D4AF37;
            color: #000000;
            border-radius: 20px;
            border: none;
            font-weight: bold;
            transition: 0.3s;
            width: 100%;
        }

        div.stButton > button:hover {
            background-color: #FFFFFF;
            color: #000000;
            box-shadow: 0px 0px 15px #D4AF37;
        }

        /* 5. CAMPOS DE UPLOAD (O Primer) */
        section[data-testid="stFileUploadDropzone"] {
            background-color: #1A1A1A;
            border: 1px dashed #D4AF37;
            border-radius: 10px;
        }

        /* 6. SUCESSO E ALERTAS */
        .stAlert {
            background-color: #1A1A1A;
            color: #D4AF37;
            border: 1px solid #D4AF37;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
