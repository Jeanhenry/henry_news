import requests
import time
import json
import os

from threading import Thread, Lock
from pymongo import MongoClient
from requests import get
from bs4 import BeautifulSoup as bs
from datetime import datetime

class TelegramBot:
    def __init__(self):
        global collection
        token = '1562077602:AAG3RAEvg2jTyHit-qkK5uvYuk1WxqpaxDE' # TESTE
        #token = '1610447655:AAFrGZnoK-p5SiMmxV1c26ssjP6uGC23gCQ' # ORIGINAL
        self.url_base = f'https://api.telegram.org/bot{token}/'

        cluster = MongoClient(
            "mongodb+srv://db_user:uOKmcSP1QSntVUTT@cluster0.uf6yd.mongodb.net/db_informa?retryWrites=true&w=majority")

        # CRIA A BASE DE DADOS (quando em seguida inserir os dados)
        db = cluster["bot"]
        #collection = db["db_informa"] # ORIGINAL
        collection = db["db_informa_teste"]  # TESTE

    def Iniciar(self):
        global collection, reenviar_lista, retorno, retorno_duplo, reenviar_lista

        update_id = None
        while True:
            atualizacao = self.obter_novas_mensagens(update_id)
            dados = atualizacao["result"]

            if dados:
                for dado in dados:
                    update_id = dado['update_id']
                    chat_id = dado["message"]["from"]["id"]
                    nome = dado['message']['from']['first_name']  # NOME DO USUÁRIO

                    """# QUANTIDADE DE MSG DO USUÁRIO
                    id_usuario1 = dado["message"]["from"]["id"]
                    date1 = dado["message"]["date"]
                    print(id_usuario1)
                    print(date1)
                    if id_usuario1 == dado["message"]["from"]["id"] and date1 == dado["message"]["date"]:
                        pass
                    else:
                        print("VAMOS ENVIAR")
                    #eh_primeira_mensagem = int(dado["message"]["message_id"]) == 1"""

                    # TRATAR AUDIO/PHOTO/DOCUMENTOS
                    if 'voice' in dado['message']:
                        nov_per_bd = None
                        ult_perg = None
                        ult_resp_bot = None
                        reenviar_lista = True
                        resposta = (nome + ', desculpa por enquanto eu só consigo coversar por texto 😊 \n'
                                      'Vou te reenviar nosso MENU de INFORMAÇÃO 👇')
                        self.responder(chat_id, resposta)
                    elif 'photo' in dado['message']:
                        print("SIM")
                        """reenviar_lista = True
                        return self.resposta_errada3(nome)"""
                    elif 'document' in dado['message']:
                        print("SIM")
                        """reenviar_lista = True
                        return self.resposta_errada3(nome)"""
                    else:
                        nov_per_bd = str(dado["message"]["text"]) #PERGUNTA DO USUÁRIO

                        # VERIFICA SE O USUÁRIO JÁ ESTA NO mongoDB
                        result = collection.find_one({"chat_id": chat_id})
                        if result is None:
                            self.insert_mongoDB(chat_id,nov_per_bd,resp_usu=None) #INSERT NO BANCO
                        else:
                            nov_per_bd = dado['message']['text'].lower().strip() #UPDATE NO BANCO
                            self.update_db(chat_id,nov_per_bd)

                        ult_perg = collection.find_one({"chat_id": chat_id})['ultima_perg']# ÚLTIMA PERGUNTA DO USUÁRIO NO BANCO
                        try:
                            ult_resp_bot = result['ultima_resp'] # ULTIMA RESPOSTA DO BOT
                        except:
                            ult_resp_bot = None
                        #nov_per_bd = data['message']['text'].lower().strip()

                    resposta = self.criar_resposta(chat_id,nome,nov_per_bd,ult_perg,ult_resp_bot)
                    self.responder(chat_id,resposta)

                    # QUANDO O BO RESPONDER DEVE ENVIAR ESSA OUTRA MSG
                    if retorno==True:
                        self.responder(chat_id,resposta='↩ Digite LISTA para retornar ao MENU PRINCIPAL')
                    elif retorno_simples ==True:
                        self.responder(chat_id,resposta='⤴ Digite VOLTAR para retornar ao MENU ANTERIOR \n' + '↩ Digite LISTA para retornar ao MENU PRINCIPAL')

                    # SE FOR NECESSÁRIO REENVIAR A LISTA DE INFORMAÇÃO
                    if reenviar_lista == True:
                        resposta = self.lista()
                        self.responder(chat_id, resposta)
                        self.update_db_bot(chat_id, "envio_lista")  # resposta do bot

    # OBTER MENSAGEM
    def obter_novas_mensagens(self, update_id):
        link_requisicao = f'{self.url_base}getUpdates?timeout=100'
        if update_id:
            link_requisicao = f'{link_requisicao}&offset={update_id + 1}'
        resultado = requests.get(link_requisicao, verify=False)
        return json.loads(resultado.content)

    # CRIAR UMA RESPOSTA
    def criar_resposta(self,chat_id,nome,nov_per_bd,ult_perg,ult_resp_bot):
        global retorno, retorno_simples, reenviar_lista

        retorno = False
        retorno_simples = False
        reenviar_lista = False

        if ult_resp_bot == None:
            ult_resp_bot = ult_resp_bot
        else:
            ult_resp_bot = ult_resp_bot.lower()

        ########################################################################################
        ########################################################################################
        # INICIO DO ChatBot
        if nov_per_bd == None:
            self.update_db(chat_id, nov_per_bd)  # pergunta do usuário
            self.update_db_bot(chat_id, resp_bot="envio_lista")  # resposta do bot
            return self.lista()
        elif nov_per_bd.lower() in ('oi', 'ola', 'olá', '/start'):
            resp_bot = "🤙 Olá " + nome + ", tudo bem? Sou Assistente Virtual do Henry. \n" \
                       "Digite LISTA para receber nosso menu de informações."
            self.update_db_bot(chat_id, resp_bot)  # RESPOSTA DO BOT
            return resp_bot
        # BOT ENVIA A LISTA DE MENU DE INFORMAÇÕES
        elif nov_per_bd.lower() == 'lista' or nov_per_bd == None:
            self.update_db(chat_id, nov_per_bd)  # pergunta do usuário
            self.update_db_bot(chat_id, resp_bot="envio_lista")  # resposta do bot
            return self.lista()
        # QUANDO O USUÁRIO RESPOSNDE QUAL ESTADO [PREVISÃO]
        elif ult_resp_bot == 'pergunta_estado' and nov_per_bd.upper() in ('AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'ES'
                                                                          , 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB'
                                                                          , 'PR', 'PE', 'PI', 'RJ','RN', 'RS', 'RO'
                                                                          , 'RR', 'SC', 'SP', 'SE', 'TO', 'DF'):
            estado = nov_per_bd
            self.update_db_bot(chat_id, resp_bot="previsao_enviada")  # RESPOSTA DO BOT
            retorno = True
            return self.previsao(estado)
        # QUANDO O USUÁRIO RESPONDE COM O SIGNO [HOROSCOPO]
        elif ult_resp_bot == 'pergunta_signo' and nov_per_bd in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'):
            if nov_per_bd == '1':
                signo = 'aquario'
            elif nov_per_bd == '2':
                signo = "peixes"
            elif nov_per_bd == '3':
                signo = "aries"
            elif nov_per_bd == '4':
                signo = "touro"
            elif nov_per_bd == '5':
                signo = "gemeos"
            elif nov_per_bd == '6':
                signo = "cancer"
            elif nov_per_bd == '7':
                signo = "leao"
            elif nov_per_bd == '8':
                signo = "virgem"
            elif nov_per_bd == '9':
                signo = "libra"
            elif nov_per_bd == '10':
                signo = "escorpiao"
            elif nov_per_bd == '11':
                signo = "sagitario"
            elif nov_per_bd == '12':
                signo = "capricornio"

            self.update_db_bot(chat_id, resp_bot="signo_enviada")  # RESPOSTA DO BOT
            retorno_simples = True # ENVIAR OPÇÃO DE VOLTAR e LISTA
            return self.horoscopo(chat_id, signo)
        # QUANDO O USUÁRIO RESPONDE COM O TIPO [COVID]
        elif ult_resp_bot == 'pergunta_covid' and nov_per_bd in ('1', '2'):
            if nov_per_bd == '1':
                tipo_covid = 'casos'
            if nov_per_bd == '2':
                tipo_covid = "vacinas"

            self.update_db_bot(chat_id, resp_bot="noticia_covid_enviada")  # RESPOSTA DO BOT
            retorno_simples = True  # ENVIAR OPÇÃO DE VOLTAR e LISTA
            return self.noticia_covid(chat_id, tipo_covid)

        ########################################################################################
        ########################################################################################
        # QUANDO O BOT ENVIA A LISTA DE INFORMAÇÃO
        elif ult_resp_bot == 'envio_lista':
            # PREVISÃO DO TEMPO
            if nov_per_bd == ('1'):
                self.update_db_bot(chat_id, resp_bot="pergunta_estado")  # RESPOSTA DO BOT
                resp_bot = "Entendi... Agora me informe o ESTADO. (Ex.: RJ)"
                return resp_bot
            # NOTICIAS + LIDAS
            elif nov_per_bd == ('2'):
                self.update_db_bot(chat_id, resp_bot="noticia_enviada")  # RESPOSTA DO BOT
                retorno = True
                return self.noticia()
            # IBOVESPA
            elif nov_per_bd == ('3'):
                self.update_db_bot(chat_id, resp_bot="acao_enviada")  # RESPOSTA DO BOT
                retorno = True
                return self.ibovespa()
            # NOTICIA ESPORTES
            elif nov_per_bd == ('4'):
                self.update_db_bot(chat_id, resp_bot="noticia_esporte_enviada")  # RESPOSTA DO BOT
                retorno = True
                return self.noticia_esportes()
            # COTAÇÃO MOEDAS
            elif nov_per_bd == ('5'):
                self.update_db_bot(chat_id, resp_bot="cotacao_moeda_enviada")  # RESPOSTA DO BOT
                retorno = True
                return self.cotacao_moedas()
            # SIGNO
            elif nov_per_bd == ('6'):
                self.update_db_bot(chat_id, resp_bot="pergunta_signo")  # RESPOSTA DO BOT
                link_requisicao = f'{self.url_base}sendMessage?chat_id={chat_id}&text={"Hum... 🔮 Agora me informa o SIGNO"}'
                requests.get(link_requisicao, verify=False)
                resp_bot = '1.  ♒ Aquário\n' +\
                            '2.  ♓ Peixes\n' +\
                            '3.  ♈ Áries\n' +\
                            '4.  ♉ Touro\n' +\
                            '5.  ♊ Gêmeos\n' +\
                            '6.  ♋ Câncer\n' +\
                            '7.  ♌ Leão\n' +\
                            '8.  ♍ Virgem\n' +\
                            '9.  ♎ Libra\n' +\
                            '10. ♏ Escorpião\n' +\
                            '11. ♐ Sagitário\n' +\
                            '12. ♑ Capricórnio'
                return resp_bot
            # COVID
            elif nov_per_bd == ('7'):
                self.update_db_bot(chat_id, resp_bot="pergunta_covid")  # RESPOSTA DO BOT
                resp_bot = '1. Estatísticas de CASOS da COVID-19 🖋 \n' + \
                           '2. Estatísticas de VACINAS da COVID-19 💉️'
                return resp_bot
            # PAGAMENTO DY
            elif nov_per_bd == ('8'):
                self.update_db_bot(chat_id, resp_bot="aviso_dividendo_enviada")  # RESPOSTA DO BOT
                link_requisicao = f'{self.url_base}sendMessage?chat_id={chat_id}&text={"📢 Vou te enviar os PROVENTOS para esse mês, beleza?"}'
                requests.get(link_requisicao, verify=False)
                retorno = True
                return self.pagamento_dividendo()
            # QUANDO O BOT NÃO RECONHECE A SOLICITAÇÃO
            else:
                reenviar_lista = True
                return self.resposta_errada2(nome)

        # SUB MENU [HOROSCOPO]
        elif ult_resp_bot == 'sub_menu_horoscopo' and nov_per_bd.lower().strip() in ('voltar'):
            self.update_db_bot(chat_id, resp_bot="pergunta_signo")  # RESPOSTA DO BOT
            resp_bot = '1.  ♒ Aquário\n' + \
                       '2.  ♓ Peixes\n' + \
                        '3.  ♈ Áries\n' + \
                        '4.  ♉ Touro\n' + \
                        '5.  ♊ Gêmeos\n' + \
                        '6.  ♋ Câncer\n' + \
                        '7.  ♌ Leão\n' + \
                        '8.  ♍ Virgem\n' + \
                        '9.  ♎ Libra\n' + \
                        '10. ♏ Escorpião\n' + \
                        '11. ♐ Sagitário\n' + \
                        '12. ♑ Capricórnio'
            return resp_bot
        elif ult_resp_bot == 'sub_menu_horoscopo' and nov_per_bd.lower().strip() in ('lista'):
            self.update_db(chat_id, nov_per_bd)  # pergunta do usuário
            self.update_db_bot(chat_id, resp_bot="envio_lista")  # resposta do bot
            return self.lista()
        # SUB MENU [COVID]
        elif ult_resp_bot == 'sub_menu_estatistica' and nov_per_bd.lower().strip() in ('voltar'):
            self.update_db_bot(chat_id, resp_bot="pergunta_covid")  # RESPOSTA DO BOT
            resp_bot = '1. Estatísticas de CASOS da COVID-19 🖋 \n' +\
                       '2. Estatísticas de VACINAS da COVID-19 💉️'
            return resp_bot
        elif ult_resp_bot == 'sub_menu_estatistica' and nov_per_bd.lower().strip() in ('lista'):
            self.update_db(chat_id, nov_per_bd)  # pergunta do usuário
            self.update_db_bot(chat_id, resp_bot="envio_lista")  # resposta do bot
            return self.lista()
        #QUANDO O USUÁRIO NÃO RESPONDE NADA AOS CRITÉRIOS ACIMA
        else:
            reenviar_lista = True
            return self.resposta_errada()

    # RESPONDER
    def responder(self, chat_id,resposta):
        link_requisicao = f'{self.url_base}sendMessage?chat_id={chat_id}&text={resposta}'
        requests.get(link_requisicao, verify=False)

    # INSERT NO mongoDB
    def insert_mongoDB(self,chat_id,perg_usu,resp_usu):
        collection.insert_one({"chat_id": chat_id, "ultima_perg": perg_usu, "ultima_resp": resp_usu})

    # UPDATE NO mongoDB
    def update_db(self,chat_id,nov_per_bd):
        collection.update_one({"chat_id": chat_id}, {"$set": {"ultima_perg": nov_per_bd}})

    # UPDATE no mongoDB pela resposta do Bot
    def update_db_bot(self,chat_id, resp_bot):
        collection.update_one({"chat_id": chat_id}, {"$set": {"ultima_resp": resp_bot}})


    # ENVIA A LISTA DE INFORMAÇÕES
    def lista(self):
        lista = ('📚 MENU de INFORMAÇÕES\n\n'
               '1. Previsão do Tempo ☀️\n'
               '2. Últimas noticias do BRASIL 💬 \n'
               '3. Cotação da IBOVESPA 💰 \n'
               '4. Últimas notícias do BRASILEIRÃO ⚽ \n'
               '5. Outras cotações 💱 \n'
               '6. Horóscopo do Dia ♎ \n'
               '7. Estatística COVID-19 🦠 \n'
               '8. Lista de DIVIDENDOS - IBOVESPA 🤑')
        return lista

    # QUANDO O BOT RECEBER UMA RESPOSTA ALEOTÓRIA
    def resposta_errada(self):
        msg = ('☹️, desculpa não consegui entender sua solicitação... Vamos tentar de novo. \n'
                'Qual a notícia que você deseja receber nesse momento?')
        return msg

    # QUANDO O BOT RECEBER UMA RESPOSTA ALEOTÓRIA
    def resposta_errada2(self, nome):
        msg = ('🤔 ' + nome + ', desculpa não consegui entender sua solicitação.... \n' +
               'Digite apenas o número que contem em nosso menu de informações abaixo...')
        return msg

    # QUANDO O BOT RECEBER AUDIO,VIDEO ou DOCUMENTO
    def resposta_errada3(self, nome):
        msg = (nome + ', desculpa por enquanto eu só consigo coversar por texto 😊 . \n\n'
                'Vou te reenviar nosso MENU de INFORMAÇÃO')
        return msg

    ########################################################################################
    # RESPOSTAS
    ########################################################################################

    def previsao(self, estado):
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
                      + "🌡️ " + str(" Máx: " + max) + " | " + str("Min: " + min) + "\n" \
                      + "☔ " + str(chuva) + "\n\n" \
                      + "Para saber mais, acesse o link abaixo 👇 " + '\n'\
                      + "https://www.climatempo.com.br/brasil"
        return msg

    def noticia(self):
        url = get('https://economia.uol.com.br/cotacoes/bolsas/acoes/bvsp-bovespa/bidi4-sa', verify=False)
        html = bs(url.text, 'html.parser')
        ps = html.find_all('h3', class_='thumb-title title-xsmall title-lg-small')
        msg = str('Noticías mais lida no site da UOL ' + "\n\n") + \
              str('▪️' + ps[0].text + '\n') + \
              str('▪️' + ps[1].text + '\n') + \
              str('▪️' + ps[2].text + '\n') + \
              str('▪️' + ps[3].text + '\n') + \
              str('▪️' + ps[4].text + '\n') + \
              str('▪️' + ps[5].text + '\n') + \
              str('▪️' + ps[6].text + '\n') + \
              str('▪️' + ps[7].text + '\n') + \
              str('▪️' + ps[8].text + '\n') + \
              str('▪️' + ps[9].text + '\n') + \
              str('▪️' + ps[10].text + '\n\n') + \
              str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
              str("https://www.uol.com.br/")
        return msg

    def ibovespa(self):
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
                primeiro_alta = ('🥇' + acao_alta + " " + perc_acao_alta + " " + valor_acao_alta).replace(".SA", "")
            if x == 2:
                primeiro_baixa = ('🥇' + acao_alta + " " + perc_acao_alta + " " + valor_acao_alta).replace(".SA",
                                                                                                           "")
            if x == 3:
                primeiro_negociada = ('🥇' + acao_alta + " " + perc_acao_alta + " " + valor_acao_alta).replace(
                    ".SA", "")

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
                segunda_alta = ('🥈' + acao_baixa + " " + perc_acao_baixa + " " + valor_acao_baixa).replace(".SA",
                                                                                                            "")
            if x == 2:
                segunda_baixa = ('🥈' + acao_baixa + " " + perc_acao_baixa + " " + valor_acao_baixa).replace(".SA",
                                                                                                             "")
            if x == 3:
                segunda_negociada = ('🥈' + acao_baixa + " " + perc_acao_baixa + " " + valor_acao_baixa).replace(
                    ".SA", "")

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
                terceira_alta = (
                            '🥉' + acao_negociada + " " + perc_acao_negociada + " " + valor_acao_negociada).replace(
                    ".SA", "")
            if x == 2:
                terceira_baixa = (
                            '🥉' + acao_negociada + " " + perc_acao_negociada + " " + valor_acao_negociada).replace(
                    ".SA", "")
            if x == 3:
                terceira_negociada = (
                            '🥉' + acao_negociada + " " + perc_acao_negociada + " " + valor_acao_negociada).replace(
                    ".SA", "")

        msg = str('Valores atualizados em - ' + dia_hoje + "\n\n") + ibo[5].text + "\n\n" + str(
            "COTAÇÕES EM ALTA" + "\n") \
              + str(primeiro_alta) + "\n" \
              + str(segunda_alta) + "\n" \
              + str(terceira_alta) + "\n\n" \
              + str("COTAÇÕES EM BAIXAS" + "\n") \
              + str(primeiro_baixa) + "\n" \
              + str(segunda_baixa) + "\n" \
              + str(terceira_baixa) + "\n\n" \
              + str("COTAÇÕES MAIS NEGOCIADAS" + "\n") \
              + str(primeiro_negociada) + "\n" \
              + str(segunda_negociada) + "\n" \
              + str(terceira_negociada) + "\n\n" \
              + str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
              str("https://economia.uol.com.br/cotacoes/bolsas/")
        return  msg

    def noticia_esportes(self):
        url = get('https://www.uol.com.br/esporte/futebol/campeonatos/brasileirao/', verify=False)
        html = bs(url.text, 'html.parser')
        ps = html.find_all('h3', class_='thumb-title title-xsmall title-lg-small')
        msg = str('Últimas notícias do BRASILEIRÃO ⚽ ' + "\n\n") + \
              str('▪️' + ps[0].text + '\n') + \
              str('▪️' + ps[1].text + '\n') + \
              str('▪️' + ps[2].text + '\n') + \
              str('▪️' + ps[3].text + '\n') + \
              str('▪️' + ps[4].text + '\n') + \
              str('▪️' + ps[5].text + '\n') + \
              str('▪️' + ps[6].text + '\n') + \
              str('▪️' + ps[7].text + '\n') + \
              str('▪️' + ps[8].text + '\n\n') + \
              str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
              str("https://www.uol.com.br/esporte/futebol/campeonatos/brasileirao/")
        return msg

        #Thread(target=send_message,args=(data, '↩ Digite LISTA para retornar ao MENU PRINCIPAL')).start()

    def cotacao_moedas(self):
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
        return  msg

        #Thread(target=send_message, args=(data, '↩ Digite LISTA para retornar ao MENU PRINCIPAL')).start()

    def horoscopo(self,chat_id, signo):
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

        self.update_db_bot(chat_id, resp_bot="sub_menu_horoscopo")  # RESPOSTA DO BOT
        return msg

    def noticia_covid(self,chat_id, tipo_covid):

        if tipo_covid == "casos":
            url = get('https://news.google.com/covid19/map?hl=pt-BR&gl=BR&ceid=BR%3Apt-419&mid=%2Fm%2F015fr',
                      verify=False)
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

            msg_estado = 'TOP 3 Total de casos por ESTADOS DO BRASIL ⤵️\n\n'
            msg_final = str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
                        str("encurtador.com.br/eoDM7")
            msg = msg + msg0 + '\n' + msg_estado + msg1 + msg2 + msg3 + msg_final
        elif tipo_covid == "vacinas":
            url = get('https://news.google.com/covid19/map?hl=pt-BR&gl=BR&ceid=BR%3Apt-419&state=4', verify=False)
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
        self.update_db_bot(chat_id, resp_bot="sub_menu_estatistica")  # RESPOSTA DO BOT
        return msg

    def pagamento_dividendo(self):
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

                    if qtd_dividendos == 0:
                        str1 = "Meu amigo(a), dei uma pesquisada aqui, e para esse mês não vamos ter PROVENTOS...\n\n"
                    msg = str1 + str('Para saber mais, acesse o link abaixo 👇 ' + '\n') + \
                        str("https://statusinvest.com.br/acoes/proventos/ibovespa")

                    return msg

bot = TelegramBot()
bot.Iniciar()

"""if eh_primeira_mensagem == True or mensagem in ('menu', 'Menu'):
    return f'''Olá bem vindo a nossa lanchonete Digite o número do hamburguer gostaria de pedir:{os.linesep}1 - Queijo MAX{os.linesep}2 - Duplo Burguer Bacon{os.linesep}3 - Triple XXX'''
if mensagem == '1':
    return f'''Queijo MAX - R$20,00{os.linesep}Confirmar pedido?(s/n)
    '''
elif mensagem == '2':
    return f'''Duplo Burguer Bacon - R$25,00{os.linesep}Confirmar pedido?(s/n)
    '''
elif mensagem == '3':
    return f'''Triple XXX - R$30,00{os.linesep}Confirmar pedido?(s/n)'''

elif mensagem.lower() in ('s', 'sim'):
    return ''' Pedido Confirmado! '''
elif mensagem.lower() in ('n', 'não'):
    return ''' Pedido Confirmado! '''
else:
    return 'Gostaria de acessar o menu? Digite "menu"'"""