import json
import requests
from time import sleep
from threading import Thread, Lock
import sys
from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
from requests import get
from datetime import datetime
from termcolor import colored
from simple_colors import *


global config
#config = {'url': 'https://api.telegram.org/bot1610447655:AAHj4vqxYCxX0d236VWLMpZKH0MGiM9Oh0E/', 'lock': Lock()} # ORIGINAL
config = {'url': 'https://api.telegram.org/bot1562077602:AAFX8anr_hfME3Zdeqqsd0E84hmUyFsWg0Q/', 'lock': Lock()} # TESTE
cluster = MongoClient("mongodb+srv://db_user:uOKmcSP1QSntVUTT@cluster0.uf6yd.mongodb.net/db_informa?retryWrites=true&w=majority")

# CRIA A BASE DE DADOS (quando em seguida inserir os dados)
db = cluster["bot"]
#collection = db["db_informa"] # ORIGINAL
collection = db["db_informa_teste"] # TESTE

def del_update(data):
    global config
    config['lock'].acquire()
    requests.post(config['url'] + 'getUpdates', {'offset': data['update_id'] + 1})
    config['lock'].release()

def insert_db(chat_id, perg_usu):
    global config
    resp_usu = None
    collection.insert_one({"chat_id": chat_id, "ultima_perg": perg_usu, "ultima_resp": resp_usu})

def update_db(chat_id, nov_per_bd):
    global config
    collection.update_one({"chat_id": chat_id}, {"$set": {"ultima_perg": nov_per_bd}})

def update_db_bot(chat_id, resp_bot):
    global config
    collection.update_one({"chat_id": chat_id}, {"$set": {"ultima_resp": resp_bot}})

def lista(data, msg):
    global config

    msg = ('📚 MENU de INFORMAÇÕES\n\n'
            '1. Previsão do Tempo ☀️\n'
            '2. Últimas noticias do BRASIL 💬 \n'
            '3. Cotação da IBOVESPA 💰 \n'
            '4. Últimas notícias do BRASILEIRÃO ⚽ \n'
            '5. Outras cotações 💱 \n'
            '6. Horóscopo do Dia ♎ \n'
            '7. Estatística COVID-19 🦠 \n'
            '8. Lista de DIVIDENDOS - IBOVESPA 🤑')

    config['lock'].acquire()
    requests.post(config['url'] + 'sendMessage', {'chat_id': data['message']['chat']['id'], 'text': str(msg)})
    config['lock'].release()

def ibovespa(data, msg):
    global config, str

    dia_hoje = datetime.now().strftime("%d/%m/%Y | %H:%M")
    url = get('https://economia.uol.com.br/cotacoes/bolsas/', verify=False)
    html = bs(url.text, 'html.parser')
    lista = html.find_all('div', class_='col-lg-8 col-md-8 col-sm-8 col-xs-8')

    url = get('https://economia.uol.com.br/cotacoes/', verify=False)
    html = bs(url.text, 'html.parser')
    ibo = html.find_all('h3', class_='tituloGrafico')

    # MAIORES ALTAS
    x = 0
    for box in lista:
        titulo = box.find('tr').text
        ps = box.find_all('td')
        acao_alta = ps[0].text
        perc_acao_alta = ps[1].text
        valor_acao_alta = ps[2].text

        x += 1
        if x == 1:
            primeiro_alta = ('🥇' + acao_alta + " " + perc_acao_alta + " " + valor_acao_alta).replace(".SA","")
        if x == 2:
            primeiro_baixa = ('🥇' + acao_alta + " " + perc_acao_alta + " " + valor_acao_alta).replace(".SA","")
        if x == 3:
            primeiro_negociada = ('🥇' + acao_alta + " " + perc_acao_alta + " " + valor_acao_alta).replace(".SA","")

    # MAIORES BAIXAS
    x = 0
    for box in lista:
        titulo = box.find('tr').text
        ps = box.find_all('td')
        acao_baixa = ps[3].text
        perc_acao_baixa = ps[4].text
        valor_acao_baixa = ps[5].text

        x += 1
        if x == 1:
            segunda_alta = ('🥈' + acao_baixa + " " + perc_acao_baixa + " " + valor_acao_baixa).replace(".SA","")
        if x == 2:
            segunda_baixa = ('🥈' + acao_baixa + " " + perc_acao_baixa + " " + valor_acao_baixa).replace(".SA","")
        if x == 3:
            segunda_negociada = ('🥈' + acao_baixa + " " + perc_acao_baixa + " " + valor_acao_baixa).replace(".SA","")

    # MAIS NEGOCIADAS
    x = 0
    for box in lista:
        titulo = box.find('tr').text
        ps = box.find_all('td')
        acao_negociada = ps[6].text
        perc_acao_negociada = ps[7].text
        valor_acao_negociada = ps[8].text

        x += 1
        if x == 1:
            terceira_alta = ('🥉' + acao_negociada + " " + perc_acao_negociada + " " + valor_acao_negociada).replace(".SA","")
        if x == 2:
            terceira_baixa = ('🥉' + acao_negociada + " " + perc_acao_negociada + " " + valor_acao_negociada).replace(".SA","")
        if x == 3:
            terceira_negociada = ('🥉' + acao_negociada + " " + perc_acao_negociada + " " + valor_acao_negociada).replace(".SA","")

    msg = str('Valores atualizados em - ' + dia_hoje + "\n\n") + ibo[5].text + "\n\n" + str("COTAÇÕES EM ALTA"+ "\n") \
          + str(primeiro_alta) + "\n" \
          + str(segunda_alta) + "\n" \
          + str(terceira_alta) + "\n\n" \
          + str("COTAÇÕES EM BAIXAS"+ "\n") \
          + str(primeiro_baixa) + "\n"\
          + str(segunda_baixa) + "\n"\
          + str(terceira_baixa) + "\n\n" \
          + str("COTAÇÕES MAIS NEGOCIADAS"+ "\n") \
          + str(primeiro_negociada)+ "\n" \
          + str(segunda_negociada) + "\n" \
          + str(terceira_negociada) + "\n\n" \
          + str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
          str("https://economia.uol.com.br/cotacoes/bolsas/")

    config['lock'].acquire()
    requests.post(config['url'] + 'sendMessage', {'chat_id': data['message']['chat']['id'], 'text': str(msg)})
    config['lock'].release()
    Thread(target=send_message,args=(data, '↩ Digite LISTA para retornar ao MENU PRINCIPAL')).start()

