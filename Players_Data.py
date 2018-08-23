from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import requests
import html5lib
from bs4 import BeautifulSoup as bs

import os

import time

# Paginas a investigar
#  https://www.laliga.es/
#  https://es.besoccer.com/
#  https://www.fifaindex.com/es/players/top/


class Conexion_by_browser(object):

    def __init__(self):
        self.ruta = os.getcwd()
        self.rutaDrivers = self.ruta + '/Drivers/geckodriver'
        self.rutaDrivers = self.ruta + '/Drivers/chromedriver'
        self.browser = webdriver
        self.Chrome()

    def Firefox(self):
        self.browser = self.browser.Firefox(executable_path=self.rutaDrivers)
        return self.browser

    def Chrome(self):
        print('Estableciendo conexion y abriendo el navegador... \n')
        self.options = self.browser.ChromeOptions()
        self.options.add_argument("headless")
        self.browser = self.browser.Chrome(executable_path=self.rutaDrivers, chrome_options=self.options)
        return self.browser

    def Navegar_web(self,page):
        print ('Conectando con ....  -->   ' + page + '\n')
        self.browser.get(page)
        self.html = self.browser.page_source
        self.browser.close()

        return bs(self.html,"html.parser")


class Conexion_to_server(object):

    def __init__(self):
        print ('Estableciendo conexion con el servidor...\n')


    def Parseo_web(self,page):
        print('Conectando con ....  -->' + page +'\n')
        self.s = requests.Session()
        self.html = self.s.get(page).text
        self.s.close()

        return bs(self.html,"html.parser")




class Plantillas(Conexion_by_browser,Conexion_to_server):

    def __init__(self):
        self.url_plantillas = 'https://www.laliga.es/laliga-santander'
        ##### By Server
        self.html = self.Parseo_web(self.url_plantillas)
        ##### By Browser
        # Conexion_by_browser.__init__(self)
        # self.html = self.Navegar_web(self.url_plantillas)
        self.equipos={}


    def exe(self):

        # self.tabla_teams = self.html.find_all('div', attrs={'class':'columna laliga-santander','class':'nombre'})
        self.tabla_teams = self.html.find_all('div', attrs={'id':'equipos'})[0].find_all('div')

        for elem in self.tabla_teams:
            for team in elem:
                print (elem.find_all('a'))


        # print (self.tabla_teams)
        # print (len(self.tabla_teams))
        # print (self.tabla_teams[0])









if __name__ == "__main__":

    html = Plantillas().exe()
    # print (html)

