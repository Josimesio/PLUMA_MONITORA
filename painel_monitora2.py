import requests
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configurações iniciais
tempo_verificacao = 10  # Intervalo padrão entre verificações, em segundos
arquivo_log = "monitoramento.log"

# Configurações de Email
email_envio = "seuemail@gmail.com"  # Email remetente
email_senha = "sua_senha"  # Senha do email remetente
email_destino = "destinatario@gmail.com"  # Email destinatário

monitorando = False  # Controle do monitoramento
tempos_resposta = []  # Lista para armazenar tempos de resposta
status_sites = []  # Lista para armazenar status (OK/FALHA)


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


def monitorar_sistema(url):
    """Função principal para monitorar o sistema."""
    global monitorando
    while monitorando:
        try:
            inicio = time.time()
            resposta = requests.get(url, timeout=10)
            fim = time.time()
            tempo_resposta = int((fim - inicio) * 1000)  # Tempo em milissegundos

            if resposta.status_code == 200:
                mensagem = f"[OK] {url} está no ar. Tempo de resposta: {tempo_resposta}ms."
                adicionar_log(mensagem)
                registrar_log(mensagem)
                tempos_resposta.append(tempo_resposta)
                status_sites.append(1)  # 1 para OK
            else:
                mensagem = f"[ERRO] {url} retornou o status: {resposta.status_code}"
                adicionar_log(mensagem)
                registrar_log(mensagem)
                enviar_email(mensagem)
                status_sites.append(0)  # 0 para ERRO
        except requests.exceptions.RequestException as e:
            mensagem = f"[FALHA] {url} está fora do ar. Detalhes: {e}"
            adicionar_log(mensagem)
            registrar_log(mensagem)
            enviar_email(mensagem)
            status_sites.append(0)  # 0 para FALHA

        time.sleep(tempo_verificacao)


def iniciar_monitoramento():
    """Inicia o monitoramento em uma thread separada."""
    global monitorando
    url = entrada_url.get()
    if not url:
        adicionar_log("[ERRO] URL não pode estar vazia!")
        return

    monitorando = True
    thread = threading.Thread(target=monitorar_sistema, args=(url,))
    thread.daemon = True
    thread.start()
    adicionar_log("[INFO] Monitoramento iniciado.")


def parar_monitoramento():
    """Para o monitoramento."""
    global monitorando
    monitorando = False
    adicionar_log("[INFO] Monitoramento parado.")


def exportar_logs():
    """Exporta os logs para um arquivo CSV."""
    arquivo = filedialog.asksaveasfilename(defaultextension=".csv",
                                           filetypes=[("CSV files", "*.csv")])
    if arquivo:
        with open(arquivo, "w") as f:
            f.write("Data,Hora,Mensagem\n")
            with open(arquivo_log, "r") as log:
                for linha in log:
                    data_hora, mensagem = linha.split(" - ", 1)
                    f.write(f"{data_hora},{mensagem.strip()}\n")
        adicionar_log(f"[INFO] Logs exportados para {arquivo}")


def exibir_grafico():
    """Exibe um gráfico dos tempos de resposta."""
    if not tempos_resposta:
        adicionar_log("[INFO] Nenhum dado de tempo de resposta disponível.")
        return

    fig, ax = plt.subplots()
    ax.plot(tempos_resposta, label="Tempo de Resposta (ms)", marker="o")
    ax.set_title("Tempo de Resposta do Sistema")
    ax.set_xlabel("Tentativas")
    ax.set_ylabel("Tempo (ms)")
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=janela)
    canvas.get_tk_widget().pack()
    canvas.draw()


# Interface Gráfica
janela = tk.Tk()
janela.title("Painel de Monitoramento")
janela.geometry("800x600")

# Entrada de URL
frame_entrada = tk.Frame(janela)
frame_entrada.pack(pady=10)

tk.Label(frame_entrada, text="URL:").grid(row=0, column=0, padx=5)
entrada_url = tk.Entry(frame_entrada, width=50)
entrada_url.grid(row=0, column=1, padx=5)
entrada_url.insert(0, "https://seusite.com")

# Painel de logs
painel_logs = scrolledtext.ScrolledText(janela, width=90, height=15)
painel_logs.pack(pady=10)

# Botões de controle
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=10)

btn_iniciar = tk.Button(frame_botoes, text="Iniciar Monitoramento", command=iniciar_monitoramento)
btn_iniciar.grid(row=0, column=0, padx=10)

btn_parar = tk.Button(frame_botoes, text="Parar Monitoramento", command=parar_monitoramento)
btn_parar.grid(row=0, column=1, padx=10)

btn_exportar = tk.Button(frame_botoes, text="Exportar Logs", command=exportar_logs)
btn_exportar.grid(row=0, column=2, padx=10)

btn_grafico = tk.Button(frame_botoes, text="Exibir Gráfico", command=exibir_grafico)
btn_grafico.grid(row=0, column=3, padx=10)

# Iniciar o loop principal da interface
janela.mainloop()
