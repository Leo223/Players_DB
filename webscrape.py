from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os

import time

class Navegar():


    def __init__(self):
        self.ruta = os.getcwd()
        self.rutaDrivers = self.ruta + '/Drivers/geckodriver'
        self.rutaDrivers = self.ruta + '/Drivers/chromedriver'
        self.browser = webdriver


    def Firefox(self):
        self.browser = self.browser.Firefox(executable_path=self.rutaDrivers)
        return self.browser

    def Chrome(self):
        self.options = self.browser.ChromeOptions()
        self.options.add_argument("headless")
        self.browser = self.browser.Chrome(executable_path=self.rutaDrivers,chrome_options=self.options)
        return self.browser


    def Login(self):
        self.browser = self.Chrome()
        self.url1 = 'https://biwenger.as.com/login'
        self.params = {'usuario':'mazarambroz61@gmail.com','password':'JuliosPower'}
        self.browser.get(self.url1)

        self.botones = {
            'logearse':'/html/body/app-root/main/ng-component/div/div[2]/button[1]',
            'submit_login':'//*[@id="login-wrapper"]/div[2]/form/button'}

        self.elem = self.browser.find_element_by_xpath(self.botones.get('logearse')).click()
        self.usuario = self.browser.find_element_by_name("email")
        self.password = self.browser.find_element_by_name("password")
        self.usuario.send_keys(self.params.get('usuario'))
        self.password.send_keys(self.params.get('password'))

        self.entrar = self.browser.find_element_by_xpath(self.botones.get('submit_login'))
        self.entrar.click()

        time.sleep(3)
        self.html = self.browser.page_source

        print (self.html)

        # return self.browser



    def exe(self):

        self.Login()

        # self.browser.close()








if __name__ == "__main__":
    Navegar().Login()




# browser.close()
# browser.quit()