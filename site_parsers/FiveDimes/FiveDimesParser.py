from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
from time import sleep
from bs4 import BeautifulSoup
from config import CONFIG as config
import re, json

def print_json(json_object):
    print json.dumps(json_object, indent=4, sort_keys=True) 
    print "\n"

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
        password.send_keys("5tUdmaster")
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

                try:
                    print self.sports_translations[sport]
                    WebDriverWait(self.driver, self.acceptable_delay).until(
                        EC.presence_of_element_located((By.ID, 'tblBaseballMLBGame')))
                        # self.driver.find_element_by_id(self.sports_translations[sport])))
                    print "Page is ready!"
                except TimeoutException:
                    print "Loading took too much time!"

                soup = BeautifulSoup(self.driver.page_source, "html.parser")

                # print soup

                away_teams = soup.findAll("tr", { "class" : "linesRow" })
                home_teams = soup.findAll("tr", { "class" : "linesRowBot" })

                # print away_teams[0]

                game_lines = []

                for i in range(len(away_teams)):
                    game_lines.append({})

                    game_lines[i]["sport"] = sport
                    game_lines[i]["site"] = "5Dimes"

                    elements = away_teams[i].findAll('td')

                    game_lines[i]["game_time"] = str(re.split(" ",elements[0].getText())[0])

                    away_list = re.split("\W+",elements[2].getText().replace(u'\xa0', u' '))[1:]
                    away_string = []
                    away_string.append(str(away_list[0]))
                    away_string.append(str(away_list[1]))
                    for j in range(2,len(away_list)):
                        if len(str(away_list[j])) > 2:
                            away_string.append(str(away_list[j]))
                        else:
                            break
                    
                    game_lines[i]["away_team"] = self.translate_name(" ".join(away_string), sport)

                    game_lines[i]["away_line"] = re.split(' ',str(elements[4].getText().replace(u'\xa0', u'')))[0]

                    elements = home_teams[i].findAll('td')

                    home_list = re.split("\W+",elements[2].getText().replace(u'\xa0', u' '))[1:]
                    home_string = []
                    home_string.append(str(home_list[0]))
                    home_string.append(str(home_list[1]))
                    for j in range(2,len(home_list)):
                        if len(str(home_list[j])) > 2:
                            home_string.append(str(home_list[j]))
                        else:
                            break
                    
                    game_lines[i]["home_team"] = self.translate_name(" ".join(home_string), sport)

                    game_lines[i]["home_line"] = re.split(' ',str(elements[4].getText().replace(u'\xa0', u'')))[0]


                 

                    # for i in range(len(away_list)):
                    #     if len(away_list[i]) < 3:
                    #         away_list = away_list[:i]
                    #         break
                    
                    # game_lines[i]["away_team"] = " ".join(away_list)

                # away_teams = self.driver.find_element_by_class_name('linesRow')
                # home_teams = self.driver.find_element_by_class_name('linesRowBottom')

                # for i in range(len(away_teams)):
                #     away_teams[i] = away_teams[i].

            else:
                "{} not yet available for 5Dimes".format(sport)

            sleep(5)
            self.driver.execute_script("window.history.go(-1)")
            self.driver.find_element_by_name(self.sports_translations[sport]).click() # unclick

            return game_lines

    def translate_name(self, long_form, sport):
        print long_form
        for short_form in config["short_names"][sport]:
            if long_form in config["short_names"][sport][short_form]:
                return short_form

if __name__ == "__main__":
    parser = FiveDimesParser(webdriver.Firefox())
    sports = ['baseball']
    print_json(parser.get_moneylines(sports))
