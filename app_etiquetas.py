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
    st.success(f"Sucesso! {len(produtos_etiquetas)} etiquetas prontas para gerar.")
    st.table(produtos_etiquetas)
    
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=14, leftMargin=14, topMargin=14, bottomMargin=14)
    story = []
    styles = getSampleStyleSheet()
    
    # Cores Oficiais da Loja
    COR_LARANJA = colors.HexColor("#FF6600")  
    COR_AMARELO = colors.HexColor("#FFCC00")  
    COR_PRETO = colors.HexColor("#000000")
    COR_BRANCO = colors.HexColor("#FFFFFF")
    
    # Definição Rígida de Estilos
    style_nome = ParagraphStyle('E_Nome', fontName='Helvetica-Bold', fontSize=8, textColor=COR_PRETO, alignment=1, leading=9)
    style_18x = ParagraphStyle('E_18x', fontName='Helvetica-Bold', fontSize=12, textColor=COR_BRANCO, alignment=1, leading=12)
    style_rs = ParagraphStyle('E_Rs', fontName='Helvetica-Bold', fontSize=10, textColor=COR_BRANCO, alignment=2, leading=10)
    style_parcela = ParagraphStyle('E_Parc', fontName='Helvetica-Bold', fontSize=24, textColor=COR_BRANCO, alignment=0, leading=24)
    style_selo = ParagraphStyle('E_Selo', fontName='Helvetica-Bold', fontSize=5.5, textColor=COR_PRETO, alignment=1, leading=6)
    style_total = ParagraphStyle('E_Total', fontName='Helvetica-Bold', fontSize=11, textColor=COR_BRANCO, alignment=0, leading=11)
    style_logo = ParagraphStyle('E_Logo', fontName='Helvetica-Bold', fontSize=9, textColor=COR_PRETO, alignment=0, leading=10)
    style_sem_juros = ParagraphStyle('E_SJ', fontName='Helvetica-Bold', fontSize=9, textColor=COR_PRETO, alignment=2, leading=10)

    # Medida base de largura por bloco
    LARGURA_ET = 5.8 * 28.346  
    
    lista_blocos_etiquetas = []
    
    for p in produtos_etiquetas:
        # 1. TOPO: Caixa branca arredondada do produto
        tab_nome_branca = Table([[Paragraph(p['nome'], style_nome)]], colWidths=[LARGURA_ET - 16], rowHeights=[22])
        tab_nome_branca.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_BRANCO),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (-1,-1), 0.5, COR_PRETO),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        tab_topo_laranja = Table([[tab_nome_branca]], colWidths=[LARGURA_ET], rowHeights=[30])
        tab_topo_laranja.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_LARANJA),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        # 2. MEIO PRETO: Divisões de coluna rígidas
        tab_balao_18x = Table([[Paragraph("18X", style_18x)]], colWidths=[30], rowHeights=[18])
        tab_balao_18x.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_AMARELO),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        tab_selo_cartao = Table([
            [Paragraph("NO CARTÃO", style_selo)],
            [Paragraph("DE CRÉDITO", style_selo)]
        ], colWidths=[42], rowHeights=[8, 8])
        tab_selo_cartao.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_AMARELO),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        miolo_dados = [
            tab_balao_18x, 
            Spacer(1, 1),
            Paragraph("R$", style_rs), 
            Paragraph(p['parcela'], style_parcela), 
            tab_selo_cartao
        ]
        
        tab_meio_preto = Table([miolo_dados], colWidths=[32, 4, 18, 66, 44], rowHeights=[34])
        tab_meio_preto.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_PRETO),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        # 3. FAIXA DO PREÇO TOTAL: Barra limpa
        tab_faixa_preco = Table([[Paragraph(p['total'], style_total)]], colWidths=[LARGURA_ET], rowHeights=[18])
        tab_faixa_preco.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_PRETO),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        # 4. RODAPÉ LARANJA: Marca e sem juros
        rodape_dados = [
            Paragraph("MYMI STORE", style_logo),
            Paragraph("SEM JUROS", style_sem_juros)
        ]
        tab_rodape_laranja = Table([rodape_dados], colWidths=[LARGURA_ET * 0.55, LARGURA_ET * 0.45], rowHeights=[22])
        tab_rodape_laranja.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COR_LARANJA),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        # 5. MONTAGEM FINAL DA ETIQUETA
        etiqueta_montada = Table([
            [tab_topo_laranja],
            [tab_meio_preto],
            [tab_faixa_preco],
            [tab_rodape_laranja]
        ], colWidths=[LARGURA_ET], rowHeights=[30, 34, 18, 22])
        
        etiqueta_montada.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#FF8C00")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        lista_blocos_etiquetas.append(etiqueta_montada)
        
    grade_linhas_finais = []
    for idx in range(0, len(lista_blocos_etiquetas), 3):
        trio = lista_blocos_etiquetas[idx:idx+3]
        while len(trio) < 3:
            trio.append(Spacer(1, LARGURA_ET))
        grade_linhas_finais.append(trio)
        
    tabela_mestre = Table(grade_linhas_finais, colWidths=[LARGURA_ET, LARGURA_ET, LARGURA_ET])
    tabela_mestre.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),  
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 14), 
        ('TOPPADDING', (0,0), (-1,-1), 14),
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
