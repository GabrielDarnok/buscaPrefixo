from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time, sys

options = Options()
options.add_argument("--headless")

driver_path = ChromeDriverManager().install()

navegador = webdriver.Chrome(options=options)


while True:
    asn = input("Digite o ASN que quer buscar: ")
    if asn.isdigit():
        break
    elif asn == 52863:
        print("O ASN da upx não pode ser analisado. Insira outro")
    else:
        print("Por favor, digite apenas números.")

try:
    navegador.get("https://upx.tools/")

    navegador.find_element('xpath', '//*[@id="__next"]/div/div[3]/form/input').send_keys(asn)

    navegador.find_element('xpath', '//*[@id="__next"]/div/div[3]/form/button').click()

    time.sleep(3)

    # Coleta do prefixos
    elementos = navegador.find_elements('css selector', '.p-3.break-words')

    prefixos = []

    for elemento in elementos:
        prefixos.append(elemento.text)
            
    # Coleta do o nome das empresas
    name = ""
    elementos = navegador.find_elements('css selector', '.overflow-ellipsis.whitespace-nowrap.overflow-hidden')
    quantidade_colunas = len(elementos) - 1 
    for index, elemento in enumerate(elementos):
        if "UPX" in elemento.text.upper():
            name = elemento.text
            coluna = index
    
    if not name:
        print("UPX não consta nas rotas de upstream.")
        sys.exit()

    # Coleta a porcentagem
    elementos = navegador.find_elements('css selector', '.CircularProgressbar-text')

    porcentagens = []

    for index, elemento in enumerate(elementos):
        if index % quantidade_colunas == (coluna - 1):
            porcentagens.append(elemento.text)

    prefixos_analise = []

    for index, porcentagem in enumerate(porcentagens):
        valor_numerico = float(porcentagem.strip('%'))

        if valor_numerico > 0 and ":" not in prefixos[index]:
            prefixos_analise.append(prefixos[index])

    if not prefixos_analise:
        print("Cliente não está anunciando nenhum prefixo para a UPX")
        sys.exit()
    print("Ips que precisam ser analisados")
    for prefixo in prefixos_analise:
        print(f"{prefixo}")
    
    prefixos_str = ', '.join(prefixos_analise)

    prefixos_formatados = prefixos_str.replace(', ', ' or ')
    
    print(f"Comando para analisar o trafégo: \ntcpdump -nni $IFIN net '({prefixos_formatados})' and udp port 53 -c 100")
    navegador.quit()
except Exception as e:
    print(f"Não foi possivel concluir o ciclo de pesquisa erro: {e}")

