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
        self.sports_translations = config["sports_translations"]
        self.driver = driver
        self.acceptable_delay = 10 #s

    def login(self):

        self.driver.get('http://www.5dimes.eu/sportsbook.html')

        username = self.driver.find_element_by_name('customerID')
        password = self.driver.find_element_by_name('password')

        username.send_keys("5D2294959")
        password.send_keys("5tUdmaster")
        password.send_keys(Keys.RETURN)

    def logout(self):

        link = self.driver.find_element_by_link_text('sign out')
        link.click()

    def get_moneylines(self, sports):

        self.login()

        moneylines = []

        for sport in sports:
            # print sport, sports
            if sport in self.sports_translations.keys():
                try:
                    # print self.sports_translations[sport]
                    WebDriverWait(self.driver, self.acceptable_delay).until(
                        EC.presence_of_element_located((By.NAME, self.sports_translations[sport])))
                        # self.driver.find_element_by_id(self.sports_translations[sport])))
                    # print "Page is ready!"
                except TimeoutException:
                    print "Loading took too much time!"

                # sleep(5)

                # self.driver.find_element_by_name(self.sports_translations[sport]).click()
                self.driver.find_element_by_name(self.sports_translations[sport]).click()
                self.driver.find_element_by_id('btnContinue').click()

                try:
                    # print self.sports_translations[sport]
                    WebDriverWait(self.driver, self.acceptable_delay).until(
                        EC.presence_of_element_located((By.ID, 'tblBaseballMLBGame')))
                        # self.driver.find_element_by_id(self.sports_translations[sport])))
                    # print "Page is ready!"
                except TimeoutException:
                    print "Loading took too much time!"

                soup = BeautifulSoup(self.driver.page_source, "html.parser")

                # print soup

                away_cells = soup.findAll("tr", { "class" : "linesRow" })
                home_cells = soup.findAll("tr", { "class" : "linesRowBot" })


                for i in range(len(away_cells)):

                    lines_for_this_game = {}

                    elements = away_cells[i].findAll('td')

                    game_time = {
                        "day": str(re.split(" ",elements[0].getText())[0]).upper(),
                        "time": ""
                    }

                    away_list = re.split("\W+",elements[2].getText().replace(u'\xa0', u' '))[1:]
                    away_string = []
                    away_string.append(str(away_list[0]))
                    away_string.append(str(away_list[1]))
                    for j in range(2,len(away_list)):
                        if len(str(away_list[j])) > 2:
                            away_string.append(str(away_list[j]))
                        else:
                            break
                    
                    away_team = self.translate_name(" ".join(away_string), sport)

                    away_line = int(re.split(' ',str(elements[4].getText().replace(u'\xa0', u'')))[0])

                    elements = home_cells[i].findAll('td')

                    game_time["time"] = str(re.split(" ",elements[0].getText())[0]).lower()

                    home_list = re.split("\W+",elements[2].getText().replace(u'\xa0', u' '))[1:]
                    home_string = []
                    home_string.append(str(home_list[0]))
                    home_string.append(str(home_list[1]))
                    for j in range(2,len(home_list)):
                        if len(str(home_list[j])) > 2:
                            home_string.append(str(home_list[j]))
                        else:
                            break
                    
                    home_team = self.translate_name(" ".join(home_string), sport)

                    home_line = int(re.split(' ',str(elements[4].getText().replace(u'\xa0', u'')))[0])

                    moneylines.append(
                    {
                        "home_team": home_team, 
                        "away_team": away_team,
                        "game_time": game_time, 
                        "home_line": home_line, 
                        "away_line": away_line,
                        "sport":sport
                    }
                )
            else:
                "{} not yet available for 5Dimes".format(sport)

            self.driver.execute_script("window.history.go(-1)")

            try:
                # print self.sports_translations[sport]
                WebDriverWait(self.driver, self.acceptable_delay).until(
                    EC.presence_of_element_located((By.NAME, self.sports_translations[sport])))
                    # self.driver.find_element_by_id(self.sports_translations[sport])))
                # print "Page is ready!"
            except TimeoutException:
                print "Loading took too much time!"

            self.driver.find_element_by_name(self.sports_translations[sport]).click() # unclick

        try:
            self.logout()
        except:
            pass

        return {"site": "5Dimes", "moneylines": moneylines}

    def translate_name(self, long_form, sport):
        # print long_form
        for short_form in config["short_names"][sport]:
            if long_form in config["short_names"][sport][short_form]:
                return short_form

        return long_form

if __name__ == "__main__":
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Firefox()
    parser = FiveDimesParser(driver)
    sports = ['baseball']
    results = parser.get_moneylines(sports)

    # for result in results:
    #     if failure_string in results:
    #         print_json(result)
    print_json(results)

    driver.close()
