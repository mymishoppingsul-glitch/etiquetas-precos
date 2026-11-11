import os
import re
import io
import streamlit as st

# Importações do ReportLab protegidas
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
except ModuleNotFoundError:
    st.error("O servidor está instalando os componentes de PDF. Por favor, clique em 'Manage App' no canto inferior direito e selecione 'Reboot App' para ativar.")
    st.stop()

# Configuração visual do Streamlit
st.set_page_config(page_title="MMYMI - Etiqueta de Vitrine", page_icon="🏷️", layout="wide")

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
    st.success(f"Sucesso! {len(produtos_etiquetas)} produtos prontos.")
    st.table(produtos_etiquetas)
    
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=14, leftMargin=14, topMargin=20, bottomMargin=14)
    story = []
    styles = getSampleStyleSheet()
    
    COR_LARANJA = colors.HexColor("#FF8C00")
    COR_PRETO = colors.HexColor("#000000")
    COR_FUNDO_TOTAL = colors.HexColor("#FF9900")
    
    style_nome = ParagraphStyle('Nome', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=1, leading=9)
    style_18x = ParagraphStyle('V_18x', fontName='Helvetica-Bold', fontSize=18, textColor=COR_LARANJA, alignment=0, leading=18)
    style_rs = ParagraphStyle('V_Rs', fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, alignment=0, leading=10)
    style_parcela = ParagraphStyle('V_Parc', fontName='Helvetica-Bold', fontSize=18, textColor=colors.white, alignment=2, leading=18)
    style_sub_cartao = ParagraphStyle('V_Cart', fontName='Helvetica-Bold', fontSize=5, textColor=colors.white, alignment=1, leading=5)
    style_tag_cartao = ParagraphStyle('V_TagC', fontName='Helvetica-Bold', fontSize=5, textColor=COR_PRETO, alignment=1, leading=5)
    style_total_original = ParagraphStyle('V_Tot', fontName='Helvetica-Bold', fontSize=12, textColor=COR_PRETO, alignment=1, leading=12)
    style_sem_juros = ParagraphStyle('V_SJ', fontName='Helvetica-Bold', fontSize=13, textColor=COR_PRETO, alignment=1, leading=13)

    LARGURA_BLOCO = 5.8 * 28.346  
    
    lista_blocos_desenhados = []
    
    for p in produtos_etiquetas:
        # Cabeçalho com 18 pontos de altura fixa
        tab_cabecalho = Table([[Paragraph(p['nome'], style_nome)]], colWidths=[LARGURA_BLOCO], rowHeights=[18])
        tab_cabecalho.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_LARANJA),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        bloco_cartao_detalhe = Table([
            [Paragraph("NO CARTÃO", style_tag_cartao)],
            [Paragraph("DE CRÉDITO", style_sub_cartao)]
        ], colWidths=[LARGURA_BLOCO * 0.4])
        bloco_cartao_detalhe.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), COR_LARANJA),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
        ]))

        linha_parcela_dados = [
            Paragraph("18X", style_18x), 
            Paragraph("R$", style_rs), 
            Paragraph(p['parcela'], style_parcela),
            bloco_cartao_detalhe
        ]
        
        # Primeira linha preta com 20 pontos de altura
        tab_linha_1 = Table([linha_parcela_dados], colWidths=[LARGURA_BLOCO * 0.22, LARGURA_BLOCO * 0.12, LARGURA_BLOCO * 0.36, LARGURA_BLOCO * 0.30], rowHeights=[20])
        tab_linha_1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_PRETO),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))

        # Linha inferior amarela com 16 pontos de altura
        bloco_total_amarelo = Table([[Paragraph(p['total'], style_total_original)]], colWidths=[LARGURA_BLOCO * 0.5], rowHeights=[16])
        bloco_total_amarelo.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_FUNDO_TOTAL),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))

        linha_rodape_dados = [bloco_total_amarelo, Paragraph("SEM JUROS", style_sem_juros)]
        
        tab_linha_2 = Table([linha_rodape_dados], colWidths=[LARGURA_BLOCO * 0.5, LARGURA_BLOCO * 0.5], rowHeights=[16])
        tab_linha_2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_LARANJA),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))

        # Junta o corpo totalizando 36 pontos de altura
        tab_corpo_etiqueta = Table([[tab_linha_1], [tab_linha_2]], colWidths=[LARGURA_BLOCO], rowHeights=[20, 16])
        tab_corpo_etiqueta.setStyle(TableStyle([
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))

        # Une Cabeçalho (18) + Corpo (36) = 54 pontos de altura total por etiqueta
        bloco_final_individual = Table([[tab_cabecalho], [tab_corpo_etiqueta]], colWidths=[LARGURA_BLOCO], rowHeights=[18, 36])
        bloco_final_individual.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#FF8C00")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        lista_blocos_desenhados.append(bloco_final_individual)
        
    grade_linhas_finais = []
    for idx in range(0, len(lista_blocos_desenhados), 3):
        trio = lista_blocos_desenhados[idx:idx+3]
        while len(trio) < 3:
            trio.append(Spacer(1, LARGURA_BLOCO))
        grade_linhas_finais.append(trio)
        
    tabela_grade_impressao = Table(grade_linhas_finais, colWidths=[LARGURA_BLOCO, LARGURA_BLOCO, LARGURA_BLOCO])
    tabela_grade_impressao.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),  
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14), 
        ('TOPPADDING', (0,0), (-1,-1), 14),
    ]))
    
    story.append(KeepTogether([tabela_grade_impressao]))
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
