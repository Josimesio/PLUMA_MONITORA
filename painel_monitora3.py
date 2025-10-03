import time
import threading
import tkinter as tk
import requests
from urllib.parse import urlparse

# Configurações iniciais
tempo_verificacao = 5
monitorando = False
status_urls = [None] * 6
progresso_barras = [0] * 6
urls_fora_do_ar = {}
urls_nomes = {}
urls = ["", "", "", "", "", ""]

def verificar_urls():
    global monitorando
    while monitorando:
        for i, url in enumerate(urls):
            if not url.strip():
                continue
            try:
                resposta = requests.get(url, timeout=10)
                if resposta.status_code == 200:
                    status_urls[i] = "online"
                    urls_fora_do_ar.pop(url, None)
                else:
                    status_urls[i] = "offline"
                    urls_fora_do_ar[url] = urls_nomes.get(url, "SISTEMA DESCONHECIDO")
            except requests.exceptions.RequestException:
                status_urls[i] = "offline"
                urls_fora_do_ar[url] = urls_nomes.get(url, "SISTEMA DESCONHECIDO")

            atualizar_progresso(i)

        atualizar_mensagem_central()
        time.sleep(tempo_verificacao)

def validar_url(url):
    try:
        resultado = urlparse(url)
        return all([resultado.scheme, resultado.netloc])
    except ValueError:
        return False

def atualizar_progresso(indice):
    if status_urls[indice] == "online" or status_urls[indice] == "offline":
        if progresso_barras[indice] < 20:
            progresso_barras[indice] += 1
    else:
        progresso_barras[indice] = 0
    atualizar_barras()

def iniciar_monitoramento():
    global monitorando
    urls_atualizadas = [entrada_url.get().strip() for entrada_url in entradas_urls]
    nomes_atualizados = [entrada_nome.get().strip() for entrada_nome in entradas_nomes]

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
    global monitorando
    monitorando = False
    adicionar_log("[INFO] Monitoramento parado.")

def atualizar_barras():
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
    if urls_fora_do_ar:
        mensagem = "\n".join([f"{nome} - SISTEMA FORA DO AR" for nome in urls_fora_do_ar.values()])
        mensagem_central.config(text=mensagem)
    else:
        mensagem_central.config(text="Todos os sistemas estão online.")

def adicionar_log(mensagem):
    painel_logs.config(state="normal")
    painel_logs.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {mensagem}\n")
    painel_logs.see(tk.END)
    painel_logs.config(state="disabled")

janela = tk.Tk()
janela.title("Painel de Monitoramento")
janela.geometry("1000x600")
janela.minsize(800, 500)
janela.rowconfigure(1, weight=1)
janela.columnconfigure(0, weight=1)

frame_urls = tk.Frame(janela)
frame_urls.pack(fill="x", padx=10, pady=10)

entradas_urls = []
entradas_nomes = []
tk.Label(frame_urls, text="Insira URLs ou IPs e seus Nomes Amigáveis (máximo 6):").grid(row=0, column=0, columnspan=4)

for i in range(6):
    tk.Label(frame_urls, text=f"URL {i + 1}:").grid(row=i + 1, column=0, padx=5, pady=2, sticky="e")
    entrada_url = tk.Entry(frame_urls, width=40)
    entrada_url.grid(row=i + 1, column=1, padx=5, pady=2, sticky="w")
    entradas_urls.append(entrada_url)

    tk.Label(frame_urls, text="Nome Amigável:").grid(row=i + 1, column=2, padx=5, pady=2, sticky="e")
    entrada_nome = tk.Entry(frame_urls, width=30)
    entrada_nome.grid(row=i + 1, column=3, padx=5, pady=2, sticky="w")
    entradas_nomes.append(entrada_nome)

frame_principal = tk.Frame(janela)
frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

canvas = tk.Canvas(frame_principal, bg="white")
canvas.pack(fill="both", expand=True)

barras = []
nomes_labels = []
for i in range(6):
    y = 30 * i + 10
    barra_segmentos = []
    for j in range(20):
        x1 = 50 + j * 25
        x2 = x1 + 20
        segmento = canvas.create_rectangle(x1, y, x2, y + 20, fill="gray")
        barra_segmentos.append(segmento)
    barras.append(barra_segmentos)

    nome_label = tk.Label(frame_principal, text="", font=("Arial", 10), anchor="w")
    nome_label.place(x=650, y=y + 5)
    nomes_labels.append(nome_label)

mensagem_central = tk.Label(janela, text="Todos os sistemas estão online.", font=("Arial", 14), fg="red", justify="center")
mensagem_central.pack(pady=10)

frame_logs = tk.Frame(janela)
frame_logs.pack(fill="both", expand=False, padx=10, pady=5)

scrollbar = tk.Scrollbar(frame_logs)
scrollbar.pack(side="right", fill="y")

painel_logs = tk.Text(frame_logs, height=8, yscrollcommand=scrollbar.set)
painel_logs.pack(side="left", fill="both", expand=True)
scrollbar.config(command=painel_logs.yview)

frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=5)

btn_iniciar = tk.Button(frame_botoes, text="Iniciar Monitoramento", command=iniciar_monitoramento)
btn_iniciar.grid(row=0, column=0, padx=10)

btn_parar = tk.Button(frame_botoes, text="Parar Monitoramento", command=parar_monitoramento)
btn_parar.grid(row=0, column=1, padx=10)

janela.mainloop()