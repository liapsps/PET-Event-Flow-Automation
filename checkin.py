import streamlit as st
import cv2
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PET TI - Check-in", page_icon="✅", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
@st.cache_resource
def conectar_planilha():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    
    # CORREÇÃO 1: Adicionei o "1" no final, pois sua planilha real tem esse nome
    return client.open("Inscrições Infogirl 2025 (UFC)(respostas)").worksheet("Respostas ao formulário")

# Função para ler dados
def carregar_dados():
    sheet = conectar_planilha()
    dados = sheet.get_all_records()
    return pd.DataFrame(dados), sheet

# --- INTERFACE ---
st.title("🤖 Sistema de Check-in - PET TI")
col1, col2 = st.columns([2, 1])

# Carrega os dados
df, sheet_instance = carregar_dados()

with col1:
    img_file_buffer = st.camera_input("Escanear QR Code")

    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(cv2_img)
        
        if data:
            # Sanitização
            email_detectado = str(data).strip().lower()
            st.info(f"🔍 Lido: '{email_detectado}'")
            
            # Debug: Mostra os emails da planilha para você conferir
            # CORREÇÃO 2: Mudei para 'E-mail' (Coluna B) que é a correta
            st.caption("Debug - Primeiros da lista:")
            st.code(df['E-mail'].head(3).tolist())

            # CORREÇÃO 3: Busca na coluna certa 'E-mail'
            usuario = df[df['E-mail'].astype(str).str.strip().str.lower() == email_detectado]
            
            if not usuario.empty:
                # CORREÇÃO 4: Busca na coluna certa 'Nome'
                nome_aluno = usuario.iloc[0]['Nome']
                
                # CORREÇÃO 5: Verifica se a coluna Checkin existe/está preenchida
                # Se a coluna não existir no DataFrame (ainda vazia), assume que não entrou
                if 'Checkin' in usuario.columns:
                    ja_entrou = usuario.iloc[0]['Checkin']
                else:
                    ja_entrou = ""
                
                if str(ja_entrou).upper() == "SIM":
                    st.warning(f"⚠️ {nome_aluno} JÁ ENTROU!")
                else:
                    numero_linha = usuario.index[0] + 2
                    # Escreve SIM na Coluna 10 (Coluna J - Checkin)
                    sheet_instance.update_cell(numero_linha, 10, "SIM")
                    st.success(f"✅ BEM-VINDO(A), {nome_aluno.upper()}!")
                    st.balloons()
                    
                    # Limpa cache para atualizar o gráfico lateral
                    st.cache_data.clear()
            else:
                st.error("❌ E-mail não encontrado! Verifique a planilha.")

# --- DASHBOARD ---
with st.sidebar:
    st.header("📊 Métricas")
    if st.button("🔄 Atualizar"):
        st.rerun()
        
    total_inscritos = len(df)
    # Conta quantos "SIM" existem na coluna Checkin (se ela existir)
    if 'Checkin' in df.columns:
        total_presentes = len(df[df['Checkin'].astype(str).str.upper() == "SIM"])
    else:
        total_presentes = 0
        
    st.metric("Total", total_inscritos)
    st.metric("Presentes", total_presentes)