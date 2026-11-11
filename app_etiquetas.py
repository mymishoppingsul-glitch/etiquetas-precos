import re
import streamlit as st

# Configuração da página do navegador
st.set_page_config(page_title="MMYMI - Etiquetas de Vitrine", page_icon="🏷️", layout="wide")

st.title("🏷️ Gerador de Etiquetas de Vitrine - Layout Oficial 18X")
st.markdown("Cole o texto do WhatsApp abaixo para gerar o painel com as etiquetas idênticas ao modelo da loja.")

texto_padrao = """TROCA DE PREÇO 05.11.26

POCO M8 5G 512/8 - R$2.299,90
REALME C73 128/4 - R$1.399,90
REALME C100I 256/4 - R$1.649,90
REDMI 15C 256/8 - R$1.599,90
POCO C85 256/8 - R$1.749,90"""

entrada_texto = st.text_area("Cole as informações do WhatsApp aqui:", value=texto_padrao, height=200)

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
        txt_parcela = f"{parcela_float:.2f}".replace(".", ",")
        
        produtos_etiquetas.append({
            "nome": nome_prod,
            "total": txt_total,
            "parcela": txt_parcela
        })
    except:
        continue

if produtos_etiquetas:
    st.success(f"Sucesso! {len(produtos_etiquetas)} produtos processados.")
    
    # CSS avançado para replicar exatamente o design geométrico e as cores do PDF
    st.markdown("""
        <style>
        @media print {
            header, footer, [data-testid="stSidebar"], [data-testid="stDecoration"], .stTextArea, .stAlert, h1, p, hr {
                display: none !important;
            }
            .stMainBlockContainer {
                padding: 0 !important;
                margin: 0 !important;
            }
            .grade-principal {
                display: grid !important;
                grid-template-columns: repeat(3, 1fr) !important;
                gap: 15px !important;
                padding: 10px !important;
                page-break-inside: avoid !important;
            }
        }
        .grade-principal {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 20px;
            background-color: #ffffff;
        }
        .etiqueta-container {
            border: 2px solid #FF8C00;
            background-color: #000000;
            font-family: 'Arial Black', 'Impact', sans-serif;
            width: 100%;
            box-sizing: border-box;
        }
        .etiqueta-topo-laranja {
            background-color: #FF8C00;
            color: #ffffff;
            text-align: center;
            padding: 8px 4px;
            font-size: 13px;
            font-weight: 900;
            text-transform: uppercase;
            border-bottom: 2px solid #ffffff;
            letter-spacing: 0.5px;
        }
        .etiqueta-meio-preto {
            background-color: #000000;
            padding: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #ffffff;
        }
        .bloco-18x-valores {
            display: flex;
            align-items: baseline;
        }
        .txt-18x {
            color: #FF8C00;
            font-size: 32px;
            font-weight: 900;
            font-style: italic;
            margin-right: 4px;
        }
        .txt-rs {
            color: #ffffff;
            font-size: 12px;
            font-weight: bold;
            margin-right: 3px;
        }
        .txt-valor {
            color: #ffffff;
            font-size: 36px;
            font-weight: 900;
            font-style: italic;
        }
        .bloco-selo-cartao {
            background-color: #FF8C00;
            color: #000000;
            font-size: 7px;
            font-weight: 900;
            text-align: center;
            padding: 4px 6px;
            line-height: 8px;
            border-radius: 2px;
            min-width: 70px;
        }
        .bloco-selo-cartao span {
            color: #ffffff;
            display: block;
        }
        .etiqueta-rodape-laranja {
            background-color: #FF8C00;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 10px;
        }
        .txt-total-bold {
            color: #000000;
            font-size: 16px;
            font-weight: 900;
            background-color: #FFA500;
            padding: 2px 8px;
            border-radius: 3px;
            letter-spacing: -0.5px;
        }
        .txt-sem-juros-bold {
            color: #000000;
            font-size: 18px;
            font-weight: 900;
            font-style: italic;
            letter-spacing: 0.5px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Constrói o HTML puro com o mapeamento exato das posições visuais
    html_etiquetas = '<div class="grade-principal">'
    for p in produtos_etiquetas:
        html_etiquetas += f"""
        <div class="etiqueta-container">
            <div class="etiqueta-topo-laranja">{p['nome']}</div>
            <div class="etiqueta-meio-preto">
                <div class="bloco-18x-valores">
                    <span class="txt-18x">18X</span>
                    <span class="txt-rs">R$</span>
                    <span class="txt-valor">{p['parcela']}</span>
                </div>
                <div class="bloco-selo-cartao">
                    NO CARTÃO
                    <span>DE CRÉDITO</span>
                </div>
            </div>
            <div class="etiqueta-rodape-laranja">
                <div class="txt-total-bold">{p['total']}</div>
                <div class="txt-sem-juros-bold">SEM JUROS</div>
            </div>
        </div>
        """
    html_etiquetas += '</div>'
    
    st.markdown(html_etiquetas, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("🖨️ **COMO SALVAR OU IMPRIMIR:** Pressione **Ctrl + P** no teclado. Mude o destino para **'Salvar como PDF'** ou envie para sua impressora física.")
