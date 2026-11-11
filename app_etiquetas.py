import os
import sys

# Força a instalação antes de tentar importar qualquer coisa do reportlab
try:
    from reportlab.lib.pagesizes import letter
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "pypdf"])
    # Reinicia o próprio script para o Python reconhecer a instalação na hora
    os.execv(sys.executable, ['python'] + sys.argv)

import re
import io
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuração da página
st.set_page_config(page_title="Gerador de Etiquetas", page_icon="🏷️", layout="wide")

st.title("🏷️ Gerador de Etiquetas de Preço - 18x Sem Juros")
st.markdown("Cole a lista de preços do WhatsApp abaixo para gerar a folha de etiquetas oficial (Grade 3x4).")

texto_padrao = """TROCA DE PREÇO 05.11.26

POCO M8 5G 512/8 - R$2.299,90
REALME C73 128/4 - R$1.399,90
REALME C100I 256/4 - R$1.649,90
REDMI 15C 256/8 - R$1.599,90
POCO C85 256/8 - R$1.749,90"""

entrada_texto = st.text_area("Cole as informações do WhatsApp aqui:", value=texto_padrao, height=200)

# Processamento do texto do WhatsApp
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
    st.success(f"{len(produtos_etiquetas)} produtos processados com sucesso!")
    st.table(produtos_etiquetas)
    
    # Geração do PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=14, leftMargin=14, topMargin=14, bottomMargin=14)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos Visuais Oficiais
    style_nome = ParagraphStyle('Et_Nome', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=1, leading=9)
    style_18x = ParagraphStyle('Et_18x', fontName='Helvetica-Bold', fontSize=20, textColor=colors.HexColor("#FF8C00"), alignment=0, leading=20)
    style_val_parc = ParagraphStyle('Et_ValParc', fontName='Helvetica-Bold', fontSize=16, textColor=colors.white, alignment=2, leading=16)
    style_sub_cartao = ParagraphStyle('Et_SubCartao', fontName='Helvetica-Bold', fontSize=5, textColor=colors.HexColor("#FF8C00"), alignment=2, leading=5)
    style_total = ParagraphStyle('Et_Total', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#A0A0A0"), alignment=0, leading=11)
    style_sem_juros = ParagraphStyle('Et_SemJuros', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#FF8C00"), alignment=2, leading=11)

    # Medidas das caixas (Grade 3x4)
    LARGURA_BLOCO = 5.8 * 28.346  
    ALTURA_BLOCO = 5.4 * 28.346   
    
    lista_blocos = []
    for p in produtos_etiquetas:
        # 1. Parte de cima Laranja
        tab_cabecalho = Table([[Paragraph(p['nome'], style_nome)]], colWidths=[LARGURA_BLOCO], rowHeights=[18])
        tab_cabecalho.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FF8C00")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        # 2. Parte de baixo Preta
        l1 = [Paragraph("18X", style_18x), [Paragraph(p['parcela'], style_val_parc), Paragraph("NO CARTÃO DE CRÉDITO", style_sub_cartao)]]
        l2 = [Paragraph(f"<strike>{p['total']}</strike>", style_total), Paragraph("SEM JUROS", style_sem_juros)]
        
        tab_corpo = Table([l1, l2], colWidths=[LARGURA_BLOCO * 0.35, LARGURA_BLOCO * 0.65], rowHeights=[20, 16])
        tab_corpo.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        # Junta na etiqueta com contorno laranja igual ao PDF
        bloco_completo = Table([[tab_cabecalho], [tab_corpo]], colWidths=[LARGURA_BLOCO], rowHeights=[18, 36])
        bloco_completo.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#FF8C00")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        lista_blocos.append(bloco_completo)
        
    # Organiza em 3 Colunas por Linha
    grade_linhas = []
    for idx in range(0, len(lista_blocos), 3):
        trio = lista_blocos[idx:idx+3]
        while len(trio) < 3:
            trio.append(Spacer(1, LARGURA_BLOCO))
        grade_linhas.append(trio)
        
    tabela_grade_final = Table(grade_linhas, colWidths=[LARGURA_BLOCO, LARGURA_BLOCO, LARGURA_BLOCO])
    tabela_grade_final.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),  
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10), 
        ('TOPPADDING', (0,0), (-1,-1), 10),
    ]))
    
    story.append(KeepTogether([tabela_grade_final]))
    doc.build(story)
    
    st.markdown("---")
    st.download_button(
        label="📥 Baixar Folha de Etiquetas em PDF (Grade 3x4 Oficial)",
        data=pdf_buffer.getvalue(),
        file_name="folha_etiquetas_18x.pdf",
        mime="application/pdf",
        use_container_width=True
    )