def cotacao_moedas(data, msg):
    global config, str

    dia_hoje = datetime.now().strftime("%d/%m/%Y | %H:%M")
    url = get('https://economia.uol.com.br/cotacoes/', verify=False)
    html = bs(url.text, 'html.parser')
    valor1 = html.find_all('td')
    ps = html.find_all('h3', class_='tituloGrafico')

    # outras moedas
    outras_moedas = valor1[0].text.strip() + " | " + valor1[1].text + " | " + valor1[2].text
    outras_moedas1 = valor1[3].text.strip() + " | " + valor1[4].text + " | " + valor1[5].text
    outras_moedas2 = valor1[6].text.strip() + " | " + valor1[7].text + " | " + valor1[8].text
    outras_moedas3 = valor1[9].text.strip() + " | " + valor1[10].text + " | " + valor1[11].text

    # outros indices
    outros_indices = valor1[12].text.strip() + " | " + valor1[13].text
    outros_indices1 = valor1[14].text.strip() + " | " + valor1[15].text
    outros_indices2 = valor1[16].text.strip() + " | " + valor1[17].text
    outros_indices3 = valor1[18].text.strip() + " | " + valor1[19].text

    # GERAIS
    gerais = valor1[80].text.strip() + " | " + valor1[81].text + " | " + valor1[82].text
    gerais1 = valor1[83].text.strip() + " | " + valor1[84].text + " | " + valor1[85].text
    gerais2 = valor1[86].text.strip() + " | " + valor1[87].text + " | " + valor1[88].text
    gerais3 = valor1[89].text.strip() + " | " + valor1[90].text + " | " + valor1[91].text
    gerais4 = valor1[92].text.strip() + " | " + valor1[93].text + " | " + valor1[94].text
    gerais5 = valor1[95].text.strip() + " | " + valor1[96].text + " | " + valor1[97].text

    # INFLAÇÃO
    inflacao = valor1[102].text.strip() + " | " + valor1[103].text + " | " + valor1[104].text
    inflacao1 = valor1[105].text.strip() + " | " + valor1[106].text + " | " + valor1[107].text
    inflacao2 = valor1[108].text.strip() + " | " + valor1[109].text + " | " + valor1[110].text
    inflacao3 = valor1[111].text.strip() + " | " + valor1[112].text + " | " + valor1[113].text

    # Commodities
    Commodities = valor1[118].text.strip() + " | " + valor1[119].text + " | " + valor1[120].text
    Commodities1 = valor1[121].text.strip() + " | " + valor1[122].text + " | " + valor1[123].text
    Commodities2 = valor1[124].text.strip() + " | " + valor1[125].text + " | " + valor1[126].text
    Commodities3 = valor1[127].text.strip() + " | " + valor1[128].text + " | " + valor1[129].text
    Commodities4 = valor1[130].text.strip() + " | " + valor1[131].text + " | " + valor1[132].text

    # Produtos agrícolas
    produtos_agricolas = valor1[136].text.strip() + " | " + valor1[137].text.strip()
    produtos_agricolas1 = valor1[138].text.strip() + " | " + valor1[139].text.strip()
    produtos_agricolas2 = valor1[140].text.strip() + " | " + valor1[141].text.strip()
    produtos_agricolas3 = valor1[142].text.strip() + " | " + valor1[143].text.strip()
    produtos_agricolas4 = valor1[144].text.strip() + " | " + valor1[145].text.strip()
    produtos_agricolas5 = valor1[146].text.strip() + " | " + valor1[147].text.strip()
    produtos_agricolas6 = valor1[148].text.strip() + " | " + valor1[149].text.strip()

    msg = str('Valores atualizados em - ' + dia_hoje + "\n\n") + str('🎯️ Outras moedas' + '\n') + \
          str('▪️' + ps[0].text.replace("% ", " | ").replace("Dólar Comercial ", "Dólar Comercial | ") + '\n') + \
          str('▪️' + outras_moedas + '\n') + \
          str('▪️' + ps[1].text.replace("% ", " | ").replace("  ", " | ") + '\n') + \
          str('▪️' + outras_moedas1 + '\n') + \
          str('▪️' + outras_moedas2 + '\n') + \
          str('▪️' + outras_moedas3 + '\n\n') + \
          str('🎯️ Outros índices' + '\n') + \
          str('▪️' + outros_indices + '\n') + \
          str('▪️' + outros_indices1 + '\n') + \
          str('▪️' + outros_indices2 + '\n') + \
          str('▪️' + outros_indices3 + '\n\n') + \
          str('🎯️ Gerais' + '\n') + \
          str('▪️' + gerais + '\n') + \
          str('▪️' + gerais1 + '\n') + \
          str('▪️' + gerais2 + '\n') + \
          str('▪️' + gerais3 + '\n') + \
          str('▪️' + gerais4 + '\n') + \
          str('▪️' + gerais5 + '\n\n') + \
          str('🎯️ Inflação' + '\n') + \
          str('▪️' + inflacao + '\n') + \
          str('▪️' + inflacao1 + '\n') + \
          str('▪️' + inflacao2 + '\n') + \
          str('▪️' + inflacao3 + '\n\n') + \
          str('🎯️ Commodities' + '\n') + \
          str('▪️' + Commodities + '\n') + \
          str('▪️' + Commodities1 + '\n') + \
          str('▪️' + Commodities2 + '\n') + \
          str('▪️' + Commodities3 + '\n') + \
          str('▪️' + Commodities4 + '\n\n') + \
          str('🎯 ️Produtos agrícolas' + '\n') + \
          str('▪️' + produtos_agricolas + '\n') + \
          str('▪️' + produtos_agricolas1 + '\n') + \
          str('▪️' + produtos_agricolas2 + '\n') + \
          str('▪️' + produtos_agricolas3 + '\n') + \
          str('▪️' + produtos_agricolas4 + '\n') + \
          str('▪️' + produtos_agricolas5 + '\n') + \
          str('▪️' + produtos_agricolas6 + '\n\n') + \
          str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
          str("https://economia.uol.com.br/cotacoes/")

    config['lock'].acquire()
    requests.post(config['url'] + 'sendMessage', {'chat_id': data['message']['chat']['id'], 'text': str(msg)})
    Thread(target=send_message,args=(data, '↩ Digite LISTA para retornar ao MENU PRINCIPAL')).start()
    config['lock'].release()

