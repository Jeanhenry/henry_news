import json
import requests
from time import sleep
from threading import Thread, Lock
import sys
from pymongo import MongoClient
from bs4 import BeautifulSoup as bs
from requests import get
from datetime import datetime

global config
config = {'url': 'https://api.telegram.org/bot1610447655:AAHj4vqxYCxX0d236VWLMpZKH0MGiM9Oh0E/', 'lock': Lock()}
cluster = MongoClient("mongodb+srv://db_user:uOKmcSP1QSntVUTT@cluster0.uf6yd.mongodb.net/db_informa?retryWrites=true&w=majority")

# CRIA A BASE DE DADOS (quando em seguida inserir os dados)
db = cluster["bot"]
collection = db["db_informa"]

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

    msg = ('Esse é o nosso MENU de INFORMAÇÕES:\n\n'
            '1. Previsão do Tempo ☀️\n'
            '2. Últimas noticias do BRASIL 💬 \n'
            '3. Cotação da IBOVESPA 💰 \n'
            '4. Últimas notícias do BRASILEIRÃO ⚽ \n'
            '5. Outras cotações 💱'
           )
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
    Thread(target=send_message,args=(data, '👍 Qualquer momento você pode digitar lista para retornar ao nosso menu.')).start()

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
    Thread(target=send_message,
           args=(data, '👍 Qualquer momento você pode digitar lista para retornar ao nosso menu.')).start()
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
            Thread(target=send_message,args=(data, '👍 Qualquer momento você pode digitar lista para retornar ao nosso menu.')).start()
            config['lock'].release()

def noticia(data,msg):
    global config, str

    url = get('https://economia.uol.com.br/cotacoes/bolsas/acoes/bvsp-bovespa/bidi4-sa', verify=False)
    html = bs(url.text, 'html.parser')
    ps = html.find_all('h3', class_='thumb-title title-xsmall title-lg-small')
    msg = str('Noticías mais lida no momento ' + "\n\n") + \
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
    Thread(target=send_message,
           args=(data, '👍 Qualquer momento você pode digitar lista para retornar ao nosso menu.')).start()
    config['lock'].release()

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
    Thread(target=send_message,
           args=(data, '👍 Qualquer momento você pode digitar lista para retornar ao nosso menu.')).start()
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
                Thread(target=send_message,args=(data, 'Digite lista para receber nosso MENU DE INFORMAÇÕES.')).start()

            #TRATAMENTO DE FOTO
            elif 'photo' in data['message']:
                Thread(target=send_message, args=(data, nome + ', desculpa mas não consigo conversar por imagens, apenas texto 😊 ')).start()
                Thread(target=send_message,args=(data, 'Digite lista para receber nosso MENU DE INFORMAÇÕES.')).start()

            else:
                chat_id = data['message']['from']['id'] #Id do usuario
                perg_usu = data['message']['text'].lower().strip() #Pergunta do usuario

                #######################################################################################################
                #######################################################################################################
                # Verifica se já existe o id no banco
                result = collection.find_one({"chat_id": chat_id})
                if result is None:
                    # INSERT NO BANCO
                    Thread(target=insert_db,args=(chat_id, perg_usu)).start()
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

                if nov_per_bd in ('oi','ola','olá','/start'):
                    resp_bot = "🤙 Olá " + nome + ", tudo bem? Sou Assistente Virtual do Henry \n\n" \
                               "Digite lista para receber nosso MENU DE INFORMAÇÕES."
                    Thread(target=send_message, args=(data, resp_bot)).start()
                    Thread(target=update_db_bot, args=(chat_id, "olá")).start()
                    pass
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
                # novos sub perguntas

                elif ult_resp_bot == 'envio_lista':

                    # PREVISÃO DO TEMPO
                    if nov_per_bd == ('1'):
                        Thread(target=send_message,args=(data, 'Informe o estado que deseja receber a PREVISÃO DO TEMPO para HOJE. (Ex.:RJ)')).start()
                        Thread(target=update_db_bot, args=(chat_id, "pergunta_estado")).start()  # resposta do bot
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
                    # novos



                    else:
                        Thread(target=send_message, args=(
                        data, nome + ', desculpa mas não consigo entender sua solicitação')).start()
                        Thread(target=send_message, args=(data,'Digite apenas o número que contem em nosso menu')).start()
                        Thread(target=lista, args=(data, "")).start()  # Envia a lista de catálogo
                else:
                    Thread(target=send_message, args=(data,
                    '😁 Oi tudo bem? \n\n' + 'Digite lista para receber nosso MENU DE INFORMAÇÕES.')).start()

        sleep(0.5)