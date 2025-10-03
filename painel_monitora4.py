import time
import threading
import tkinter as tk
from urllib.parse import urlparse
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configurações iniciais
tempo_verificacao = 5  # Intervalo entre verificações, em segundos
monitorando = False  # Controle do monitoramento
status_urls = [None] * 6  # Status inicial das URLs (None = não verificado)
progresso_barras = [0] * 6  # Progresso inicial (0 a 20)
urls_fora_do_ar = {}  # Dicionário para armazenar URLs fora do ar e seus nomes
urls_nomes = {}  # Dicionário para mapear URLs e seus nomes amigáveis

# Configurações de URLs
urls = ["", "", "", "", "", ""]  # Até 6 URLs

# Para o gráfico
online_count = 0
offline_count = 0

def verificar_urls():
    """Função principal para monitorar múltiplas URLs."""
    global monitorando, online_count, offline_count
    while monitorando:
        for i, url in enumerate(urls):
            if not url.strip():
                continue  # Pula URLs vazias

            try:
                resposta = requests.get(url, timeout=10)
                if resposta.status_code == 200:
                    status_urls[i] = "online"
                    if url in urls_fora_do_ar:
                        del urls_fora_do_ar[url]  # Remove da lista de offline
                else:
                    status_urls[i] = "offline"
                    urls_fora_do_ar[url] = urls_nomes.get(url, "SISTEMA DESCONHECIDO")
            except requests.exceptions.RequestException:
                status_urls[i] = "offline"
                urls_fora_do_ar[url] = urls_nomes.get(url, "SISTEMA DESCONHECIDO")

            atualizar_progresso(i)  # Atualiza o progresso da barra correspondente

        # Atualiza os contadores de online e offline
        online_count = sum(1 for status in status_urls if status == "online")
        offline_count = len(urls) - online_count

        atualizar_grafico()  # Atualiza o gráfico de status

        atualizar_mensagem_central()  # Atualiza a lista de URLs fora do ar
        time.sleep(tempo_verificacao)

def atualizar_grafico():
    """Atualiza o gráfico de barras com o status de URLs."""
    # Atualiza o gráfico de status (online vs offline)
    ax.clear()
    ax.bar(['Online', 'Offline'], [online_count, offline_count], color=['green', 'red'])
    ax.set_title('Status das URLs')
    ax.set_ylabel('Número de URLs')
    ax.set_ylim(0, len(urls))  # Ajusta o limite superior do gráfico

    canvas.draw()  # Redesenha o gráfico no tkinter

def atualizar_progresso(indice):
    """Atualiza o progresso da barra para a URL correspondente."""
    if status_urls[indice] == "online":
        if progresso_barras[indice] < 20:
            progresso_barras[indice] += 1
    elif status_urls[indice] == "offline":
        if progresso_barras[indice] < 20:
            progresso_barras[indice] += 1
    else:
        progresso_barras[indice] = 0  # Reseta o progresso em caso de falha

    atualizar_barras()  # Atualiza a interface gráfica

def iniciar_monitoramento():
    """Inicia o monitoramento em uma thread separada."""
    global monitorando
    urls_atualizadas = [entrada_url.get().strip() for entrada_url in entradas_urls]
    nomes_atualizados = [entrada_nome.get().strip() for entrada_nome in entradas_nomes]

    # Valida URLs
    urls_validas = []
    for i, url in enumerate(urls_atualizadas):
        if not url:
            continue
        if validar_url(url):
            urls[i] = url
            urls_nomes[url] = nomes_atualizados[i] or "SISTEMA DESCONHECIDO"
            urls_validas.append(url)
        else:
            adicionar_log(f"[ERRO] URL/IP inválido: {url}")

    if not urls_validas:
        adicionar_log("[ERRO] Nenhuma URL/IP válida para monitorar!")
        return

    monitorando = True
    thread = threading.Thread(target=verificar_urls)
    thread.daemon = True
    thread.start()
    adicionar_log("[INFO] Monitoramento iniciado.")

def parar_monitoramento():
    """Para o monitoramento."""
    global monitorando
    monitorando = False
    adicionar_log("[INFO] Monitoramento parado.")

def validar_url(url):
    """Valida se o link ou IP inserido é válido."""
    try:
        resultado = urlparse(url)
        return all([resultado.scheme, resultado.netloc])
    except ValueError:
        return False