def previsao(data, estado, msg):
    global config, str

    url = get('https://www.climatempo.com.br/brasil', verify=False)
    html = bs(url.text, 'html.parser')
    lista_cap = html.find_all('div', class_='card-capitals')
    dia_hoje = datetime.now().strftime("%d/%m/%Y | %H:%M")

    for lista_cap1 in lista_cap:
        capitais_brasileiras = lista_cap1.find_all('a', class_='city')
        temperatura_max = lista_cap1.find_all('p', class_='max')
        temperatura_min = lista_cap1.find_all('p', class_='min')
        chuva = lista_cap1.find_all('p', class_='-gray _flex _align-center')

        if capitais_brasileiras[0].text[-2:] == estado.upper():
            capital = capitais_brasileiras[0].text
            max = temperatura_max[0].text.replace("\n", "")
            min = temperatura_min[0].text.replace("\n", "")
            chuva = chuva[0].text.replace("\n", "")

            msg = str("Previsão atualizada em " + dia_hoje + "\n\n"
                  + "📍 " + capital.upper()) + "\n" \
                  + "🌡️ " + str(" Máx: " + max) + " | " + str("Min: " + min) + "\n"\
                  + "☔ " + str(chuva) + "\n\n"\
                  + "Para saber mais, acesse o link abaixo 👇 " + '\n' + "https://www.climatempo.com.br/brasil"

            config['lock'].acquire()
            requests.post(config['url'] + 'sendMessage', {'chat_id': data['message']['chat']['id'], 'text': str(msg)})
            Thread(target=send_message,args=(data, '↩ Digite LISTA para retornar ao MENU PRINCIPAL')).start()
            config['lock'].release()

def noticia(data,msg):
    global config, str

    url = get('https://economia.uol.com.br/cotacoes/bolsas/acoes/bvsp-bovespa/bidi4-sa', verify=False)
    html = bs(url.text, 'html.parser')
    ps = html.find_all('h3', class_='thumb-title title-xsmall title-lg-small')
    msg = str('Noticías mais lida no site da UOL ' + "\n\n") + \
            str('▪️' + ps[0].text + '\n\n') + \
            str('▪️' + ps[1].text + '\n\n') + \
            str('▪️' + ps[2].text + '\n\n') + \
            str('▪️' + ps[3].text + '\n\n') + \
            str('▪️' + ps[4].text + '\n\n') + \
            str('▪️' + ps[5].text + '\n\n') + \
            str('▪️' + ps[6].text + '\n\n') + \
            str('▪️' + ps[7].text + '\n\n') + \
            str('▪️' + ps[8].text + '\n\n') + \
            str('▪️' + ps[9].text + '\n\n') + \
            str('▪️' + ps[10].text + '\n\n') + \
            str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
            str("https://www.uol.com.br/")

    config['lock'].acquire()
    requests.post(config['url'] + 'sendMessage', {'chat_id': data['message']['chat']['id'], 'text': str(msg)})
    Thread(target=send_message,args=(data, '↩ Digite LISTA para retornar ao MENU PRINCIPAL')).start()
    config['lock'].release()

