import schedule
import subprocess
import os
import time

def encerrar_executavel():
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    #subprocess.call(["taskkill", "/IM", "Bot_informacao_teste.exe", "/T", "/F"], startupinfo=si)
    subprocess.call(["taskkill", "/IM", "Bot_informacao.exe", "/T", "/F"], startupinfo=si)

def abrir_executavel():
    #caminho = "C:\\Users\jean.carlo.da.henry\Desktop\\bot\\teste\dist\Bot_informacao_teste.exe"
    caminho = "C:\\Users\Administrator\Desktop\Chatbots\henry_informa\dist\Bot_informacao.exe"
    os.startfile(caminho)

schedule.every(30).seconds.do(encerrar_executavel)
schedule.every(30).seconds.do(abrir_executavel)

while 1:
    schedule.run_pending()