def atualizar_barras():
    """Atualiza o painel de barras com base no progresso das URLs."""
    for i, progresso in enumerate(progresso_barras):
        for j in range(20):
            if status_urls[i] == "online":
                cor = "green" if j < progresso else "gray"
            elif status_urls[i] == "offline":
                cor = "red" if j < progresso else "gray"
            else:
                cor = "gray"

            canvas.itemconfig(barras[i][j], fill=cor)

def atualizar_mensagem_central():
    """Exibe uma lista de todas as URLs fora do ar no centro da tela."""
    if urls_fora_do_ar:
        mensagem = "\n".join([f"{nome} - SISTEMA FORA DO AR" for nome in urls_fora_do_ar.values()])
        mensagem_central.config(text=mensagem)
    else:
        mensagem_central.config(text="Todos os sistemas estão online.")

def adicionar_log(mensagem):
    """Adiciona uma mensagem ao painel de logs."""
    painel_logs.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {mensagem}\n")
    painel_logs.see(tk.END)

# Interface Gráfica
janela = tk.Tk()
janela.title("Painel de Monitoramento com Gráfico")
janela.geometry("1200x600")

# Adiciona o gráfico no Tkinter
frame_grafico = tk.Frame(janela)
frame_grafico.grid(row=0, column=0, padx=20, pady=20)

# Criação do gráfico de barras (online vs offline)
fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=frame_grafico)  # Tela Tkinter para o gráfico
canvas.get_tk_widget().pack()

# Entrada de URLs e Nomes Amigáveis
frame_urls = tk.Frame(janela)
frame_urls.grid(row=1, column=0, padx=20, pady=10)

tk.Label(frame_urls, text="Insira URLs ou IPs e seus Nomes Amigáveis (máximo 6):").grid(row=0, column=0, columnspan=2)

entradas_urls = []
entradas_nomes = []
for i in range(6):
    tk.Label(frame_urls, text=f"URL {i + 1}:").grid(row=i + 1, column=0, padx=5, pady=2, sticky="e")
    entrada_url = tk.Entry(frame_urls, width=40)
    entrada_url.grid(row=i + 1, column=1, padx=5, pady=2, sticky="w")
    entradas_urls.append(entrada_url)

    tk.Label(frame_urls, text="Nome Amigável:").grid(row=i + 1, column=2, padx=5, pady=2, sticky="e")
    entrada_nome = tk.Entry(frame_urls, width=30)
    entrada_nome.grid(row=i + 1, column=3, padx=5, pady=2, sticky="w")
    entradas_nomes.append(entrada_nome)

# Painel de Barras Gráficas
frame_principal = tk.Frame(janela)
frame_principal.grid(row=2, column=0, padx=20, pady=20)

canvas = tk.Canvas(frame_principal, width=700, height=300)
canvas.pack()

barras = []
for i in range(6):
    y = 30 * i + 10
    barra_segmentos = []
    for j in range(20):
        x1 = 50 + j * 25
        x2 = x1 + 20
        segmento = canvas.create_rectangle(x1, y, x2, y + 20, fill="gray")
        barra_segmentos.append(segmento)
    barras.append(barra_segmentos)

# Mensagem Central
mensagem_central = tk.Label(janela, text="Todos os sistemas estão online.", font=("Helvetica", 16), anchor="center")
mensagem_central.grid(row=3, column=0, padx=20, pady=20)

# Painel de Logs
frame_logs = tk.Frame(janela)
frame_logs.grid(row=4, column=0, padx=20, pady=20)

painel_logs = tk.Listbox(frame_logs, width=100, height=10)
painel_logs.pack()

# Botões de Controle
frame_botoes = tk.Frame(janela)
frame_botoes.grid(row=5, column=0, padx=20, pady=20)

botao_iniciar = tk.Button(frame_botoes, text="Iniciar Monitoramento", command=iniciar_monitoramento, width=20)
botao_iniciar.grid(row=0, column=0, padx=10, pady=5)

botao_parar = tk.Button(frame_botoes, text="Parar Monitoramento", command=parar_monitoramento, width=20)
botao_parar.grid(row=0, column=1, padx=10, pady=5)

janela.mainloop()