def horoscopo(data, signo):
    global config, str

    url = get('https://www.uol.com.br/universa/horoscopo/' + signo + '/horoscopo-do-dia/', verify=False)
    html = bs(url.text, 'html.parser')
    lista = html.find_all('div', class_='col-xs-8 col-sm-21 col-md-21')

    if signo == 'aquario':
        cabecalho = "♒ AQUÁRIO" + " | 21/01 a 19/02"
    if signo == 'peixes':
        cabecalho = "♓ PEIXES" + " | 20/02 a 20/03"
    if signo == 'aries':
        cabecalho = "♈ Áries" + " | 21/03 a 20/04"
    if signo == 'touro':
        cabecalho = "♉ TOURO" + " | 21/04 a 20/05"
    if signo == 'gemeos':
        cabecalho = "♊ GÊMEOS" + " | 21/05 a 20/06"
    if signo == 'cancer':
        cabecalho = "♋ CÂNCER" + " | 21/06 a 21/07"
    if signo == 'leao':
        cabecalho = "♌ LEÃO" + " | 22/07 a 22/08"
    if signo == 'virgem':
        cabecalho = "♍ VIRGEM" + " | 23/08 a 22/09"
    if signo == 'libra':
        cabecalho = "♎ LIBRA" + " | 23/09 a 22/10"
    if signo == 'escorpiao':
        cabecalho = "♏ ESCORPIÃO" + " | 23/10 a 21/11"
    if signo == 'sagitario':
        cabecalho = "♐ SAGITÁRIO" + " | 22/11 a 21/12"
    if signo == 'capricornio':
        cabecalho = "♑ CAPRICÓRNIO" + " | 22/12 a 20/01"

    x = html.find_all('p')
    msg1 = x[2].text

    msg = str(cabecalho + "\n\n") + \
          str("🔘 " + msg1 + '\n\n') + \
          str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
          str("https://www.uol.com.br/universa/horoscopo/" + signo + "/horoscopo-do-dia/")

    # ENVIA A MSG
    config['lock'].acquire()
    requests.post(config['url'] + 'sendMessage', {'chat_id': data['message']['chat']['id'], 'text': str(msg)})
    Thread(target=send_message, args=(
    data, '⤴ Digite VOLTAR para retornar ao MENU ANTERIOR \n' + '↩ Digite LISTA para retornar ao MENU PRINCIPAL')).start()
    config['lock'].release()

    # informa em qual MENU o usuário esta
    Thread(target=update_db_bot, args=(chat_id, "sub_menu_horoscopo")).start()

def noticia_esportes(data, msg):
    global config, str

    url = get('https://www.uol.com.br/esporte/futebol/campeonatos/brasileirao/', verify=False)
    html = bs(url.text, 'html.parser')
    ps = html.find_all('h3', class_='thumb-title title-xsmall title-lg-small')
    msg = str('Últimas notícias do BRASILEIRÃO ' + "\n\n") + \
          str('▪️' + ps[0].text + '\n\n') + \
          str('▪️' + ps[1].text + '\n\n') + \
          str('▪️' + ps[2].text + '\n\n') + \
          str('▪️' + ps[3].text + '\n\n') + \
          str('▪️' + ps[4].text + '\n\n') + \
          str('▪️' + ps[5].text + '\n\n') + \
          str('▪️' + ps[6].text + '\n\n') + \
          str('▪️' + ps[7].text + '\n\n') + \
          str('▪️' + ps[8].text + '\n\n') + \
          str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
          str("https://www.uol.com.br/esporte/futebol/campeonatos/brasileirao/")

    config['lock'].acquire()
    requests.post(config['url'] + 'sendMessage', {'chat_id': data['message']['chat']['id'], 'text': str(msg)})
    Thread(target=send_message,args=(data, '↩ Digite LISTA para retornar ao MENU PRINCIPAL')).start()
    config['lock'].release()

