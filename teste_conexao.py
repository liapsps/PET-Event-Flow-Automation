import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuração da autenticação
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

try:
    # Abre a planilha pelo nome exato (tem que ser igualzinho ao do Google Sheets)
    sheet = client.open("PET Eventos - Database").sheet1
    
    # Leitura: Pega todos os dados
    dados = sheet.get_all_records()
    print("✅ Conexão bem sucedida! Dados lidos:")
    print(dados)

    # Escrita: Vamos escrever algo na coluna E (linha 2) para provar que temos poder
    # update_cell(linha, coluna, valor)
    sheet.update_cell(2, 5, "Teste OK") 
    print("✅ Escrita realizada! Confira a coluna E na sua planilha.")

except Exception as e:
    print(f"❌ Deu ruim: {e}")