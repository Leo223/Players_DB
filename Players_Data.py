from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import requests
import html5lib
from bs4 import BeautifulSoup as bs

import os
from pprint import pprint as pp

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

        ### Atributos y variables
        self.equipos={}


    def get_equipos(self):

        ## Accedemos a la pagina de la LFP y obtenemos los equipos con sus correspondientes
        ## links para acceder a cada una de las plantillas
        self.tabla_teams = self.html.find_all('div', attrs={'id':'equipos'})[0].find_all('div')

        for elem in self.tabla_teams:
            for team in elem:
                self.equipos[team.text] = {'link': team.get('href'),'Jugadores':{}}




    def exe(self):
        self.get_equipos()

        for team in self.equipos:
            self.enlace = self.equipos.get(team).get('link')
            self.html = self.Parseo_web(self.enlace)
            ### Accedemos a las cajas ('box') de los jugadores.
            self._box = self.html.find_all('div',attrs={'id':'plantilla'})[0].find_all('a',attrs={'class':'box-jugador'})

            for jug in self._box:
                ###### Parseamos la pagina del jugador
                self.jug_enlace = jug.get('href')
                self.html = self.Parseo_web(self.jug_enlace)
                self.jug_perfil = self.html.find_all('div',attrs={'id':'datos-perfil'})[0].find_all('div')

                # obtenemos los datos generales del jugador
                self.Datos_jugador = {}
                for param in self.jug_perfil:
                    self.Datos_jugador[param.get('id')] = param.text

                self.instagram = self.html.find_all('div',attrs={'class':'dato'})[4].find_all('a')[0].get('href')
                self.twitter = self.html.find_all('div', attrs={'class': 'dato'})[5].find_all('a')[0].get('href')

                self.Datos_jugador['instagram'] = self.instagram
                self.Datos_jugador['twitter'] = self.twitter
                self.equipos[team]['Jugadores'][self.Datos_jugador.get('nombre')] = {'Info_general':self.Datos_jugador}

                # estadisticas del jugador

                self.Estadisticas_jugador={}

                self._est = self.html.find_all('section',attrs={'id':'box-estadisticas-jugador'})[0].find_all('div')

                for tabla in self._est:

                    if len(tabla.find_all('table')) == 0: continue

                    self.table_data = tabla.find_all('table')[0].find_all('tr')

                    self.definicion1 = [param.text.strip() for param in self.table_data]


                    pp(self.table_data)
                    pp(self.definicion1)

                    break


                # pp(self._est)




                ######




                # pp(self.equipos)

                break






            break






        # print (self.equipos)









if __name__ == "__main__":

    html = Plantillas().exe()
    # print (html)