def noticia_covid(data, tipo_covid):
    global config, str

    if tipo_covid == "casos":
        url = get('https://news.google.com/covid19/map?hl=pt-BR&gl=BR&ceid=BR%3Apt-419&mid=%2Fm%2F015fr', verify=False)
        html = bs(url.text, 'html.parser')
        titulo = html.find_all('th')
        dados = html.find_all('td')
        pais = html.find_all('div', class_='TWa0lb')

        # GLOBAL
        msg = str(pais[0].text + '\n') + \
              str(titulo[1].text + " | " + dados[0].text + '\n') + \
              str(titulo[2].text + " | " + dados[1].text + '\n') + \
              str(titulo[3].text + " | " + dados[3].text + '\n') + \
              str(titulo[4].text + " | " + dados[4].text + '\n\n')

        # BRASIL
        msg0 = str(pais[1].text + '\n') + \
               str(titulo[1].text + " | " + dados[5].text + '\n') + \
               str(titulo[2].text + " | " + dados[6].text + '\n') + \
               str(titulo[3].text + " | " + dados[8].text + '\n') + \
               str(titulo[4].text + " | " + dados[9].text + '\n\n')

        # TOP 1
        msg1 = str("TOP 1 | " + pais[2].text + '\n') + \
               str(titulo[1].text + " | " + dados[10].text + '\n') + \
               str(titulo[2].text + " | " + dados[11].text + '\n') + \
               str(titulo[3].text + " | " + dados[13].text + '\n') + \
               str(titulo[4].text + " | " + dados[14].text + '\n\n')

        # TOP 2
        msg2 = str("TOP 2 | " + pais[3].text + '\n') + \
               str(titulo[1].text + " | " + dados[15].text + '\n') + \
               str(titulo[2].text + " | " + dados[16].text + '\n') + \
               str(titulo[3].text + " | " + dados[18].text + '\n') + \
               str(titulo[4].text + " | " + dados[19].text + '\n\n')

        # TOP 3
        msg3 = str("TOP 3 | " + pais[4].text + '\n') + \
               str(titulo[1].text + " | " + dados[20].text + '\n') + \
               str(titulo[2].text + " | " + dados[21].text + '\n') + \
               str(titulo[3].text + " | " + dados[23].text + '\n') + \
               str(titulo[4].text + " | " + dados[24].text + '\n\n')

        msg_estado = 'TOP 3 Total de casos por ESTADO DO BRASIL ⤵️\n\n'
        msg_final = str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
                    str("encurtador.com.br/eoDM7")
        msg = msg + msg0 + '\n' + msg_estado + msg1 + msg2 + msg3 + msg_final

    elif tipo_covid == "vacinas":
        url = get('https://news.google.com/covid19/map?hl=pt-BR&gl=BR&ceid=BR%3Apt-419&state=4',verify=False)
        html = bs(url.text, 'html.parser')
        pais = html.find_all('div', class_='TWa0lb')
        titulo = html.find_all('th')
        dados = html.find_all('td')

        # GLOBAL
        msg = str(pais[0].text + '\n') + \
              str(titulo[1].text + " | " + dados[0].text + '\n') + \
              str(titulo[2].text + " | " + dados[1].text + '\n') + \
              str(titulo[3].text + " | " + dados[3].text + '\n') + \
              str(titulo[4].text + " | " + dados[4].text + '\n')

        # TOP 1
        msg0 = str("TOP 1 | " + pais[1].text + '\n') + \
               str(titulo[1].text + " | " + dados[5].text + '\n') + \
               str(titulo[2].text + " | " + dados[6].text + '\n') + \
               str(titulo[3].text + " | " + dados[8].text + '\n') + \
               str(titulo[4].text + " | " + dados[9].text + '\n\n')

        # TOP 2
        msg1 = str("TOP 2 | " + pais[2].text + '\n') + \
               str(titulo[1].text + " | " + dados[10].text + '\n') + \
               str(titulo[2].text + " | " + dados[11].text + '\n') + \
               str(titulo[3].text + " | " + dados[13].text + '\n') + \
               str(titulo[4].text + " | " + dados[14].text + '\n\n')

        # TOP 3
        msg2 = str("TOP 3 | " + pais[3].text + '\n') + \
               str(titulo[1].text + " | " + dados[15].text + '\n') + \
               str(titulo[2].text + " | " + dados[16].text + '\n') + \
               str(titulo[3].text + " | " + dados[18].text + '\n') + \
               str(titulo[4].text + " | " + dados[19].text + '\n\n')

        msg_mundo = 'TOP 3 Total de doses aplicadas pelo MUNDO ⤵️\n\n'
        msg_final = str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
                    str("encurtador.com.br/bhNOQ")
        msg = msg + '\n' + msg_mundo + msg0 + msg1 + msg2 + msg_final

    # ENVIA A MSG
    config['lock'].acquire()
    requests.post(config['url'] + 'sendMessage', {'chat_id': data['message']['chat']['id'], 'text': str(msg)})
    Thread(target=send_message, args=(
    data, '⤴ Digite VOLTAR para retornar ao MENU ANTERIOR \n' + '↩ Digite LISTA para retornar ao MENU PRINCIPAL')).start()
    config['lock'].release()

    # informa em qual MENU o usuário esta
    Thread(target=update_db_bot, args=(chat_id, "sub_menu_estatistica")).start()

def pagamento_dividendo(data,msg):
    url = get('https://statusinvest.com.br/acoes/proventos/ibovespa', verify=False)
    html = bs(url.text, 'html.parser')
    link_list = html.find_all('input')

    for link in link_list:
        if 'value' in link.attrs:
            link_1 = str(link.attrs['value'])
            if link_1[0] == '{':
                string = link_1

                # TEXTO COMPLETO
                qtd_dividendos = string.count('{"code":"')  # TOTAL DE AÇÕES COM DIVIDENDOS

                x = 0
                y = 0
                palavras = []
                print(qtd_dividendos)
                exit()
                if qtd_dividendos != 0:
                    while x < qtd_dividendos:
                        acao = string.find('code')
                        dividendo = string.find('resultAbsoluteValue')
                        dateCom = string.find('"dateCom":"')
                        datePg = string.find('paymentDividend')
                        tipo = string.find('earningType')  # Tipo de PAGAMENTO
                        dy = string.find('"dy"')  # DY
                        recent = string.find('"recentEvents"')  # para identificar ate que casa deve pegar o DY
                        prox_acao = string.find('/acoes/')
                        tipo = string[tipo + 14:dy - 2]
                        dy = string[dy + 6:recent - 2]
                        acao = string[acao + 7:][:5]
                        dividendo = string[dividendo + 22:dividendo + 32]
                        dateCom = string[dateCom + 11:][:10]
                        datePg = string[datePg + 18:datePg + 28]

                        if datePg != '-","earnin' and datetime.now().strftime("%m") == datePg[3:][:2]:
                            msg = str("📌 Ação: " + acao + '\n') + \
                                  str("💰 R$: " + dividendo + '\n') + \
                                  str("📅 DataCom: " + dateCom + '\n') + \
                                  str("📆 DataPag: " + datePg + '\n') + \
                                  str("🖋️ Tipo: " + tipo + '\n') + \
                                  str("🔍 DY: " + dy + '\n\n')

                            palavras.append(msg)

                        string = string[prox_acao + 15:]
                        x = x + 1

                    list1 = palavras
                    str1 = ''.join(str(e) for e in list1)

                    msg = str1 + str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
                        str("https://statusinvest.com.br/acoes/proventos/ibovespa")

                else:
                    msg = str('Ops..Até o momento, para esse mês não temos pagamento de proventos ' + '\n') +\
                          str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
                          str("https://statusinvest.com.br/acoes/proventos/ibovespa")

                config['lock'].acquire()
                requests.post(config['url'] + 'sendMessage',
                              {'chat_id': data['message']['chat']['id'], 'text': str(msg)})
                Thread(target=send_message, args=(data, '↩ Digite LISTA para retornar ao MENU PRINCIPAL')).start()
                config['lock'].release()

