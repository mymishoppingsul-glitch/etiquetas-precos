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
st.set_page_config(page_title="MYMI STORE - Etiquetas", page_icon="🏷️", layout="wide")

st.title("🏷️ Gerador de Etiquetas de Vitrine - Padrão MYMI STORE")
st.markdown("Cole o texto do WhatsApp abaixo para gerar o PDF com as etiquetas ampliadas, limpas e com a logo oficial.")

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
    if not empty_line := not linha or "TROCA DE PREÇO" in linha.upper():
        if empty_line:
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
    st.success(f"Sucesso! {len(produtos_etiquetas)} etiquetas prontas para gerar.")
    st.table(produtos_etiquetas)
    
    # Motor de desenho manual vetorial com ampliação e destaque máximo
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    
    # Medidas oficiais das etiquetas (Grade 3x4 = 12 por página)
    LARGURA_ET = 5.8 * 28.346
    ALTURA_ET = 5.4 * 28.346
    
    MARGEM_X = 25
    MARGEM_Y = 30
    ESPACO_X = 12
    ESPACO_Y = 18
    
    # Cores Ajustadas: Laranja mais aberto/claro e chamativo
    COR_LARANJA_CLARO = HexColor("#FF6600")  # Laranja comercial limpo e aberto
    COR_AMARELO_DESTAQUE = HexColor("#FFCC00") # Círculo do 18X expandido
    COR_PRETO = HexColor("#000000")
    COR_BRANCO = HexColor("#FFFFFF")
    
    x_atual = MARGEM_X
    y_atual = letter - MARGEM_Y - ALTURA_ET
    
    for idx, p in enumerate(produtos_etiquetas):
        if idx > 0 and idx % 12 == 0:
            c.showPage()
            x_atual = MARGEM_X
            y_atual = letter - MARGEM_Y - ALTURA_ET
        elif idx > 0 and idx % 3 == 0:
            x_atual = MARGEM_X
            y_atual -= (ALTURA_ET + ESPACO_Y)
            
        # 1. Fundo geral da etiqueta (Laranja claro e limpo)
        c.setFillColor(COR_LARANJA_CLARO)
        c.setStrokeColor(COR_LARANJA_CLARO)
        c.roundRect(x_atual, y_atual, LARGURA_ET, ALTURA_ET, 10, fill=True, stroke=True)
        
        # 2. Caixa branca do topo (Nome do Produto ampliado)
        c.setFillColor(COR_BRANCO)
        c.setStrokeColor(COR_PRETO)
        c.setLineWidth(0.6)
        c.roundRect(x_atual + 8, y_atual + ALTURA_ET - 32, LARGURA_ET - 16, 24, 6, fill=True, stroke=True)
        
        c.setFillColor(COR_PRETO)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(x_atual + (LARGURA_ET / 2), y_atual + ALTURA_ET - 22, p['nome'])
        
        # 3. Círculo Amarelo Expandido do "18X" (Maior destaque à esquerda)
        c.setFillColor(COR_AMARELO_DESTAQUE)
        c.setStrokeColor(COR_BRANCO)
        c.setLineWidth(1.2)
        c.circle(x_atual + 26, y_atual + 54, 15, fill=True, stroke=True)
        
        c.setFillColor(COR_BRANCO)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x_atual + 26, y_atual + 50, "18X")
        
        # 4. VALOR DA PARCELA GIGANTE E CENTRALIZADO (Eliminando espaço vazio)
        c.setFillColor(COR_PRETO)
        c.setFont("Helvetica-Bold", 26)  # Fonte muito maior para chamar atenção
        c.drawString(x_atual + 64, y_atual + 44, p['parcela'])
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_atual + 48, y_atual + 56, "R$")
        
        # 5. Selo à direita ("NO CARTÃO DE CRÉDITO")
        c.setFillColor(COR_PRETO)
        c.setFont("Helvetica-Bold", 5.5)
        c.drawString(x_atual + 116, y_atual + 54, "NO CARTÃO")
        c.drawString(x_atual + 116, y_atual + 48, "DE CRÉDITO")
        
        # 6. Faixa Preta Horizontal Reta (Preço Total Limpo e sem cortes)
        c.setFillColor(COR_PRETO)
        c.rect(x_atual, y_atual + 18, LARGURA_ET, 18, fill=True, stroke=False)
        
        c.setFillColor(COR_BRANCO)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_atual + 24, y_atual + 23, p['total'])  # CORREGIDO: Sem nenhuma linha branca cruzando por cima!
        
        # 7. RODAPÉ OFICIAL: Logo MYMI STORE à esquerda e SEM JUROS à direita
        c.setFillColor(COR_PRETO)
        
        # Logo da Loja integrada
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_atual + 10, y_atual + 5, "MYMI STORE")
        
        # Selo sem juros normalizado
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(x_atual + LARGURA_ET - 10, y_atual + 3, "JUROS")
        c.drawRightString(x_atual + LARGURA_ET - 10, y_atual + 11, "SEM")
        
        x_atual += (LARGURA_ET + ESPACO_X)
        
    c.save()
    
    st.markdown("---")
    st.subheader("📥 Exportar Resultados")
    st.download_button(
        label="📥 Baixar PDF de Etiquetas Oficial MYMI STORE (Grade 3x4)",
        data=pdf_buffer.getvalue(),
        file_name="etiquetas_vitrine_mymi_store.pdf",
        mime="application/pdf",
        use_container_width=True
    )
