from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
from config import CONFIG as config
from bs4 import BeautifulSoup
import time, json, re

def print_json(json_object):
    print json.dumps(json_object, indent=4, sort_keys=True) 
    print "\n"

class bodogParser():

    def __init__(self, driver):
        self.driver = driver
        self.links = config["sport_webpages"]

    def get_moneylines(self, sports):

        moneylines = []
        
        for sport in sports:

            self.driver.get(self.links[sport])

            # scroll to make sure we reveal all the hidden games
            self.scroll()

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            game_cells = soup.findAll("article", {"class" :"gameline-layout ng-scope show-cta"})

            # print len(game_cells)

            for cell in game_cells:

                teams = cell.findAll("h3", {"class" :"ng-binding ng-scope"})
                away_team = self.translate_name(teams[0].getText(), sport)
                home_team = self.translate_name(teams[1].getText(), sport)

                day, time = re.split(' ',str(cell.findAll("time")[0].getText()))

                time = time.replace('.',':')

                game_time = {"day": day, "time": time}

                moneyline_cells = cell.findAll('ul', {'class': "ng-isolate-scope"})[1]
                lines = moneyline_cells.findAll('span', {'class': 'ng-binding'})

                away_line = int(str((lines[0].getText())))
                home_line = int(str((lines[1].getText())))

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

        return {"site": "bodog", "moneylines": moneylines}

    def scroll(self):

        previous_length = 0

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            games = self.driver.find_elements_by_css_selector(
                'article.gameline-layout.ng-scope.show-cta')
            print "previous length was {0}, new length is {1}".format(
                previous_length, len(games))
            if len(games) == previous_length and len(games) != 0:
                break
            previous_length = len(games)
            time.sleep(2)

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
    parser = bodogParser(driver)
    sports = ['baseball']
    results = parser.get_moneylines(sports)

    # for result in results:
    #     if failure_string in results:
    #         print_json(result)
    print_json(results)

    driver.close()