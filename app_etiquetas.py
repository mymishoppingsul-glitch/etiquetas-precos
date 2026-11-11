import os
import re
import io
import streamlit as st

# Importações protegidas do ReportLab para garantir o desenho gráfico
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
except ModuleNotFoundError:
    st.error("O servidor está processando a ativação gráfica. Por favor, aguarde alguns segundos e atualize a página (F5).")
    st.stop()

# Configuração da página do navegador
st.set_page_config(page_title="MMYMI - Etiquetas Oficiais", page_icon="🏷️", layout="wide")

st.title("🏷️ Gerador de Etiquetas de Vitrine - Cópia Fiel do Modelo")
st.markdown("Cole o texto do WhatsApp abaixo para gerar o PDF com o design idêntico ao que você já usa no computador.")

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
    st.success(f"{len(produtos_etiquetas)} etiquetas processadas com sucesso.")
    
    # Motor de desenho manual vetorial para clonar o design da foto
    pdf_buffer = io.BytesIO()
    
    # Criamos a folha tamanho Carta/A4
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    
    # Configurações de tamanho físico de cada etiqueta (Grade 3x4 = 12 por página)
    LARGURA_ET = 5.8 * 28.346
    ALTURA_ET = 5.4 * 28.346
    
    # Margens e espaçamentos da página
    MARGEM_X = 20
    MARGEM_Y = 30
    ESPACO_X = 10
    ESPACO_Y = 15
    
    # Cores Oficiais extraídas da sua imagem
    LARANJA_VIVO = HexColor("#FF5500")
    LARANJA_CLARO = HexColor("#FFA500")
    PRETO_PURO = HexColor("#000000")
    BRANCO_PURO = HexColor("#FFFFFF")
    CINZA_BORDA = HexColor("#D0D0D0")
    
    x_atual = MARGEM_X
    y_atual = letter[1] - MARGEM_Y - ALTURA_ET
    
    for idx, p in enumerate(produtos_etiquetas):
        # Controle de quebra de página automática para caber 12 por folha
        if idx > 0 and idx % 12 == 0:
            c.showPage()
            x_atual = MARGEM_X
            y_atual = letter[1] - MARGEM_Y - ALTURA_ET
        elif idx > 0 and idx % 3 == 0:
            x_atual = MARGEM_X
            y_atual -= (ALTURA_ET + ESPACO_Y)
            
        # -----------------------------------------------------------------
        # DESENHO VETORIAL DA ETIQUETA (A CÓPIA FIEL DA IMAGEM)
        # -----------------------------------------------------------------
        
        # 1. Corpo/Fundo Geral Laranja com cantos arredondados
        c.setFillColor(LARANJA_VIVO)
        c.setStrokeColor(CINZA_BORDA)
        c.setLineWidth(1)
        c.roundRect(x_atual, y_atual, LARGURA_ET, ALTURA_ET, 8, fill=True, stroke=True)
        
        # 2. Cabeçalho Branco Arredondado Interno para o Nome do Produto
        c.setFillColor(BRANCO_PURO)
        c.setStrokeColor(PRETO_PURO)
        c.setLineWidth(0.8)
        c.roundRect(x_atual + 6, y_atual + ALTURA_ET - 34, LARGURA_ET - 12, 28, 6, fill=True, stroke=True)
        
        # Texto do Nome do Produto centralizado na caixinha branca
        c.setFillColor(PRETO_PURO)
        c.setFont("Helvetica-Bold", 8)
        nome_linhas = [p['nome'][i:i+24] for i in range(0, len(p['nome']), 24)]
        if len(nome_linhas) == 1:
            c.drawCentredString(x_atual + (LARGURA_ET / 2), y_atual + ALTURA_ET - 22, nome_linhas[0])
        else:
            c.drawCentredString(x_atual + (LARGURA_ET / 2), y_atual + ALTURA_ET - 18, nome_linhas[0])
            c.drawCentredString(x_atual + (LARGURA_ET / 2), y_atual + ALTURA_ET - 28, nome_linhas[1])
            
        # 3. O Corte Diagonal Preto do Meio (Construção do Polígono Inclinado da foto)
        p_corte = c.beginPath()
        p_corte.moveTo(x_atual, y_atual + 20)                        # Canto inferior esquerdo do corte
        p_corte.lineTo(x_atual + (LARGURA_ET * 0.65), y_atual + 20)  # Segue reto até o início da inclinação
        p_corte.lineTo(x_atual + (LARGURA_ET * 0.85), y_atual + 46)  # Sobe em diagonal para a direita
        p_corte.lineTo(x_atual, y_atual + 46)                        # Volta reto até a borda esquerda
        p_corte.close()
        c.setFillColor(PRETO_PURO)
        c.drawPath(p_corte, fill=True, stroke=False)
        
        # Preço total riscado dentro do polígono inclinado preto
        c.setFillColor(BRANCO_PURO)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_atual + 24, y_atual + 28, p['total'])
        # Desenha o risco preto/cinza por cima do preço total
        c.setStrokeColor(HexColor("#A0A0A0"))
        c.setLineWidth(1.5)
        c.line(x_atual + 22, y_atual + 32, x_atual + 85, y_atual + 32)
        
        # Mini "R$" antes do preço riscado igual ao modelo
        c.setFont("Helvetica-Bold", 6)
        c.drawString(x_atual + 12, y_atual + 28, "RS")
        
        # 4. Elipse Laranja/Amarela do "18X" à esquerda
        c.setFillColor(LARANJA_CLARO)
        c.setStrokeColor(BRANCO_PURO)
        c.setLineWidth(1)
        c.ellipse(x_atual + 8, y_atual + 54, x_atual + 46, y_atual + 76, fill=True, stroke=True)
        
        c.setFillColor(BRANCO_PURO)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(x_atual + 27, y_atual + 60, "18X")
        
        # 5. Preço da Parcela no Centro (Letras pretas e garrafais)
        c.setFillColor(PRETO_PURO)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(x_atual + 62, y_atual + 58, p['parcela'])
        
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x_atual + 50, y_atual + 62, "R$")
        
        # 6. Selo Informativo à Direita ("NO CARTÃO DE CRÉDITO")
        c.setFillColor(PRETO_PURO)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawString(x_atual + 114, y_atual + 66, "NO CARTÃO")
        c.drawString(x_atual + 114, y_atual + 58, "DE CRÉDITO")
        
        # 7. Texto "SEM JUROS" no Rodapé Laranja (Canto inferior direito)
        c.setFillColor(PRETO_PURO)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_atual + 104, y_atual + 4, "SEM")
        c.drawString(x_atual + 100, y_atual + 14, "JUROS")
        
        # Avança para a próxima coluna da grade
        x_atual += (LARGURA_ET + ESPACO_X)
        
    c.save()
    pdf_bytes = pdf_buffer.getvalue()
    
    st.markdown("---")
    st.subheader("📥 Download do Arquivo Oficial")
    st.download_button(
        label="📥 Baixar PDF de Etiquetas Clonado da Foto (Grade 3x4)",
        data=pdf_bytes,
        file_name="folha_etiquetas_mymi_oficial.pdf",
        mime="application/pdf",
        use_container_width=True
    )