def send_message(data, msg):
    global config
    config['lock'].acquire()
    requests.post(config['url'] + 'sendMessage', {'chat_id': data['message']['chat']['id'], 'text': str(msg)})
    config['lock'].release()

def get_file(file_path):
    global config
    return requests.get(config['url_file'] + str(file_path)).content

def upload_file(data, file):
    global config

    formatos = {'png': {'metodo': 'sendPhoto', 'send': 'photo'},
                'text': {'metodo': 'sendDocument', 'send': 'document'}}

    return requests.post(config['url'] + formatos['text' if '.txt' in file else 'png']['metodo'],
                         {'chat_id': data['message']['chat']['id']},
                         files={formatos['text' if '.txt' in file else 'png']['send']: open(file, 'rb')}).text

while True:
    pass

    sys.setrecursionlimit(10**6)

    x = ''
    encarte_enviado = None
    while 'result' not in x:
        try:
            x = json.loads(requests.get(config['url'] + 'getUpdates', verify=False).text)
        except Exception as e:
            x = ''
            if 'Failed to establish a new connection' in str(e):
                print('Perca de conexão')
            else:
                print('Erro desconhecido: ' + str(e))

    if len(x['result']) > 0:
        for data in x['result']:
            Thread(target=del_update, args=(data,)).start()

            nome = data['message']['from']['first_name'] # Nome do usuário

            if 'document' in data['message']:

                #print(json.dumps(data['message'], indent=1))
                file = get_file(json.loads(requests.post(
                    config['url'] + 'getFile?file_id=' + data['message']['document']['file_id']).text)['result'][
                                    'file_path'])
                open(data['message']['document']['file_name'], 'wb').write(file)

            #TRATAMENTO DE AUDIO
            elif 'voice' in data['message']:
                Thread(target=send_message, args=(data, nome + ', desculpa mas não consigo conversar por áudio, apenas texto 😊 ')).start()
                Thread(target=send_message,args=(data, 'Digite LISTA para retornar ao MENU PRINCIPAL')).start()

            #TRATAMENTO DE FOTO
            elif 'photo' in data['message']:
                Thread(target=send_message, args=(data, nome + ', desculpa mas não consigo conversar por imagens, apenas texto 😊 ')).start()
                Thread(target=send_message,args=(data, 'Digite LISTA para retornar ao MENU PRINCIPAL')).start()

            else:
                chat_id = data['message']['from']['id'] #Id do usuario
                #print(data['message'])
                perg_usu = data['message']['text'].lower().strip() #Pergunta do usuario

                #######################################################################################################
                #######################################################################################################
                # Verifica se já existe o id no banco
                result = collection.find_one({"chat_id": chat_id})
                usuario_antigo = None
                env_nov_not = None
                if result is None:
                    # INSERT NO BANCO
                    Thread(target=insert_db,args=(chat_id, perg_usu, env_nov_not)).start()
                    ult_resp_bot = ""
                    insert = True
                else:
                    # UPDATE NO BANCO
                    ult_per_bd = collection.find_one({"chat_id": chat_id})['ultima_perg']
                    nov_per_bd = data['message']['text'].lower().strip()
                    Thread(target=update_db, args=(chat_id,nov_per_bd)).start()
                #######################################################################################################
                #######################################################################################################

                # Retorna a ultima pergunta do usuário
                result = collection.find_one({"chat_id": chat_id})
                ult_resp_bot = result['ultima_resp']
                ult_per_usu = result['ultima_perg'].lower()
                nov_per_bd = data['message']['text'].lower().strip()

                if ult_resp_bot == None:
                    ult_resp_bot = ult_resp_bot
                else:
                    ult_resp_bot = ult_resp_bot.lower()

                # INICIO DO ChatBot
                if nov_per_bd in ('oi','ola','olá','/start'):
                    resp_bot = "🤙 Olá " + nome + ", tudo bem? Sou Assistente Virtual do Henry \n\n" \
                               "Digite LISTA para receber nosso menu de informações."
                    Thread(target=send_message, args=(data, resp_bot)).start()
                    Thread(target=update_db_bot, args=(chat_id, "olá")).start()
                    pass

                # ENVIO DA LISTA
                elif nov_per_bd.lower() == 'lista':
                    Thread(target=lista, args=(data, "")).start() # Envia a lista de catálogo
                    Thread(target=update_db, args=(chat_id,nov_per_bd)).start() # pergunta do usuário
                    Thread(target=update_db_bot, args=(chat_id, "envio_lista")).start() # resposta do bot
                    pass

                elif ult_resp_bot == 'pergunta_estado' and nov_per_bd.upper() in ('AC','AL','AP','AM','BA','CE','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO','DF'):
                    estado = nov_per_bd
                    Thread(target=previsao, args=(data,estado, "")).start()
                    Thread(target=update_db_bot, args=(chat_id, "previsao_enviada")).start()  # resposta do bot
                    pass

                # HOROSCOPO
                elif ult_resp_bot == 'pergunta_signo' and nov_per_bd in ('1','2','3','4','5','6','7','8','9','10','11','12'):
                    if nov_per_bd == '1':
                        signo = 'aquario'
                    if nov_per_bd == '2':
                        signo = "peixes"
                    if nov_per_bd == '3':
                        signo = "aries"
                    if nov_per_bd == '4':
                        signo = "touro"
                    if nov_per_bd == '5':
                        signo = "gemeos"
                    if nov_per_bd == '6':
                        signo = "cancer"
                    if nov_per_bd == '7':
                        signo = "leao"
                    if nov_per_bd == '8':
                        signo = "virgem"
                    if nov_per_bd == '9':
                        signo = "libra"
                    if nov_per_bd == '10':
                        signo = "escorpiao"
                    if nov_per_bd == '11':
                        signo = "sagitario"
                    if nov_per_bd == '12':
                        signo = "capricornio"
                    Thread(target=horoscopo, args=(data,signo)).start()
                    Thread(target=update_db_bot, args=(chat_id, "signo_enviada")).start()  # resposta do bot
                    pass

                # COVID
                elif ult_resp_bot == 'pergunta_covid' and nov_per_bd in ('1','2'):
                    if nov_per_bd == '1':
                        tipo_covid = 'casos'
                    if nov_per_bd == '2':
                        tipo_covid = "vacinas"

                    Thread(target=noticia_covid, args=(data,tipo_covid)).start()
                    Thread(target=update_db_bot, args=(chat_id, "noticia_covid_enviada")).start()  # resposta do bot
                    pass

                # ANDANDO PELO SUB MENU
                elif ult_resp_bot == 'sub_menu_estatistica' and nov_per_bd.lower().strip() in ('voltar'):
                    Thread(target=send_message,args=(data, '1. Estatísticas de CASOS da COVID-19 🖋 \n'
                                                           '2. Estatísticas de VACINAS da COVID-19 💉️')).start()
                    Thread(target=update_db_bot, args=(chat_id, "pergunta_covid")).start()  # resposta do bot
                    pass
                elif ult_resp_bot == 'sub_menu_estatistica' and nov_per_bd.lower().strip() in ('lista'):
                    Thread(target=lista, args=(data, "")).start() # Envia a lista de catálogo
                    Thread(target=update_db, args=(chat_id,nov_per_bd)).start() # pergunta do usuário
                    Thread(target=update_db_bot, args=(chat_id, "envio_lista")).start() # resposta do bot
                    pass

                # ANDANDO PELO SUB MENU [HOROSCOPO]
                elif ult_resp_bot == 'sub_menu_horoscopo' and nov_per_bd.lower().strip() in ('voltar'):
                    Thread(target=send_message, args=(data, 'Informe o SIGNO para receber as noticías')).start()
                    Thread(target=send_message, args=(data, '1.  ♒ Aquário\n'
                                                            '2.  ♓ Peixes\n'
                                                            '3.  ♈ Áries\n'
                                                            '4.  ♉ Touro\n'
                                                            '5.  ♊ Gêmeos\n'
                                                            '6.  ♋ Câncer\n'
                                                            '7.  ♌ Leão\n'
                                                            '8.  ♍ Virgem\n'
                                                            '9.  ♎ Libra\n'
                                                            '10. ♏ Escorpião\n'
                                                            '11. ♐ Sagitário\n'
                                                            '12. ♑ Capricórnio')).start()
                    Thread(target=update_db_bot, args=(chat_id, "pergunta_signo")).start()  # resposta do bot
                    pass
                elif ult_resp_bot == 'sub_menu_horoscopo' and nov_per_bd.lower().strip() in ('lista'):
                    Thread(target=lista, args=(data, "")).start()  # Envia a lista de catálogo
                    Thread(target=update_db, args=(chat_id, nov_per_bd)).start()  # pergunta do usuário
                    Thread(target=update_db_bot, args=(chat_id, "envio_lista")).start()  # resposta do bot
                    pass

                ########################################
                ########################################
                # novos sub perguntas
                ########################################
                ########################################

                elif ult_resp_bot == 'envio_lista':

                    # PREVISÃO DO TEMPO
                    if nov_per_bd == ('1'):
                        Thread(target=send_message,args=(data, 'Entendi... Agora me informe o ESTADO. (Ex.: RJ)')).start()
                        """Thread(target=send_message, args=(data,'1. Acre - AC\n'
                                                                '2. Alagoas - AL\n'
                                                                '3. Amapá - AP\n'
                                                                '4. Amazonas - AM\n'
                                                                '5. Bahia  - BA\n'
                                                                '6. Ceará - CE\n'
                                                                '7. Distrito Federal  - DF\n'
                                                                '8. Espírito Santo - ES\n'
                                                                '9. Goiás - GO\n'
                                                                '10. Maranhão - MA\n'
                                                                '11. Mato Grosso - MT\n'
                                                                '12. Mato Grosso do Sul - MS\n'
                                                                '13. Minas Gerais - MG\n'
                                                                '14. Pará - PA\n'
                                                                '15. Paraíba - PB\n'
                                                                '16. Paraná - PR\n'
                                                                '17. Pernambuco - PE\n'
                                                                '18. Piauí - PI\n'
                                                                '19. Rio de Janeiro - RJ\n'
                                                                '20. Rio Grande do Norte - RN\n'
                                                                '21. Rio Grande do Sul - RS\n'
                                                                '22. Rondônia - RO\n'
                                                                '23. Roraima - RR\n'
                                                                '24. Santa Catarina - SC\n'
                                                                '25. São Paulo - SP\n'
                                                                '26. Sergipe - SE\n'
                                                                '27. Tocantins - TO')).start()"""
                        Thread(target=update_db_bot, args=(chat_id, "pergunta_estado")).start()  # resposta do bot
                        config['lock'].release()
                        pass

                    # NOTICIAS
                    elif nov_per_bd == ('2'):
                        Thread(target=noticia, args=(data,"")).start()
                        Thread(target=update_db_bot, args=(chat_id, "noticia_enviada")).start()  # resposta do bot
                        pass

                    # IBOVESPA
                    elif nov_per_bd == ('3'):
                        Thread(target=ibovespa, args=(data,"")).start()
                        Thread(target=update_db_bot, args=(chat_id, "acao_enviada")).start()  # resposta do bot
                        pass

                    # NOTICIA ESPORTES
                    elif nov_per_bd == ('4'):
                        Thread(target=noticia_esportes, args=(data,"")).start()
                        Thread(target=update_db_bot, args=(chat_id, "noticia_esporte_enviada")).start()  # resposta do bot
                        pass

                    # COTAÇÃO MOEDAS
                    elif nov_per_bd == ('5'):
                        Thread(target=cotacao_moedas, args=(data,"")).start()
                        Thread(target=update_db_bot, args=(chat_id, "cotacao_moeda_enviada")).start()  # resposta do bot
                        pass

                    # SIGNO
                    elif nov_per_bd == ('6'):
                        Thread(target=send_message, args=(data, 'Hum... 🔮 Agora me informa o SIGNO')).start()
                        Thread(target=send_message, args=(data,'1.  ♒ Aquário\n'
                                                               '2.  ♓ Peixes\n'
                                                               '3.  ♈ Áries\n'
                                                               '4.  ♉ Touro\n'
                                                               '5.  ♊ Gêmeos\n'
                                                               '6.  ♋ Câncer\n'
                                                               '7.  ♌ Leão\n'
                                                               '8.  ♍ Virgem\n'
                                                               '9.  ♎ Libra\n'
                                                               '10. ♏ Escorpião\n'
                                                               '11. ♐ Sagitário\n'
                                                               '12. ♑ Capricórnio')).start()
                        Thread(target=update_db_bot, args=(chat_id, "pergunta_signo")).start()  # resposta do bot
                        pass

                    # COVID
                    elif nov_per_bd == ('7'):
                        Thread(target=send_message,args=(data, '1. Estatísticas de CASOS da COVID-19 🖋 \n'
                                                               '2. Estatísticas de VACINAS da COVID-19 💉️')).start()
                        Thread(target=update_db_bot, args=(chat_id, "pergunta_covid")).start()  # resposta do bot
                        pass

                    # PAGAMENTO DY
                    elif nov_per_bd == ('8'):
                        Thread(target=send_message,args=(data, '📢 Vou te enviar os PROVENTOS para esse mês, beleza?')).start()
                        Thread(target=pagamento_dividendo, args=(data,"")).start()
                        Thread(target=update_db_bot, args=(chat_id, "aviso_dividendo_enviada")).start()  # resposta do bot
                        pass

                    ########################################
                    ########################################
                    # novas respostas
                    ########################################
                    ########################################

                    else:
                        Thread(target=send_message, args=(
                        data, '🤔 ' + nome + ', desculpa mas não consegui entender sua solicitação')).start()
                        Thread(target=send_message, args=(data,'Digite apenas o número que contem em nosso menu de informações abaixo...')).start()
                        Thread(target=lista, args=(data, "")).start()  # Envia a lista de catálogo

                # SE O USUPARIO NÃO ENVIAR NADA
                else:
                    Thread(target=send_message, args=(data,
                    'Poxa, desculpa não consegui entender sua solicitação... Vamos tentar de novo. Qual a notícia que você deseja receber nesse momento?')).start()
                    Thread(target=lista, args=(data, "")).start()  # Envia a lista de catálogo
                    Thread(target=update_db_bot, args=(chat_id, "envio_lista")).start()  # resposta do bot

        sleep(0.5)

