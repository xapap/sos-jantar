import os
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# Configuração da página da aplicação
st.set_page_config(
    page_title="SOS Jantar do Casal",
    page_icon="🍳",
    layout="centered"
)

st.title("🍳 SOS Jantar: O que vamos comer hoje?")
st.caption("Carrega fotos do frigorífico, despensa ou talões e deixa a IA decidir sem discussões.")

# Obter a chave da API de forma segura:
# Primeiro tenta nos Secrets do Streamlit Cloud, depois nas variáveis de ambiente locais
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif os.environ.get("GEMINI_API_KEY"):
    api_key = os.environ.get("GEMINI_API_KEY")

# Upload de múltiplas fotos (frigorífico, gavetas, despensa, talão)
uploaded_files = st.file_uploader(
    "Tira ou envia fotos (frigorífico, prateleiras, gavetas, despensa, talão...)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

# Miniaturas das fotos enviadas
if uploaded_files:
    st.write(f"**{len(uploaded_files)} foto(s) pronta(s) para análise:**")
    cols = st.columns(min(len(uploaded_files), 4))
    for idx, file in enumerate(uploaded_files):
        with cols[idx % 4]:
            st.image(file, use_container_width=True)

# Campo opcional para restrições de última hora
observacoes = st.text_input("Algum detalhe extra? (ex.: estamos com pressa, hoje não apetece massa, etc.)")

# Botão principal
if st.button("Decidir o Jantar 🪄", type="primary", disabled=not uploaded_files):
    if not api_key:
        st.error("Chave da API não configurada! Adiciona GEMINI_API_KEY nos Secrets do Streamlit.")
    else:
        with st.spinner("A analisar os ingredientes e a preparar o menu..."):
            try:
                # 1. Carregar as imagens
                pil_images = [Image.open(f) for f in uploaded_files]

                # 2. Inicializar o cliente com a chave guardada
                client = genai.Client(api_key=api_key)

                # 3. Prompt de mediação
                prompt = f"""
                És o mediador culinário oficial de um casal cansado ao fim de um dia de trabalho.
                
                Analisa o conjunto de fotos anexadas (podem incluir prateleiras do frigorífico, gavetas, armários de despensa ou talões de compras de supermercado).
                
                Detalhe opcional dado pelo casal: "{observacoes if observacoes else 'Nenhum'}"
                
                A tua tarefa:
                1. Identificar ingredientes frescos, sobras visíveis e produtos nos talões.
                2. Apresentar exatamente 3 opções práticas:
                   - **Opção 1: 'Ultra-Rápida'** (15 a 20 min, o mínimo de esforço e louça).
                   - **Opção 2: 'Conforto da Casa'** (um prato reconfortante com os ingredientes principais).
                   - **Opção 3: 'Desperdício Zero'** (focada em gastar o que parece mais urgente consumir).
                
                Regras:
                - Assume apenas básicos essenciais de despensa (azeite, alho, cebola, sal, pimenta, massa ou arroz).
                - Se mencionares um produto detetado no talão ou despensa, refere-o de passagem (ex.: "usa as natas do talão").
                - Responde em Português de Portugal, com passos simples e curtos por opção.
                """

                # 4. Chamada ao modelo atualizado
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[*pil_images, prompt],
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                    )
                )

                # 5. Apresentação do menu final
                st.success("Menu decidido!")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Ocorreu um erro ao processar: {e}")