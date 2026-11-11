import os
import re
import io
import streamlit as st

# Importações do ReportLab protegidas
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
except ModuleNotFoundError:
    st.error("O servidor está processando a ativação gráfica. Por favor, aguarde alguns segundos e atualize a página (F5).")
    st.stop()

# Configuração da página do navegador
st.set_page_config(page_title="MMYMI - Etiquetas Oficiais", page_icon="🏷️", layout="wide")

st.title("🏷️ Gerador de Etiquetas de Vitrine - Correção de Layout")
st.markdown("Cole o texto do WhatsApp abaixo para gerar o PDF com o design idêntico ao modelo reto da tela.")

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
    st.success(f"{len(produtos_etiquetas)} etiquetas geradas com sucesso.")
    
    # Motor de desenho manual vetorial corrigido
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    
    # Medidas das etiquetas (Grade 3x4 = 12 por página)
    LARGURA_ET = 5.8 * 28.346
    ALTURA_ET = 5.4 * 28.346
    
    MARGEM_X = 25
    MARGEM_Y = 30
    ESPACO_X = 12
    ESPACO_Y = 18
    
    # Cores exatas extraídas da imagem
    COR_LARANJA = HexColor("#FF3B00")  # Vermelho/Laranja de fundo
    COR_AMARELO = HexColor("#FFB300")   # Círculo do 18X
    COR_PRETO = HexColor("#000000")
    COR_BRANCO = HexColor("#FFFFFF")
    
    x_atual = MARGEM_X
    y_atual = letter[1] - MARGEM_Y - ALTURA_ET
    
    for idx, p in enumerate(produtos_etiquetas):
        if idx > 0 and idx % 12 == 0:
            c.showPage()
            x_atual = MARGEM_X
            y_atual = letter[1] - MARGEM_Y - ALTURA_ET
        elif idx > 0 and idx % 3 == 0:
            x_atual = MARGEM_X
            y_atual -= (ALTURA_ET + ESPACO_Y)
            
        # 1. Fundo geral da etiqueta (Laranja com cantos arredondados)
        c.setFillColor(COR_LARANJA)
        c.setStrokeColor(COR_LARANJA)
        c.roundRect(x_atual, y_atual, LARGURA_ET, ALTURA_ET, 10, fill=True, stroke=True)
        
        # 2. Caixa branca do topo (Nome do Produto)
        c.setFillColor(COR_BRANCO)
        c.setStrokeColor(COR_PRETO)
        c.setLineWidth(0.5)
        c.roundRect(x_atual + 8, y_atual + ALTURA_ET - 32, LARGURA_ET - 16, 24, 6, fill=True, stroke=True)
        
        # Texto do produto centralizado na caixinha branca
        c.setFillColor(COR_PRETO)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x_atual + (LARGURA_ET / 2), y_atual + ALTURA_ET - 22, p['nome'])
        
        # 3. Círculo Amarelo do "18X" à esquerda
        c.setFillColor(COR_AMARELO)
        c.setStrokeColor(COR_BRANCO)
        c.setLineWidth(1)
        c.circle(x_atual + 24, y_atual + 56, 12, fill=True, stroke=True)
        
        c.setFillColor(COR_BRANCO)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x_atual + 24, y_atual + 53, "18X")
        
        # 4. Valor da Parcela no centro
        c.setFillColor(COR_PRETO)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(x_atual + 58, y_atual + 48, p['parcela'])
        
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x_atual + 44, y_atual + 54, "R$")
        
        # 5. Selo à direita ("NO CARTÃO DE CRÉDITO") em linhas retas normais
        c.setFillColor(COR_PRETO)
        c.setFont("Helvetica-Bold", 5.5)
        c.drawString(x_atual + 116, y_atual + 56, "NO CARTÃO")
        c.drawString(x_atual + 116, y_atual + 50, "DE CRÉDITO")
        
        # 6. Faixa Preta Horizontal Reta (Preço Total)
        c.setFillColor(COR_PRETO)
        c.rect(x_atual, y_atual + 18, LARGURA_ET, 18, fill=True, stroke=False)
        
        # Texto do preço original dentro da faixa preta
        c.setFillColor(COR_BRANCO)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_atual + 26, y_atual + 23, p['total'])
        c.setFont("Helvetica-Bold", 6)
        c.drawString(x_atual + 12, y_atual + 25, "R$")
        
        # Linha branca de rasura em cima do preço total
        c.setStrokeColor(COR_BRANCO)
        c.setLineWidth(1.2)
        c.line(x_atual + 10, y_atual + 26, x_atual + 85, y_atual + 26)
        
        # 7. Texto "SEM JUROS" no Rodapé Laranja (Corrigido para escrita normal)
        c.setFillColor(COR_PRETO)
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(x_atual + LARGURA_ET - 12, y_atual + 8, "JUROS")
        c.drawRightString(x_atual + LARGURA_ET - 12, y_atual + 18, "SEM")
        
        x_atual += (LARGURA_ET + ESPACO_X)
        
    c.save()
    
    st.markdown("---")
    st.subheader("📥 Exportar Resultados")
    st.download_button(
        label="📥 Baixar PDF de Etiquetas Oficial Corrigido (Grade 3x4)",
        data=pdf_buffer.getvalue(),
        file_name="folha_etiquetas_mymi_corrigida.pdf",
        mime="application/pdf",
        use_container_width=True
    )
