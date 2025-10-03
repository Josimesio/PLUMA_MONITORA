import requests
import time

# Configurações
url = "https://epfa-test.fa.us2.oraclecloud.com/fscmUI/faces/FuseWelcome?_afrLoop=29754934183513255&_afrWindowMode=0&_afrWindowId=null&_adf.ctrl-state=jfpood4hh_1&_afrFS=16&_afrMT=screen&_afrMFW=1536&_afrMFH=695&_afrMFDW=1536&_afrMFDH=864&_afrMFC=8&_afrMFCI=0&_afrMFM=0&_afrMFR=120&_afrMFG=0&_afrMFS=0&_afrMFO=0"  # Substitua pela URL ou IP a ser monitorado
tempo_verificacao = 30 # Intervalo entre verificações, em segundos

def monitorar_sistema():
    while True:
        try:
            resposta = requests.get(url, timeout=10)
            if resposta.status_code == 200:
                print(f"[OK] {url} está no ar.")
            else:
                print(f"[ERRO] {url} retornou o status: {resposta.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[FALHA] {url} está fora do ar. Detalhes: {e}")

        time.sleep(tempo_verificacao)

if __name__ == "__main__":
    monitorar_sistema()
