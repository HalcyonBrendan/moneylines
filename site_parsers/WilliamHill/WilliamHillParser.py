from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display

class WilliamHillParser():

    def __init__(self, driver):
        self.sports = {"hockey": "Hockey_NHL", 
                       "baseball": "Baseball_MLB",
                       "basketball": "Basketball_NBA"
                        }
        self.driver = driver
        self.sports = self.translate_sports(sports)
        self.driver.get('http://www.5dimes.eu/sportsbook.html')
        self.login()

    def login(self):
        username = self.driver.driver.find_element_by_name('customerID')
        password = driver.find_element_by_name('password')

        username.send_keys("id")
        password.send_keys("pwd")
        password.send_keys(Keys.RETURN)

    def translate_sports(self, sports):
        for sport in sports:
            if sport in self.sports.keys():

            else:
                "{} not yet available for 5Dimes"



    def get_moneylines(sport):
        
