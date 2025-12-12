import gspread
import qrcode
import smtplib
import os
from oauth2client.service_account import ServiceAccountCredentials
from email.message import EmailMessage

# --- CONFIGURAÇÕES ---
# Coloque aqui o seu email que vai enviar
EMAIL_REMETENTE = "lialilinbox@gmail.com" 
# Coloque a senha de 16 letras do App Password (NÃO A SUA SENHA NORMAL)
EMAIL_SENHA = "omcn dsto vunx jexf" 

def conectar_planilha():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    # Abre a planilha e pega a primeira aba
    return client.open("Inscrições Infogirl 2025 (UFC)(respostas)").worksheet("Respostas ao formulário")

def gerar_qr_code(conteudo, nome_arquivo):
    # Cria um QR Code simples com o conteúdo (ex: email da pessoa)
    img = qrcode.make(conteudo)
    img.save(nome_arquivo)
    return nome_arquivo

def enviar_email(destinatario, nome_pessoa, arquivo_qr):
    msg = EmailMessage()
    msg['Subject'] = f"Seu ingresso para o evento do PET TI chegou, {nome_pessoa}!"
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = destinatario
    
    # Corpo do e-mail
    msg.set_content(f"""
    Olá, {nome_pessoa}!
    
    Sua inscrição está confirmada.
    Em anexo está o seu QR Code para o check-in no dia do evento.
    
    Por favor, apresente este código na entrada (pode ser no celular mesmo).
    
    Atenciosamente,
    Equipe PET TI
    """)

    # Anexar a imagem
    with open(arquivo_qr, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(arquivo_qr)
    
    msg.add_attachment(file_data, maintype='image', subtype='png', filename=file_name)

    # Conectar ao servidor do Gmail e enviar
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_REMETENTE, EMAIL_SENHA)
        smtp.send_message(msg)

def main():
    print("🤖 Iniciando o Robô Carteiro...")
    sheet = conectar_planilha()
    registros = sheet.get_all_records()
    
    # IMPORTANTE: get_all_records retorna uma lista de dicionários.
    # O gspread conta linhas começando do 1. O cabeçalho é a linha 1.
    # O primeiro registro de dados é a linha 2.
    
    for i, linha in enumerate(registros):
        # O índice 'i' começa em 0, mas na planilha essa é a linha 2 (porque tem cabeçalho)
        numero_linha_planilha = i + 2 
        
        nome = linha['Nome']
        email = linha['E-mail']
        status = linha['QR_Enviado']

        # A Lógica de Idempotência: Só processa se status estiver vazio
        if status == "":
            print(f"📧 Processando: {nome}...")
            
            try:
                # 1. Gerar QR Code (usando o email como dado único)
                nome_arquivo_qr = f"qr_{i}.png"
                gerar_qr_code(email, nome_arquivo_qr)
                
                # 2. Enviar E-mail
                enviar_email(email, nome, nome_arquivo_qr)
                print(f"   ✅ E-mail enviado para {email}")
                
                # 3. Atualizar Planilha
                # Atenção: Coluna 4 é onde está o 'QR_Enviado' (A=1, B=2, C=3, D=4)
                sheet.update_cell(numero_linha_planilha, 4, "SIM")
                
                # 4. Limpeza (apagar a imagem do computador para não acumular lixo)
                os.remove(nome_arquivo_qr)
                
            except Exception as e:
                print(f"   ❌ Erro ao processar {nome}: {e}")
        else:
            print(f"⏩ Pulando {nome} (Já enviado).")

if __name__ == "__main__":
    main()