import os
import re
import io
import streamlit as st

# Importações protegidas do ReportLab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
except ModuleNotFoundError:
    st.error("O servidor está instalando os componentes de PDF. Por favor, clique em 'Manage App' no canto inferior direito e selecione 'Reboot App' para ativar.")
    st.stop()

# Configuração da página do navegador
st.set_page_config(page_title="MMYMI - Etiquetas de Vitrine", page_icon="🏷️", layout="wide")

st.title("🏷️ Gerador de Etiquetas de Vitrine - Layout Oficial 18X")
st.markdown("Cole o texto do WhatsApp abaixo para gerar o PDF com as etiquetas idênticas ao modelo da loja.")

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
    st.table(produtos_etiquetas)
    
    pdf_buffer = io.BytesIO()
    # Configuração de folha A4 com margens seguras para 12 etiquetas (grade 3x4)
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=25, bottomMargin=20)
    story = []
    
    # Cores exatas do modelo da loja
    COR_LARANJA = colors.HexColor("#FF8C00")
    COR_PRETO = colors.HexColor("#000000")
    
    # Estilos de fontes milimetricamente ajustados
    style_nome = ParagraphStyle('Nome', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white, alignment=1, leading=10)
    style_18x = ParagraphStyle('Txt18x', fontName='Helvetica-Bold', fontSize=18, textColor=COR_LARANJA, alignment=0, leading=18)
    style_parcela = ParagraphStyle('TxtParc', fontName='Helvetica-Bold', fontSize=18, textColor=colors.white, alignment=0, leading=18)
    style_selo_txt = ParagraphStyle('TxtSelo', fontName='Helvetica-Bold', fontSize=5, textColor=colors.white, alignment=1, leading=6)
    style_total = ParagraphStyle('TxtTotal', fontName='Helvetica-Bold', fontSize=11, textColor=COR_PRETO, alignment=0, leading=11)
    style_sem_juros = ParagraphStyle('TxtSJ', fontName='Helvetica-Bold', fontSize=11, textColor=COR_PRETO, alignment=2, leading=11)

    # Dimensões da etiqueta física (em pontos de PDF)
    LARGURA_ETIQUETA = 5.8 * 28.346  
    ALTURA_CABECALHO = 0.5 * 28.346
    ALTURA_CENTRAL = 1.1 * 28.346
    ALTURA_RODAPE = 0.5 * 28.346
    
    lista_etiquetas_finais = []
    
    for p in produtos_etiquetas:
        # 1. LINHA SUPERIOR (Nome do Produto em fundo Laranja)
        row1 = Table([[Paragraph(p['nome'], style_nome)]], colWidths=[LARGURA_ETIQUETA], rowHeights=[ALTURA_CABECALHO])
        row1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_LARANJA),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        # Selo interno "NO CARTÃO DE CRÉDITO" com fundo Laranja
        selo_interno = Table([
            [Paragraph("NO CARTÃO", style_selo_txt)],
            [Paragraph("DE CRÉDITO", style_selo_txt)]
        ], colWidths=[LARGURA_ETIQUETA * 0.26], rowHeights=[7, 7])
        selo_interno.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_LARANJA),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        # 2. LINHA CENTRAL (Fundo Preto com Parcelamento e o Selo)
        conteudo_centro = [
            Paragraph(f"18X R$", style_18x),
            Paragraph(p['parcela'], style_parcela),
            selo_interno
        ]
        row2 = Table([conteudo_centro], colWidths=[LARGURA_ETIQUETA * 0.36, LARGURA_BLOCO_LARGURA * 0.36 if 'LARGURA_BLOCO_LARGURA' in locals() else LARGURA_ETIQUETA * 0.36, LARGURA_ETIQUETA * 0.28], rowHeights=[ALTURA_CENTRAL])
        row2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_PRETO),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (2,0), (2,0), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        
        # 3. LINHA INFERIOR (Fundo Laranja com Preço Total e SEM JUROS)
        conteudo_rodape = [
            Paragraph(p['total'], style_total),
            Paragraph("SEM JUROS", style_sem_juros)
        ]
        row3 = Table([conteudo_rodape], colWidths=[LARGURA_ETIQUETA * 0.5, LARGURA_ETIQUETA * 0.5], rowHeights=[ALTURA_RODAPE])
        row3.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_LARANJA),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        
        # EMPACOTAMENTO DA ETIQUETA COMPLETA
        etiqueta_montada = Table([[row1], [row2], [row3]], colWidths=[LARGURA_ETIQUETA], rowHeights=[ALTURA_CABECALHO, ALTURA_CENTRAL, ALTURA_RODAPE])
        etiqueta_montada.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1.5, COR_LARANJA), # Contorno externo laranja
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        lista_etiquetas_finais.append(etiqueta_montada)
        
    # Organização matemática da grade (3 Colunas por Linha fixas)
    grade_linhas = []
    for idx in range(0, len(lista_etiquetas_finais), 3):
        trio = lista_etiquetas_finais[idx:idx+3]
        while len(trio) < 3:
            trio.append(Spacer(1, LARGURA_ETIQUETA))
        grade_linhas.append(trio)
        
    tabela_mestre = Table(grade_linhas, colWidths=[LARGURA_ETIQUETA, LARGURA_ETIQUETA, LARGURA_ETIQUETA])
    tabela_mestre.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),  # Margem para guilhotina horizontal
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16), # Margem para guilhotina vertical
        ('TOPPADDING', (0,0), (-1,-1), 16),
    ]))
    
    story.append(KeepTogether([tabela_mestre]))
    doc.build(story)
    
    st.markdown("---")
    st.subheader("📥 Exportar Resultados")
    st.download_button(
        label="📥 Clique aqui para baixar o PDF Oficial de Etiquetas (Grade 3x4)",
        data=pdf_buffer.getvalue(),
        file_name="folha_etiquetas_18x_oficial.pdf",
        mime="application/pdf",
        use_container_width=True
    )
