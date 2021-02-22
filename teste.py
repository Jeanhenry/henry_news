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


url = get('https://news.google.com/covid19/map?hl=pt-BR&gl=BR&ceid=BR%3Apt-419&mid=%2Fm%2F015fr', verify=False)
html = bs(url.text, 'html.parser')
lista = html.find_all('tr', class_='sgXwHf wdLSAe ROuVee')
titulo = html.find_all('th')
dados = html.find_all('td')
pais = html.find_all('div', class_='TWa0lb')

print(pais[0].text)
print(titulo[1].text + " | " + dados[0].text)
print(titulo[2].text + " | " + dados[1].text)
print(titulo[3].text + " | " + dados[3].text)
print(titulo[4].text + " | " + dados[4].text)

for x in len(pais):
    print(pais[x-5].text)
    print(titulo[1].text + " | " + dados[x].text)
    print(titulo[2].text + " | " + dados[x+1].text)
    print(titulo[3].text + " | " + dados[x+2].text)
    print(titulo[4].text + " | " + dados[x+3].text)
    print('#######################################')
exit()

x = 0
while x < len(pais):
    print(pais[x].text)
    print(titulo[x].text)
    print(dados[x].text)
    print('----')
    x = x + 1
exit()

print(lista1[0].text)
print(lista1[1].text)
print(lista1[2].text)
print(lista1[3].text)
print(lista1[4].text)
print(lista1[5].text)
exit()


"""url = get('http://www.lancamentosdanetflix.com/', verify=False)
html = bs(url.text, 'html.parser')
lista = html.find_all('div', class_='widget-content')
link_list = html.find_all('a')
link_list1 = html.find_all('img')

x = 1
msg_final = '+'
while x < len(link_list1):
    inf = str(link_list1[x])
    texto = inf.replace("<img alt=", " ")
    i = texto.index('class="post-thumb"') + 1
    msg_final = msg_final + "\n" + str(x) + ". " + texto[2:i - 3]
    x = x + 1
print(msg_final.replace("+",""))
exit()

for box in link_list:
    if box.text in ('Filmes', 'Séries', 'BloggerTemplates', 'Templates Top Best', 'Documentários', '\n'):
        pass
    else:
        print(box.text)
exit()
"""

"""titulo = box.find('img')
if titulo != None:
print(titulo)
exit()"""

"""for link in link_list:
    #if 'post-image-link' in link.attrs:

    print(link)
exit()

for link in link_list:
    if link.text.replace("\n\n", ""):
        print(link.text)

exit()

for link in link_list:
    if 'href' in link.attrs:
        link_1 = str(link.attrs['href'])
        print(link_1)


exit()"""

"""url = get('https://www.uol.com.br/universa/horoscopo/aries/horoscopo-do-dia/', verify=False)
html = bs(url.text, 'html.parser')
lista = html.find_all('div', class_='col-xs-8 col-sm-21 col-md-21')

x = 0
for box in lista:
    x = html.find_all('p')
    print(x[2].text)
    print(x[5].text)
exit()

print(texto)
exit()

signo = html.find_all('span', class_='sign-name')
data = html.find_all('span', class_='sign-date')
texto = html.find_all('h2')

print("♈" + signo[0].text + " | " + data[0].text)
"https://www.uol.com.br/universa/horoscopo/aries/horoscopo-do-dia/"
print(texto[0].text)
exit()


x = 0
for box in lista:
    x = html.find_all('span', class_='sign-date')
    print(x1)
exit()"""

url = get('https://www.meusdividendos.com/agenda-dividendos/2020/', verify=False)
html = bs(url.text, 'html.parser')
#lista = html.find_all('div', class_='box box-widget')
lista = html.find_all('a', class_='btn btn-xs btn-info')
#link_list = html.find_all('a')

x = 0
while x < len(lista):
    x = html.find_all('td')
    print(x[0].text + " | " + "Dia: " + x[1].text)
    x = x + 1

exit()

x = 0
while x < len(lista):
    print(lista[x].text)
    #if lista[x].text != "":
    #    print("Ação: " + lista[x].text.replace("| ", " | R$ "))
    x = x + 1
exit()

x = 0
for box in lista:
    #x = html.find_all('<span>')
    x1 = html.find_all('<span>')
    print(x1)
exit()

for link in link_list:
    #if 'span' in link.attrs:
    #link_1 = str(link.attrs['span'])
    print(link_1[0][0].text)
exit()

'odd'

print(lista)
exit()