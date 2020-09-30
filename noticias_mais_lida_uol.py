# -*- coding:UTF-8 -*-

import requests
from bs4 import BeautifulSoup as bs
from requests import get
from time import gmtime,strftime
from datetime import datetime

class telegram:

    def __init__(self):
        token = '1319558756:AAEdfhZRcoxVea43DgaXec_ds0sDwI3sR84'  # Jean
        self.url_base = f'https://api.telegram.org/bot{token}/'

    def mais_lida(self):
        while True:
            now = datetime.now()
            hora_agora = now.strftime("%H:%M:%S")
            hora_de_rodar = hora_agora[0:8] == "06:15:00" or hora_agora[0:8] == "12:15:00" or hora_agora[0:8] == "18:15:00"
            if hora_de_rodar != False:
                bot.noticia(hora_agora)

    def noticia(self,hora_agora):
        global inf_chuva, inf_temp_min, inf_temp_max
        chat_id = "-423392877"  # Jean

        acao = 'bidi4'
        if acao.lower() == 'bidi4':
            ext = 'bidi4-sa'

        url = get('https://economia.uol.com.br/cotacoes/bolsas/acoes/bvsp-bovespa/' + ext)  # rio de janeiro
        html = bs(url.text, 'html.parser')

        #+ LIDAS
        mais_lida = html.find_all('div', class_='thumbnails-item grid col-xs-4 col-sm-6 small')
        ps = html.find_all('h3', class_='thumb-title title-xsmall title-lg-small')

        self.responder('AS NOTÍCIAS MAIS LIDAS AGORA NO UOL - ' + hora_agora + "\n\n"
                       + '.: ' + ps[0].text + '\n'
                       + '.: ' + ps[1].text + '\n'
                       + '.: ' + ps[2].text + '\n'
                       + '.: ' + ps[3].text + '\n'
                       + '.: ' + ps[4].text + '\n'
                       + '.: ' + ps[5].text + '\n'
                       + '.: ' + ps[6].text + '\n'
                       + '.: ' + ps[7].text + '\n'
                       + '.: ' + ps[8].text + '\n'
                       + '.: ' + ps[9].text + '\n'
                       + '.: ' + ps[10].text + '\n'
                       + '.: ' + ps[11].text + '\n\n'
                       + "🧾 Henry's trazendo as melhores informações do DIA, pra você! " + '\n'
                       + "🌎 https://www.uol.com.br/"
                       , chat_id)
        #breakpoint()

    def responder(self, resposta, chat_id):
        link_de_envio = f'{self.url_base}sendMessage?chat_id={chat_id}&text={resposta}'
        requests.get(link_de_envio)

bot = telegram()
bot.mais_lida()
