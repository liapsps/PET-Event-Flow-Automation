import streamlit as st
import cv2
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PET TI - Check-in", page_icon="✅", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS (Cacheada para não reconectar toda hora) ---
@st.cache_resource
def conectar_planilha():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client.open("Inscrições Infogirl 2025 (UFC)(respostas)").worksheet("Respostas ao formulário").sheet1

# Função para ler dados atuais (sem cache, para pegar atualizações)
def carregar_dados():
    sheet = conectar_planilha()
    # Pega todos os registros e transforma em DataFrame do Pandas (mais fácil de mexer)
    dados = sheet.get_all_records()
    return pd.DataFrame(dados), sheet

# --- INTERFACE PRINCIPAL ---
st.title("🤖 Sistema de Check-in - PET TI")
st.write("Aponte o QR Code para a câmera abaixo.")

# Layout em colunas (Câmera na Esquerda, Status na Direita)
col1, col2 = st.columns([2, 1])

df, sheet_instance = carregar_dados()

with col1:
    # O Widget de Câmera do Streamlit
    img_file_buffer = st.camera_input("Escanear QR Code")

    if img_file_buffer is not None:
        # 1. Converter a imagem para formato que o OpenCV entende
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # 2. Detectar QR Code
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(cv2_img)
        
        if data:
            # 1. Sanitização (Limpeza) do Input
            # Transforma em texto, tira espaços extras e joga tudo pra minúsculo
            email_detectado = str(data).strip().lower()
            
            st.info(f"🔍 Código lido (sanitizado): '{email_detectado}'")
            
            # 2. Debug (Para você ver o que está acontecendo na tela)
            # Isso mostra os primeiros 5 emails da lista pra você conferir se está batendo
            st.caption("Debug - Primeiros e-mails da base:")
            st.code(df['Endereço de e-mail'].head().tolist())

            # 3. Busca Robusta (Case Insensitive)
            # Criamos uma máscara onde limpamos a coluna da planilha TAMBÉM antes de comparar
            # Isso não altera os dados originais, só a comparação
            usuario = df[df['Endereço de e-mail'].astype(str).str.strip().str.lower() == email_detectado]
            
            if not usuario.empty:
                # Se achou, pega o nome da linha original (sem minúsculas)
                nome_aluno = usuario.iloc[0]['Nome completo']
                ja_entrou = usuario.iloc[0]['Checkin']
                
                # ... (o resto do código segue igual: verifica se já entrou, dá parabéns, etc)

# --- SIDEBAR (DASHBOARD) ---
with st.sidebar:
    st.header("📊 Métricas do Evento")
    
    # Recarrega dados para garantir contagem atualizada
    df_atual, _ = carregar_dados()
    
    total_inscritos = len(df_atual)
    total_presentes = len(df_atual[df_atual['Checkin'] == "SIM"])
    percentual = (total_presentes / total_inscritos) * 100 if total_inscritos > 0 else 0
    
    st.metric("Total de Inscritos", total_inscritos)
    st.metric("Presentes Agora", total_presentes, delta=f"{percentual:.1f}% de comparecimento")
    
    # Barra de progresso
    st.progress(total_presentes / total_inscritos if total_inscritos > 0 else 0)
    
    st.divider()
    if st.button("🔄 Atualizar Dados"):
        st.rerun()