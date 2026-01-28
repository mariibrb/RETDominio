import streamlit as st

def aplicar_estilo_rihanna_sentinela():
    """
    Aplica o estilo 'Sentinela' inspirado na Rihanna:
    Fundo escuro, detalhes em dourado e fontes de alta visibilidade.
    """
    st.markdown(
        """
        <style>
        /* IMPORTANDO FONTES LUXUOSAS */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Roboto:wght@300;400;700&display=swap');

        /* CONFIGURAÇÃO DO CORPO (A Pele do App) */
        .stApp {
            background-color: #0b0b0b;
            color: #e0e0e0;
            font-family: 'Roboto', sans-serif;
        }

        /* CABEÇALHO SENTINELA (Estilo Diamond) */
        h1 {
            color: #d4af37 !important;
            font-family: 'Playfair Display', serif;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 5px;
            border-bottom: 2px solid #d4af37;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        /* CARTÕES E CONTAINERS (Organização por Blocos) */
        div.stMarkdown {
            color: #ffffff;
        }

        /* BOTÕES PERSONALIZADOS (O Batom Fenty) */
        div.stButton > button {
            background-color: #d4af37;
            color: #000000;
            font-weight: bold;
            border-radius: 5px;
            border: none;
            padding: 15px 30px;
            width: 100%;
            transition: all 0.3s ease;
            text-transform: uppercase;
        }

        div.stButton > button:hover {
            background-color: #ffffff;
            color: #000000;
            box-shadow: 0px 0px 15px 2px #d4af37;
            transform: translateY(-2px);
        }

        /* UPLOAD DE ARQUIVOS (O Primer de Luxo) */
        section[data-testid="stFileUploadDropzone"] {
            background-color: #1a1a1a;
            border: 2px dashed #d4af37 !important;
            border-radius: 10px;
            padding: 40px;
        }

        /* MENSAGENS DE SUCESSO (O Glow Final) */
        div[data-testid="stNotification"] {
            background-color: #000000;
            color: #d4af37;
            border: 1px solid #d4af37;
        }

        /* ESCONDER O MENU PADRÃO PARA MAIOR IMERSÃO */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )
