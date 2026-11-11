import re
import streamlit as st

# Configuração da página do navegador
st.set_page_config(page_title="Gerador de Etiquetas", page_icon="🏷️", layout="wide")

st.title("🏷️ Gerador de Etiquetas de Preço - 18x Sem Juros")
st.markdown("Cole a lista de preços do WhatsApp abaixo. O sistema calculará as parcelas e montará o layout estruturado.")

texto_padrao = """TROCA DE PREÇO 05.11.26

POCO M8 5G 512/8 - R$2.299,90
REALME C73 128/4 - R$1.399,90
REALME C100I 256/4 - R$1.649,90
REDMI 15C 256/8 - R$1.599,90
POCO C85 256/8 - R$1.749,90"""

entrada_texto = st.text_area("Cole as informações do WhatsApp aqui:", value=texto_padrao, height=200)

# Processamento do texto do WhatsApp de forma limpa
linhas = entrada_texto.split('\n')
produtos_etiquetas = []

for linha in linhas:
    linha = linha.strip()
    if not linha or "TROCA DE PREÇO" in linha.upper():
        continue
    
    if "-" in linha:
        partes = linha.split("-")
        nome_prod = partes[0].strip().upper()
        preco_str = partes[1].strip()
    else:
        match = re.search(r'(.*?)(?:R\$)?\s*([\d\.,]+)$', linha)
        if match:
            nome_prod = match.group(1).strip().upper()
            preco_str = match.group(2).strip()
        else:
            continue
            
    preco_limpo = preco_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        total_float = float(preco_limpo)
        parcela_float = total_float / 18
        
        txt_total = f"R${total_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        txt_parcela = f"R${parcela_float:.2f}".replace(".", ",")
        
        produtos_etiquetas.append({
            "nome": nome_prod,
            "total": txt_total,
            "parcela": txt_parcela
        })
    except:
        continue

if produtos_etiquetas:
    st.success(f"{len(produtos_etiquetas)} produtos processados.")
    
    # Injeta estilos CSS para garantir que a impressão saia idêntica ao PDF original (Grade 3x4)
    st.markdown("""
        <style>
        @media print {
            header, footer, [data-testid="stSidebar"], [data-testid="stDecoration"], .stTextArea, .stAlert, h1, p {
                display: none !important;
            }
            .stMainBlockContainer {
                padding: 0 !important;
                margin: 0 !important;
            }
            .grid-impressao {
                display: grid !important;
                grid-template-columns: repeat(3, 1fr) !important;
                gap: 15px !important;
                page-break-inside: avoid !important;
            }
        }
        .grid-impressao {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 20px;
        }
        .etiqueta-box {
            border: 3px solid #FF8C00;
            border-radius: 8px;
            background-color: white;
            font-family: 'Arial', sans-serif;
            overflow: hidden;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .etiqueta-header {
            background-color: #FF8C00;
            color: white;
            text-align: center;
            padding: 8px;
            font-weight: bold;
            font-size: 13px;
            min-height: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-transform: uppercase;
        }
        .etiqueta-body {
            background-color: #000000;
            padding: 12px;
            color: white;
        }
        .linha-parcela {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .txt-18x {
            color: #FF8C00;
            font-size: 26px;
            font-weight: 900;
        }
        .bloco-preco-parc {
            text-align: right;
        }
        .txt-val-parc {
            color: white;
            font-size: 22px;
            font-weight: bold;
        }
        .txt-sub-cartao {
            color: #FF8C00;
            font-size: 7px;
            font-weight: bold;
            letter-spacing: 0.5px;
            display: block;
            margin-top: -2px;
        }
        .linha-rodape {
            margin-top: 8px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }
        .txt-total-original {
            color: #A0A0A0;
            font-size: 13px;
            font-weight: bold;
            text-decoration: line-through;
            opacity: 0.7;
        }
        .txt-sem-juros {
            color: #FF8C00;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 1px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Renderiza a grade estruturada de etiquetas na tela
    html_grade = '<div class="grid-impressao">'
    for p in produtos_etiquetas:
        html_grade += f"""
        <div class="etiqueta-box">
            <div class="etiqueta-header">{p['nome']}</div>
            <div class="etiqueta-body">
                <div class="linha-parcela">
                    <span class="txt-18x">18X</span>
                    <div class="bloco-preco-parc">
                        <span class="txt-val-parc">{p['parcela']}</span>
                        <span class="txt-sub-cartao">NO CARTÃO DE CRÉDITO</span>
                    </div>
                </div>
                <div class="linha-rodape">
                    <span class="txt-total-original">{p['total']}</span>
                    <span class="txt-sem-juros">SEM JUROS</span>
                </div>
            </div>
        </div>
        """
    html_grade += '</div>'
    
    st.markdown(html_grade, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 **Para salvar o PDF ou Imprimir:** Pressione **Ctrl + P** no seu teclado (ou clique com o botão direito na página e selecione 'Imprimir'). Na tela de impressão, defina o destino como 'Salvar como PDF' ou escolha a sua impressora física.")
