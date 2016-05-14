from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
from time import sleep

class FiveDimesParser():

    def __init__(self, driver):
        self.sports_translations = {"hockey": "Hockey_NHL", 
                                    "baseball": "Baseball_MLB",
                                    "basketball": "Basketball_NBA"
                                   }
        self.driver = driver
        self.acceptable_delay = 10 #s
        self.driver.get('http://www.5dimes.eu/sportsbook.html')
        self.login()

    def login(self):
        username = self.driver.find_element_by_name('customerID')
        password = self.driver.find_element_by_name('password')

        username.send_keys("5D2294959")
        password.send_keys("pwd")
        password.send_keys(Keys.RETURN)

    def get_moneylines(self, sports):
        for sport in sports:
            if sport in self.sports_translations.keys():
                try:
                    print self.sports_translations[sport]
                    WebDriverWait(self.driver, self.acceptable_delay).until(
                        EC.presence_of_element_located((By.NAME, self.sports_translations[sport])))
                        # self.driver.find_element_by_id(self.sports_translations[sport])))
                    print "Page is ready!"
                except TimeoutException:
                    print "Loading took too much time!"

                # sleep(5)

                # self.driver.find_element_by_name(self.sports_translations[sport]).click()
                self.driver.find_element_by_name(self.sports_translations[sport]).click()
                self.driver.find_element_by_id('btnContinue').click()

            else:
                "{} not yet available for 5Dimes".format(sport)

            sleep(5)
            self.driver.execute_script("window.history.go(-1)")
            self.driver.find_element_by_name(self.sports_translations[sport]).click() # unclick

if __name__ == "__main__":
    parser = FiveDimesParser(webdriver.Firefox())
    sports = ['hockey', 'baseball']
    parser.get_moneylines(sports)
