from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import requests
import html5lib
from bs4 import BeautifulSoup as bs

import os
from pprint import pprint as pp

from collections import OrderedDict as OrdDict
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
        Conexion_by_browser.__init__(self)
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
                self.jug_enlace = 'https://www.laliga.es/jugador/messi'
                # self.html = self.Parseo_web(self.jug_enlace)
                self.html = self.Navegar_web(self.jug_enlace)
                self.jug_perfil = self.html.find_all('div',attrs={'id':'datos-perfil'})[0].find_all('div')

                # obtenemos los datos generales del jugador
                self.Datos_jugador = {}
                for param in self.jug_perfil:
                    self.Datos_jugador[param.get('id')] = param.text

                self.informacion_jug = self.html.find_all('div',attrs={'class':'box-dato'})

                for info in self.informacion_jug[:-1]:
                    if not info.find_all('div', attrs={'class','nombre'}):
                        self._dato = info.find_all('h2', attrs={'class','nombre'})[0].text
                    else:
                        self._dato = info.find_all('div', attrs={'class', 'nombre'})[0].text
                    self._valor = info.find_all('div', attrs={'class','dato'})[0].text

                    self.Datos_jugador[self._dato] = self._valor

                # pp(self.Datos_jugador)

                self.equipos[team]['Jugadores'][self.Datos_jugador.get('nombre')] = {'Info_general': self.Datos_jugador}

                # Estadisticas del jugador

                self.Estadisticas_jugador={}

                # sacamos las cabeceras de las tablas
                self._box_est = self.html.find_all('section',attrs={'id':'box-estadisticas-jugador'})[0]
                self._cabeceras = self._box_est.find_all('nav',attrs={'class':'cabecera-seccion-2 submenu'})[0].find_all('ul')
                self._cabeceras_url = [cab.get('href') for cab in self._cabeceras[0].find_all('a')]
                self._cabeceras_text = [cab.text.strip() for cab in self._cabeceras[0].find_all('a')]

                #
                # pp(self._cabeceras_text)

                # for cab_text,cab_url in zip(self._cabeceras_text,self._cabeceras_url):
                #     self.html = self.Parseo_web(cab_url)
                #     self._box_est = self.html.find_all('section', attrs={'id': 'box-estadisticas-jugador'})[0]


                self._tipo_tabla = ['General', 'Por_Campo', 'Por_Resultado']
                self._tablas = self._box_est.find_all('table')
                # pp(len(self._tablas))

                for tabla,tipo in zip(self._tablas,self._tipo_tabla):
                    # pp(tabla)
                    self._params_init = tabla.find_all('tr')
                    # self._params = [row for row in self._params_init if row.get('class')[0].find('mostrar_movil') == -1]

                    self._params=[]
                    for row in self._params_init:
                        if not row.get('class'):
                            self._params.append(row)
                            continue
                        if row.get('class')[0].find('mostrar_movil') == -1:
                            self._params.append(row)


                    # self._values = tabla.find_all('td')

                    pp(self._params)

                    # self._dic_data = OrdDict()
                    # for param,value in zip(self._params,self._values):
                    #     self._dic_data[param.get('title')] = value.text

                    # pp(self.Datos_jugador)
                    # pp(self._dic_data)

                    # pp(self._dic_data.get('Minutos jugados'))


                    break




                ######




                # pp(self.equipos)

                break






            break






        # print (self.equipos)









if __name__ == "__main__":

    html = Plantillas().exe()
    # print (html)

