"""

   Scrapper for Brazilian Ceará (CE) State Trade Board

   As CE Trade Board is using javascript, I found impossible to get the process info using GET or POST request...
   The alternative was using Selenium with a headless Chrome instance. It's messy but it gets the job done!

"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def ce_update(protocol):

    options = Options()
    options.headless = True

    browser = webdriver.Chrome(options=options)
    options.add_argument('headless')

    # request protocol info
    browser.get('http://portalservicos.jucec.ce.gov.br/Portal/pages/consultaProcesso.jsf')

    username = browser.find_element_by_name('protocolo')
    username.send_keys(protocol)

    browser.find_element_by_xpath('//*[@id="formulario"]/div/div/div[1]/div[2]/div/a').click()

    # get general process status
    s = browser.find_element_by_class_name('dados-processo').text

    # handle 'no info error'
    if s == 'Nenhum registro encontrado.':
        parsed = {'situacao': f'Nenhum registro encontrado para Protocolo {protocol}', 'nome': 'N/A', 'cnpj': 'N/A',
                  'nire': 'N/A', 'dataentrada': 'N/A', 'dataretorno': 'N/A', 'dataaprovacao': 'N/A',
                  'pendencias': 'N/A'}

    # check if there's pending issues at process ("pendências")
    else:
        try:
            pend = browser.find_element_by_class_name('pendencias').text
            start = 'Pendências'
            pendencias = (pend.split(start))[1].strip()
        except:
            pendencias = 'N/A'

        # parse retrieved info in specific fields - use tries as JUCEC website not always have all fields
        try:
            start = 'Situação:'
            end = '\n'
            situacao = (s.split(start))[1].split(end)[1].strip()
        except:
            situacao = 'N/A'

        try:
            start = 'Nome:'
            end = '\n'
            nome = (s.split(start))[1].split(end)[1].strip()
        except:
            nome = 'N/A'

        try:
            start = 'CNPJ:'
            end = '\n'
            cnpj = (s.split(start))[1].split(end)[1].strip()
        except:
            cnpj = 'N/A'

        try:
            start = 'Nire:'
            end = '\n'
            nire = (s.split(start))[1].split(end)[1].strip()
        except:
            nire = 'N/A'

        try:
            start = 'Data da Entrada:'
            end = '\n'
            dataentrada = (s.split(start))[1].split(end)[1].strip()
        except:
            dataentrada = 'N/A'

        try:
            start = 'Data Retorno:'
            end = '\n'
            dataretorno = (s.split(start))[1].split(end)[1].strip()
        except:
            dataretorno = 'N/A'

        try:
            start = 'Data de Aprovação:'
            end = '\n'
            dataaprovacao = (s.split(start))[1].split(end)[1].strip()
        except:
            dataaprovacao = 'N/A'

        try:
            start = 'Inscrição Municipal:'
            end = '\n'
            inscmunicipal = (s.split(start))[1].split(end)[1].strip()
        except:
            inscmunicipal = 'N/A'

        try:
            start = 'Alvará de Funcionamento:'
            end = '\n'
            alvara = (s.split(start))[1].split(end)[1].strip()
        except:
            alvara = 'N/A'

        parsed = {'situacao': situacao, 'nome': nome, 'cnpj': cnpj, 'nire': nire, 'dataentrada': dataentrada,
                  'dataretorno': dataretorno,'pendencias': pendencias, 'dataaprovacao': dataaprovacao,
                  'inscmunicipal': inscmunicipal, 'alvara': alvara}

    # quit webdriver process to avoid running out of system memory due to multiple instances of Chrome
    browser.quit()
    # sleep some time to get well rested and fresh
    time.sleep(3)
    # return results
    return parsed