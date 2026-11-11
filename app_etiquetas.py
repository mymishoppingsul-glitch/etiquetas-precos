import os
import re
import streamlit as st

# Configuração da página do navegador
st.set_page_config(page_title="MMYMI - Etiquetas de Vitrine", page_icon="🏷️", layout="wide")

st.title("🏷️ Gerador de Etiquetas de Vitrine - Layout Oficial 18X")
st.markdown("Cole o texto do WhatsApp abaixo. O sistema gerará a folha de etiquetas pronta em tamanho A4 para impressão.")

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
        
        txt_total = f"R$ {total_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        txt_parcela = f"{parcela_float:.2f}".replace(".", ",")
        
        produtos_etiquetas.append({
            "nome": nome_prod,
            "total": txt_total,
            "parcela": txt_parcela
        })
    except:
        continue

if produtos_etiquetas:
    st.success(f"{len(produtos_etiquetas)} produtos prontos para impressão.")
    
    # Injeta a folha de estilo que desenha a etiqueta idêntica ao modelo físico enviado
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
                gap: 10px !important;
                padding: 10px !important;
            }
        }
        .grade-principal {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
            background-color: #ffffff;
        }
        .etiqueta-loja {
            border: 2px solid #FF8C00;
            background-color: #000000;
            font-family: 'Arial Black', sans-serif;
            overflow: hidden;
            width: 100%;
            max-width: 280px;
            margin: 0 auto;
        }
        .faixa-laranja-topo {
            background-color: #FF8C00;
            color: #ffffff;
            text-align: center;
            padding: 6px 4px;
            font-size: 11px;
            font-weight: 900;
            text-transform: uppercase;
            border-bottom: 2px solid #ffffff;
            letter-spacing: 0.5px;
        }
        .bloco-centro-preto {
            background-color: #000000;
            padding: 8px 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .texto-18x-bold {
            color: #FF8C00;
            font-size: 26px;
            font-weight: 900;
            font-style: italic;
            margin-right: 4px;
        }
        .texto-rs-white {
            color: #ffffff;
            font-size: 11px;
            font-weight: bold;
            vertical-align: super;
            margin-right: 2px;
        }
        .texto-valor-parcela {
            color: #ffffff;
            font-size: 28px;
            font-weight: 900;
            font-style: italic;
        }
        .selo-cartao-credito {
            background-color: #FF8C00;
            color: #000000;
            font-size: 6px;
            font-weight: 900;
            text-align: center;
            padding: 3px;
            line-height: 7px;
            border-radius: 2px;
            width: 65px;
        }
        .selo-cartao-credito span {
            color: #ffffff;
            display: block;
        }
        .faixa-inferior-diagonal {
            background: linear-gradient(135deg, #FF8C00 50%, #FF8C00 50%, #FF9900 50.1%);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 10px;
            border-top: 1px solid #ffffff;
        }
        .preco-total-riscado {
            color: #000000;
            font-size: 14px;
            font-weight: 900;
            background-color: #FF9900;
            padding: 2px 6px;
            border-radius: 4px;
        }
        .texto-sem-juros-tarja {
            color: #000000;
            font-size: 14px;
            font-weight: 900;
            font-style: italic;
            text-shadow: 0.5px 0.5px 0px #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

    # Monta a estrutura da grade 3x4 idêntica à foto
    html_etiquetas = '<div class="grade-principal">'
    for p in produtos_etiquetas:
        html_etiquetas += f"""
        <div class="etiqueta-loja">
            <div class="faixa-laranja-topo">{p['nome']}</div>
            <div class="bloco-centro-preto">
                <div>
                    <span class="texto-18x-bold">18X</span>
                    <span class="texto-rs-white">R$</span>
                    <span class="texto-valor-parcela">{p['parcela']}</span>
                </div>
                <div class="selo-cartao-credito">
                    NO CARTÃO
                    <span>DE CRÉDITO</span>
                </div>
            </div>
            <div class="faixa-inferior-diagonal">
                <div class="preco-total-riscado">{p['total']}</div>
                <div class="texto-sem-juros-tarja">SEM JUROS</div>
            </div>
        </div>
        """
    html_etiquetas += '</div>'
    
    st.markdown(html_etiquetas, unsafe_allow_html=True)
    
    st.markdown("---")
    st.warning("🖨️ **COMO IMPRIMIR / SALVAR EM PDF:** Pressione **Ctrl + P** no teclado do computador. Na tela que abrir, mude o destino para **'Salvar como PDF'** ou selecione a sua impressora física de etiquetas.")
