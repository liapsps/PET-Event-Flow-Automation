# 🎟️ PET Event Flow: Automação de Eventos com Python e Visão Computacional

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![OpenCV](https://img.shields.io/badge/Computer_Vision-OpenCV-green)
![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)

## 🎯 O Problema
No **PET TI (UFC Quixadá)**, a gestão de eventos enfrentava gargalos manuais significativos:
1.  **Inscrições:** Gerenciadas em planilhas isoladas.
2.  **Credenciamento:** Feito manualmente em papel ou busca lenta em planilhas na porta do evento (gerando filas).
3.  **Certificação:** Processo manual demorado, suscetível a erros humanos e atrasos no envio.

## 🚀 A Solução
Desenvolvi um pipeline de automação **Full Python** que transforma o Google Sheets em um Banco de Dados relacional simplificado, utilizando **Visão Computacional** para agilizar o check-in e scripts de automação para comunicação.

### Arquitetura do Projeto

O sistema é dividido em três módulos principais:

1.  **📬 O "Carteiro" (Pré-Evento)**
    * Consome dados de novos inscritos via **Google Sheets API**.
    * Gera **QR Codes únicos** para cada participante.
    * Dispara e-mails automáticos com o ingresso digital (anexo do QR Code).

2.  **👁️ O "Porteiro" (Check-in em Tempo Real)**
    * Aplicação Web construída com **Streamlit**.
    * Utiliza **OpenCV** para leitura de QR Codes via webcam em tempo real.
    * Realiza a validação e atualização de presença na nuvem (Sheets) instantaneamente.
    * *Elimina filas e fraudes de presença.*

3.  **🎓 O "Gerador" (Pós-Evento)**
    * Filtra participantes confirmados.
    * Gera certificados em PDF personalizados (usando `ReportLab`).
    * *(Feature em Dev)*: Integração com **GenAI** para criar corpos de e-mail de agradecimento personalizados e sumarizados sobre o tema do evento.

## 🛠️ Tech Stack

* **Linguagem:** Python 3.x
* **Interface (Frontend):** Streamlit
* **Computer Vision:** OpenCV (`cv2`)
* **Banco de Dados:** Google Sheets (via `gspread`)
* **Automação:** SMTP Lib (E-mails), PyQRCode
* **Infraestrutura:** Local / Deploy em Streamlit Cloud (futuro)

## 📦 Estrutura do Projeto

```bash
├── src/
│   ├── modules/
│   │   ├── google_client.py   # Conexão com GSheets API
│   │   ├── mail_sender.py     # Disparo de e-mails
│   │   └── qr_generator.py    # Geração de códigos
│   ├── checkin_app.py         # App Streamlit (Visão Computacional)
│   └── certificate_bot.py     # Script de pós-evento
├── assets/
│   └── qrcodes/               # Armazenamento temporário
├── credentials/               # (Ignorado no .gitignore)
├── requirements.txt
└── README.md