"""# PREVISÃO DO TEMPO
elif ult_resp_bot == 'pergunta_estado' and nov_per_bd in ('1','2','3','4','5','6','7','8','9','10'
                                                        ,'11','12','13','14','15','16','17','18','19'
                                                        ,'20','21','22','23','24','25','26','27'):
    if nov_per_bd == '1':
        estado = 'AC'
    if nov_per_bd == '2':
        estado = 'AL'
    if nov_per_bd == '3':
        estado = 'AP'
    if nov_per_bd == '4':
        estado = 'AM'
    if nov_per_bd == '5':
        estado = 'BA'
    if nov_per_bd == '6':
        estado = 'CE'
    if nov_per_bd == '7':
        estado = 'DF'
    if nov_per_bd == '8':
        estado = 'ES'
    if nov_per_bd == '9':
        estado = 'GO'
    if nov_per_bd == '10':
        estado = 'MA'
    if nov_per_bd == '11':
        estado = 'MT'
    if nov_per_bd == '12':
        estado = 'MS'
    if nov_per_bd == '13':
        estado = 'MG'
    if nov_per_bd == '14':
        estado = 'PA'
    if nov_per_bd == '15':
        estado = 'PB'
    if nov_per_bd == '16':
        estado = 'PR'
    if nov_per_bd == '17':
        estado = 'PE'
    if nov_per_bd == '18':
        estado = 'PI'
    if nov_per_bd == '19':
        estado = 'RJ'
    if nov_per_bd == '20':
        estado = 'RN'
    if nov_per_bd == '21':
        estado = 'RS'
    if nov_per_bd == '22':
        estado = 'RO'
    if nov_per_bd == '23':
        estado = 'RR'
    if nov_per_bd == '24':
        estado = 'SC'
    if nov_per_bd == '25':
        estado = 'SP'
    if nov_per_bd == '26':
        estado = 'SE'
    if nov_per_bd == '27':
        estado = 'TO'
    estado = nov_per_bd
    Thread(target=previsao, args=(data,estado, "")).start()
    Thread(target=update_db_bot, args=(chat_id, "previsao_enviada")).start()  # resposta do bot
    pass"""

