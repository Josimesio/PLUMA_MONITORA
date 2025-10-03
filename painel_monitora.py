import requests
import time
import threading
import tkinter as tk
from tkinter import scrolledtext
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Configurações
url = "https://epfa-test.fa.us2.oraclecloud.com/fscmUI/faces/FuseWelcome?_afrLoop=29754934183513255&_afrWindowMode=0&_afrWindowId=null&_adf.ctrl-state=jfpood4hh_1&_afrFS=16&_afrMT=screen&_afrMFW=1536&_afrMFH=695&_afrMFDW=1536&_afrMFDH=864&_afrMFC=8&_afrMFCI=0&_afrMFM=0&_afrMFR=120&_afrMFG=0&_afrMFS=0&_afrMFO=0"  # Substitua pela URL ou IP a ser monitorado
tempo_verificacao = 10  # Intervalo entre verificações, em segundos
arquivo_log = "monitoramento.log"

# Configurações de Email
email_envio = "seuemail@gmail.com"  # Email remetente
email_senha = "sua_senha"  # Senha do email remetente
email_destino = "destinatario@gmail.com"  # Email destinatário

monitorando = False  # Controle do monitoramento


def enviar_email(mensagem):
    """Função para enviar notificações por email."""
    try:
        msg = MIMEMultipart()
        msg['From'] = email_envio
        msg['To'] = email_destino
        msg['Subject'] = "Alerta: Sistema Fora do Ar"

        msg.attach(MIMEText(mensagem, 'plain'))

        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(email_envio, email_senha)
        servidor.send_message(msg)
        servidor.quit()

        adicionar_log("[NOTIFICAÇÃO] Email enviado com sucesso!")
    except Exception as e:
        adicionar_log(f"[ERRO] Falha ao enviar email. Detalhes: {e}")


def registrar_log(mensagem):
    """Função para registrar eventos em um arquivo de log."""
    with open(arquivo_log, "a") as log:
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {mensagem}\n")


def adicionar_log(mensagem):
    """Adiciona uma mensagem ao painel de logs."""
    painel_logs.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {mensagem}\n")
    painel_logs.see(tk.END)


def monitorar_sistema():
    """Função principal para monitorar o sistema."""
    global monitorando
    while monitorando:
        try:
            resposta = requests.get(url, timeout=10)
            if resposta.status_code == 200:
                mensagem = f"[OK] {url} está no ar."
                adicionar_log(mensagem)
                registrar_log(mensagem)
            else:
                mensagem = f"[ERRO] {url} retornou o status: {resposta.status_code}"
                adicionar_log(mensagem)
                registrar_log(mensagem)
                enviar_email(mensagem)
        except requests.exceptions.RequestException as e:
            mensagem = f"[FALHA] {url} está fora do ar. Detalhes: {e}"
            adicionar_log(mensagem)
            registrar_log(mensagem)
            enviar_email(mensagem)

        time.sleep(tempo_verificacao)


def iniciar_monitoramento():
    """Inicia o monitoramento em uma thread separada."""
    global monitorando
    monitorando = True
    thread = threading.Thread(target=monitorar_sistema)
    thread.daemon = True
    thread.start()
    adicionar_log("[INFO] Monitoramento iniciado.")


def parar_monitoramento():
    """Para o monitoramento."""
    global monitorando
    monitorando = False
    adicionar_log("[INFO] Monitoramento parado.")


# Interface Gráfica
janela = tk.Tk()
janela.title("Painel de Monitoramento")
janela.geometry("600x400")

# Label de URL monitorada
label_url = tk.Label(janela, text=f"Monitorando: {url}", font=("Arial", 12))
label_url.pack(pady=10)

# Painel de logs
painel_logs = scrolledtext.ScrolledText(janela, width=70, height=15)
painel_logs.pack(pady=10)

# Botões de controle
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=10)

btn_iniciar = tk.Button(frame_botoes, text="Iniciar Monitoramento", command=iniciar_monitoramento)
btn_iniciar.grid(row=0, column=0, padx=10)

btn_parar = tk.Button(frame_botoes, text="Parar Monitoramento", command=parar_monitoramento)
btn_parar.grid(row=0, column=1, padx=10)

# Iniciar o loop principal da interface
janela.mainloop()
