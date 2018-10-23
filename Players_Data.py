from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import requests
import html5lib
from bs4 import BeautifulSoup as bs

import os
import sys
import base64
from time import sleep
from pprint import pprint as pp

import json
import time
from PIL import Image
from keras.preprocessing import image
from dask.distributed import Client,LocalCluster
from dask.delayed import delayed
import dask.bag as db
import dask.dataframe as dd
import dask

# Paginas a investigar
#  https://www.laliga.es/
#  https://es.besoccer.com/
#  https://www.fifaindex.com


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
        # print('Estableciendo conexion y abriendo el navegador... \n')
        self.options = self.browser.ChromeOptions()
        self.options.add_argument("headless")
        self.browser = self.browser.Chrome(executable_path=self.rutaDrivers, chrome_options=self.options)
        self.browser.maximize_window()

        return self.browser

    def Navegar_web(self,page,format='html'):
        print ('Conectando con ....  -->   ' + page + '\n')
        self.browser.get(page)
        # self.browser.close()
        if format == 'html':
            self.html = self.browser.page_source
            return bs(self.html,"html.parser")
        elif format == 'web':
            return self.browser

    def close_browser(self):
        self.browser.close()

    def get_image_from_canvas(self,html,mapa,equipo):

        self.mapa = 'mapa-'+ mapa
        self.canvas = html.find_element_by_id(self.mapa).find_element_by_css_selector('canvas')
        # self.script = "return document.querySelector('.campo-mapa-calor canvas').toDataURL('image/png').substring(21);"
        self.script = "return arguments[0].toDataURL('image/png').substring(21);"
        self.canvas_base64 = html.execute_script(self.script, self.canvas)
        self.canvas_png = base64.b64decode(self.canvas_base64)

        # self.ruta_imagen = os.getcwd() + "/Mapa_de_calor/imagen_aux_"+ mapa +".png"
        self.ruta_imagen = os.getcwd() + "/Imagenes/imagen_"+ equipo +"_aux.png"
        self.imagen_aux = open(self.ruta_imagen, 'wb')
        self.imagen_aux.write(self.canvas_png)
        self.imagen_aux.close()

        self.im1 = Image.open(self.ruta_imagen)
        self.im1np = image.img_to_array(self.im1)
        self.im1.close()

        return self.im1np



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
        self.url_skills = 'https://www.fifaindex.com'
        ##### By Browser
        # Conexion_by_browser.__init__(self)

        if not os.path.isfile(os.getcwd()+ '/' + 'Equipos.json'):
            ##### By Server
            self.html = self.Parseo_web(self.url_plantillas)

            # self.html = self.Navegar_web(self.url_plantillas)
            self.get_equipos()
            self.All_teams = self.Import_json()



    def Export_json(self,data,nombre_file = 'json_export_DB.json'):

        self.equipos_json = json.dumps(data)
        self.ruta_export = os.getcwd()
        self.nombre_file = nombre_file.replace(' ','_')
        self.json_file = open(self.ruta_export + '/' + self.nombre_file,'w')
        json.dump(self.equipos_json,self.json_file,indent=4)
        self.json_file.close()

    def Import_json(self, nombre_file = 'Equipos.json'):
        self.ruta_import = os.getcwd()
        self.json_import = open(self.ruta_import + '/' + nombre_file,'r')
        self.data = json.load(self.json_import)
        return json.loads(self.data)

    def page_skills(self,Name_full,Name_short,team):
        self.nombre = Name_full.replace(' ','+')
        self.url_player = 'https://www.fifaindex.com/players/?name=' + self.nombre
        self.html = self.Parseo_web(self.url_player)
        self._pos_jug_table = self.html.find_all('table', attrs={'class': 'table table-striped table-players'})[0]
        self._pos_jug_table = self._pos_jug_table.find_all('tbody')

        self.NoResults = 'There are no results'
        if len(self._pos_jug_table) == 1 and self.NoResults in self._pos_jug_table[0].text:
            self.nombre = Name_short.replace(' ', '+')
            self.url_player = 'https://www.fifaindex.com/players/?name=' + self.nombre
            self.html = self.Parseo_web(self.url_player)
            self._pos_jug_table = self.html.find_all('table', attrs={'class': 'table table-striped table-players'})[0]
            self._pos_jug_table = self._pos_jug_table.find_all('tbody')

        if len(self._pos_jug_table)==1 and self.NoResults not in self._pos_jug_table[0].text:
            self._jug = self._pos_jug_table[0].find_all('tr')[0]
            self._url_player = self._jug.find_all('td', attrs={'data-title': 'Name'})[0]
            self.url_player = self._url_player.find_all('a')[0].get('href')
        else:
            for _jug in self._pos_jug_table[0].find_all('tr'):
                self._team =_jug.find_all('td',attrs={'data-title':'Team'})
                if len(self._team)==0: return False
                else: self._team = self._team[0]
                self.team = self._team.find_all('img')[0].get('title')
                if team == self.team:
                    self._url_player = _jug.find_all('td',attrs={'data-title':'Name'})[0]
                    self.url_player = self._url_player.find_all('a')[0].get('href')
                    # pp(self.url_player)
                    break


        self.html = self.Parseo_web(self.url_skills + self.url_player)

        return self.html

    def skills(self,html_jugador):

        self.html = html_jugador
        self.Generales = {}
        self.Fisicas = {}
        ## Tabla Principal
        self._tabla_gnral = self.html.find_all('div',attrs={'class':'col-lg-8'})[0]

        ## Datos Generarles
        self._av = self._tabla_gnral.find_all('h5',attrs={'class':'card-header'})[0].find_all('span')[1:]
        self._PrePos = self._tabla_gnral.find_all('div',attrs={'class':'card-body'})[0].find_all('p')[5].find_all('span')[1:]
        self._PrePos = [elem.text for elem in self._PrePos]
        self.Generales = {'Overall': self._av[0].text, 'Potential': self._av[1].text,'Prefered_Positions':self._PrePos}

        ## Datos Fisicos
        self._fis = self.html.find_all('div',attrs={'class':'row grid'})[0]
        self.skills_names = self._fis.find_all('h5')
        self.skills_values = self._fis.find_all('div',attrs={'class':'card-body'})

        for data,skill in zip(self.skills_values,self.skills_names):
            self.fisical_skill = skill.text
            self.Fisicas[self.fisical_skill] = {}
            for values in data.find_all('p'):
                self.subskill_name = values.text[:-3]
                self.subskill_value= values.find('span').text
                self.Fisicas[self.fisical_skill][self.subskill_name]=self.subskill_value
        return self.Generales,self.Fisicas

    def get_equipos(self):
        """Accedemos a la pagina de la LFP y obtenemos los equipos con sus correspondientes
          links para acceder a cada una de las plantillas"""
        self.equipos = {}
        self.tabla_teams = self.html.find_all('div', attrs={'id':'equipos'})[0].find_all('div')

        for elem in self.tabla_teams:
            for team in elem:
                """ Estadisticas del equipo """
                self.link = team.get('href')
                self.html_team = self.Parseo_web(self.link)
                self._graficos = self.html_team.find_all('div',attrs={'id':'zona-graficos'})[0].find_all('div',attrs={'class':'grafico'})
                self._iconos = self.html_team.find_all('div',attrs={'id':'zona-iconos'})[0].find_all('div',attrs={'class':'icono'})

                self.Stat_team = {}
                for graf in self._graficos:
                    self._gr = [i for i in graf.text.split('\n') if i]
                    self.Stat_team[self._gr[0]] = self._gr[1]

                for icon in enumerate(self._iconos):
                    self._ic = [i for i in icon[1].text.split('\n') if i][0]
                    self._ic = self._ic.split(':')
                    if len(self._ic) == 1:
                        if int(icon[0]) == len(self._iconos)-1:
                            self.Stat_team['Tarjetas_rojas'] = self._ic[0]
                        if int(icon[0]) == len(self._iconos)-2:
                            self.Stat_team['Tarjetas_amarillas'] = self._ic[0]
                        continue
                    self.Stat_team[self._ic[0]] = self._ic[1]


                self.equipos[team.text] = {'link': self.link,
                                           'Jugadores':{},
                                           'Estadisticas': self.Stat_team}

        self.Export_json(self.equipos,'Equipos.json')
        # return True


    def get_info_team(self,equipo):
        Conexion_by_browser.__init__(self)
        self.equipo = equipo
        self.nombre_team = list(self.equipo.keys())[0]
        self.enlace = self.equipo.get(self.nombre_team).get('link')
        self.html = self.Parseo_web(self.enlace)
        ### Accedemos a las cajas ('box') de los jugadores.
        self._box = self.html.find_all('div',attrs={'id':'plantilla'})[0].find_all('a',attrs={'class':'box-jugador'})

        self.Team = {self.nombre_team: {'Jugadores': {}}}

        for jug in self._box:
            ########## Parseamos la pagina del jugador
            self.jug_enlace = jug.get('href')
            # self.jug_enlace = 'https://www.laliga.es/jugador/messi'
            # self.jug_enlace ='https://www.laliga.es/jugador/lucas-hernandez'
            # self.html = self.Parseo_web(self.jug_enlace)
            self.html = self.Navegar_web(self.jug_enlace)
            self.jug_perfil = self.html.find_all('div',attrs={'id':'datos-perfil'})[0].find_all('div')

            """ 1/ Obtenemos los datos generales del jugador """
            print('Obteniendo Datos Generales del Jugador...')
            self.Datos_jugador = {}
            for param in self.jug_perfil:
                self.Non_Params = ['Trayectoria','lugar_nacimiento']
                if param.get('id') in self.Non_Params: continue
                self.Datos_jugador[param.get('id')] = param.text


            self.informacion_jug = self.html.find_all('div',attrs={'class':'box-dato'})

            for info in self.informacion_jug[:-1]:
                if not info.find_all('div', attrs={'class','nombre'}):
                    self._dato = info.find_all('h2', attrs={'class','nombre'})[0].text
                else:
                    self._dato = info.find_all('div', attrs={'class', 'nombre'})[0].text
                self._valor = info.find_all('div', attrs={'class','dato'})[0].text

                self.Datos_jugador[self._dato] = self._valor

            self.Nombre_short = self.html.find_all('h1', attrs={'id': 'nickname'})[0].text
            self.Datos_jugador['nick'] = self.Nombre_short
            self.Nombre_full  = self.Datos_jugador.get('nombre')



            """ 2/ Estadisticas del jugador """
            print('Obteniendo Estadisticas del Jugador...')
            self.Estadisticas_jugador = {}
            # Miramos si el contenedor de las estadisticas esta vacio o no
            self.contenedor_est = self.html.find_all('section',attrs={'class':'contenedor-graficas-jugador'})[0]
            self.contenedor_est = self.contenedor_est.find_all('div')

            if len(self.contenedor_est) != 1:

                # sacamos las cabeceras de las tablas
                self._box_est = self.html.find_all('section',attrs={'id':'box-estadisticas-jugador'})[0]
                self._cabeceras = self._box_est.find_all('nav',attrs={'class':'cabecera-seccion-2 submenu'})[0].find_all('ul')
                self._cabeceras_url = [cab.get('href') for cab in self._cabeceras[0].find_all('a')]
                self._cabeceras_text = [cab.text.strip() for cab in self._cabeceras[0].find_all('a')]

                for cab_text,cab_url in zip(self._cabeceras_text,self._cabeceras_url):
                    self.html = self.Parseo_web(cab_url)
                    self._box_est = self.html.find_all('section', attrs={'id': 'box-estadisticas-jugador'})[0]

                    self._tablas = self._box_est.find_all('table')

                    self.data = {}
                    for tabla in self._tablas:
                        self._params_init = tabla.find_all('tr')

                        self._params=[]
                        for row in self._params_init:
                            if not row.get('class'):
                                self._params.append(row)
                                continue
                            if row.get('class')[0].find('mostrar_movil') == -1:
                                self._params.append(row)

                        self._caract = self._params[0]
                        self._vals = self._params[1:]

                        self.caracts = [caract.get('title') for caract in self._caract.find_all('th') ][1:]

                        for row in self._vals:
                            self._v = [ vals.text for vals in row]
                            self.data[self._v[0]]=self._v[1:]


                    self.Estadisticas_jugador[cab_text] = {'Params': self.caracts,
                                                           'Values': self.data }


                # Mapas de calor

                self.lista_mapas = self.html.find_all('div', attrs={'id':'selector-mapa-calor'})[0]
                self.lista_mapas = self.lista_mapas.find_all('option')
                self.mapas = [mapa.get('value') for mapa in self.lista_mapas]
                self.partidos =[mapa.text for mapa in self.lista_mapas]

                self.mapas_calor = {}
                for mapa,partido in zip(self.mapas,self.partidos):
                    self.html_web = self.Navegar_web(self.jug_enlace, format='web')
                    self.select = Select(self.html_web.find_element_by_class_name('formulario'))
                    self.select.select_by_value(mapa)
                    sleep(2.5)
                    self.mapa_calor = self.get_image_from_canvas(self.html_web,mapa,self.nombre_team)
                    self.mapas_calor[partido] = self.mapa_calor.tolist()
                    # self.mapas_calor = 1

                self.Estadisticas_jugador['Mapas_Calor'] = self.mapas_calor


            """ 3/ Caracteristicas del jugador  """
            print('Obteniendo Caracteristicas del Jugador...')
            self.html = self.page_skills(self.Nombre_full,self.Nombre_short,self.nombre_team)
            if self.html:
                self.Generales,self.Fisicas = self.skills(self.html)
            else:
                self.Generales, self.Fisicas = {},{}
            self.Caracteristicas_jugador = {'generales': self.Generales, 'fisicas': self.Fisicas}

            self.Team[self.nombre_team]['Jugadores'][self.Nombre_full] = \
            {    'Info_general': self.Datos_jugador,
                 'Estadisticas': self.Estadisticas_jugador,
                 'Caracteristicas' : self.Caracteristicas_jugador
            }
            ##############
            # self.equipos[self.nombre_team]['Jugadores'][self.Nombre_full] = \
            #     {'Info_general': self.Datos_jugador,
            #      'Estadisticas': self.Estadisticas_jugador,
            #      'Caracteristicas' : self.Caracteristicas_jugador}
            ##############

            # break
            #####
        # break
        self.Traza(self.nombre_team)
        self.Export_json(self.Team,'/Equipos_json/'+self.nombre_team +'.json')
        # return True

    def Traza(self,team):
        if not os.path.isfile(os.getcwd() + '/' + 'traza.txt'):
            self.Crear_Traza()
        _t = self.Recuperar_traza()
        _t.remove(team)
        self.traza = open(os.getcwd() + '/traza.txt', 'wb')
        for i in self._equipos.keys():
            self._e = i + '\n'
            traza.write(self._e.encode())
        self.traza.close()

    def Crear_Traza(self):
        self._equipos = self.Import_json()
        self.traza = open(os.getcwd() + '/traza.txt', 'wb')
        for i in self._equipos.keys():
            self._e = i + '\n'
            traza.write(self._e.encode())
        self.traza.close()

    def Recuperar_traza(self):
        self._txt = open(os.getcwd() + '/traza.txt', 'r')
        self._t = [line.split("\n")[0] for line in self._txt]
        self._txt.close()
        return self._t








if __name__ == "__main__":

    client = Client(processes = True)
    DB = Plantillas()
    equipos = DB.Import_json()
    traza = open(os.getcwd() + '/traza.txt', 'wb')






    # tasks = [dask.delayed(DB.get_info_team)({team: equipos.get(team)}) for team in equipos]
    # dask.compute(*tasks)

    tasks = [DB.get_info_team({team: equipos.get(team)}) for team in equipos]
