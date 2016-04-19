import time, datetime, pytz, re, sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
from config import CONFIG as config

class HTML_parser():

    def __init__(self):

        self.betting_website_links = config["bookie_links"]
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        # login to allow modification of roster
        self.driver = webdriver.Firefox()

    def get_moneylines(self):

        sports = self.betting_website_links.keys()

        games_to_return = {}

        for sport in sports:

            print "\tParsing {} games".format(sport)

            games_to_return[sport] = []

            sites = self.betting_website_links[sport].keys()

            for site in sites:

                print "\t\tParsing {}".format(site)

                # access website
                self.driver.get(self.betting_website_links[sport][site])

                games_at_link = []
                
                # scroll to make sure we reveal all the hidden games
                games = self.obtain_games()

                print games

                for game in games:

                    names = game.find_elements_by_css_selector(
                        'header.event-shortnames')
                    moneyline = game.find_elements_by_css_selector('ul.ng-isolate-scope')[1]
                    moneyline = moneyline.find_elements_by_css_selector('span.ng-binding')

                    if type(moneyline[0].get_attribute("innerHTML") == unicode):
                        try:
                            # this will fail if there are no lines yet
                            away_line = self.convert_line_to_int(moneyline[0].get_attribute("innerHTML"))
                            home_line = self.convert_line_to_int(moneyline[1].get_attribute("innerHTML"))
                        except:
                            print "No lines available yet"
                            continue
                    else:
                        try:
                            # this will fail if there are no lines yet
                            away_line = self.convert_line_to_int(moneyline[0].text.encode('utf-8'))
                            home_line = self.convert_line_to_int(moneyline[1].text.encode('utf-8'))
                        except:
                            print "No lines available yet"
                            continue
                # print names[0]
                    name_objects = names[0].find_elements_by_css_selector('h4.ng-binding')
                    away_team = str(name_objects[0].text)
                    home_team = str(name_objects[1].text)

                    # determine if the game is live
                    live = game.find_elements_by_css_selector('span.live-event.ng-scope')

                    timestamp = int(time.time())
                    # find time value based on whether live or not
                    if len(live) > 0:
                        # try to get live time value
                        # failure met by showing that the time is 20:00 P1
                        try:
                            game_time = {"day": None, "time":game.find_element_by_css_selector(
                                'time.ng-binding.ng-scope.ng-isolate-scope').text}
                        except:
                            game_time = {"day": None, "time":"starting"}

                        games_at_link.append({"poll_time":timestamp,
                            "home_team": home_team, "away_team": away_team,
                            "game_time": game_time,
                            "home_line": home_line, "away_line": away_line,
                            "site": site, "status": "live",
                            "sport":sport})                   
                    else:
                        game_time = re.split(" ",str(game.find_element_by_css_selector(
                            'time.ng-binding.ng-scope').text))

                        game_time = {"day": game_time[0], "time":game_time[1]}

                        games_at_link.append({"poll_time":timestamp, 
                            "home_team": home_team, "away_team": away_team,
                            "game_time": game_time, 
                            "home_line": home_line, "away_line": away_line,
                            "site": site, "status":"upcoming",
                            "sport":sport})
                        


                    print "{0}({3}) at {1}({4}), {2}".format(away_team, home_team, 
                        game_time, moneyline[0].text.encode('utf-8'), moneyline[1].text.encode('utf-8'))

                games_to_return[sport].append({"site":site, "moneylines":games_at_link})

        return games_to_return


    def obtain_games(self):
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

        return games

    def convert_line_to_int(self, line):
        if type(line) == unicode:
            line = line.encode('utf-8')
        elif type(line) != str:
            print "invalid type for conversion"
            return None

        if "+" in line:
            result = int(line[1:])
        else:
            result = int(line)

        return result