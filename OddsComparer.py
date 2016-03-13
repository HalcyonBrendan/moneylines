# from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
import requests, re, time, smtplib, sys, datetime
import email.message
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from config import CONFIG as config
import MySQLdb

class OddsComparer():

    def __init__(self):
        self.betting_website_links = {}
        self.db = MySQLdb.connect(passwd=config["mysql"]["pw"],host="localhost",
            user="root", db="betting")
        self.cursor = self.db.cursor()
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        # login to allow modification of roster
        self.driver = webdriver.Firefox()
        self.games = {"live": [], "upcoming": []}
        self.timestamp = 0

    def add_website(self,website):
        self.betting_website_links[website["shorthand"]] = website["link"]

    def update_moneylines(self, shorthand):

        link = self.betting_website_links[shorthand]

        # access website
        self.driver.get(link)

        previous_length = 0
        # scroll to make sure we reveal all the hidden games
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

        self.timestamp= int(time.time())

        for game in games:

            names = game.find_elements_by_css_selector(
                'header.event-shortnames')
            moneyline = game.find_elements_by_css_selector('ul.ng-isolate-scope')[1]
            moneyline = moneyline.find_elements_by_css_selector('span.ng-binding')
            away_line = self.convert_line_to_int(moneyline[0].text.encode('utf-8'))
            home_line = self.convert_line_to_int(moneyline[1].text.encode('utf-8'))
        # print names[0]
            name_objects = names[0].find_elements_by_css_selector('h4.ng-binding')
            away_team = name_objects[0].text
            home_team = name_objects[1].text

            # determine if the game is live
            live = game.find_elements_by_css_selector('span.live-event.ng-scope')
            # find time value based on whether live or not
            if len(live) > 0:
                # try to get live time value
                # failure met by showing that the time is 20:00 P1
                try:
                    game_time = game.find_element_by_css_selector(
                        'time.ng-binding.ng-scope.ng-isolate-scope').text
                except:
                    game_time = "20:00 P1"

                self.games["live"].append({"poll_time":self.timestamp,
                    "home_team": home_team, "away_team": away_team,
                    "game_time": game_time, "home_line": home_line,
                    "away_line": away_line,
                    "site": shorthand})                   
            else:
                game_time = game.find_element_by_css_selector(
                    'time.ng-binding.ng-scope').text

                self.games["upcoming"].append({"poll_time":self.timestamp, 
                    "home_team": home_team, "away_team": away_team,
                    "game_time": game_time, "home_line": home_line,
                    "away_line": away_line,
                    "site": shorthand})
                


            print "{0}({3}) at {1}({4}), {2}".format(away_team, home_team, 
                game_time, moneyline[0].text.encode('utf-8'), moneyline[1].text.encode('utf-8'))

        # locate the proper fields (teams, start time, moneylines)


        # find all players in webpage

        
        # soup = BeautifulSoup(r.content,'html.parser')
        # table = soup.find("table",{"class": "Tst-table Table"}).tbody
        # players = table.findAll('tr')

        self.driver.close()
        self.display.stop()

    def convert_line_to_int(self, line):
        if "+" in line:
            result = int(line[1:])
        else:
            result = int(line)

        # print "input: {0}, output ({1}): {2}".format(line, type(result), result)
        return result

    def add_moneylines_to_database(self):

        games_to_add = self.games["live"] + self.games["upcoming"]


        for game in games_to_add:
            # print type(game["home_line"])
            # print type(game["away_line"])
            self.cursor.execute("""INSERT INTO money_lines (poll_time, site, 
    game_time, home_team, home_line, away_team, away_line) VALUES 
    (%s,%s,%s, %s, %s, %s, %s)""",(game["poll_time"], game["site"],0,game["home_team"],
        game["home_line"], game["away_team"], game["away_line"]))

        self.db.commit()



    def flush_games(self):
        self.games = {"live": [], "upcoming": []}

    def convert_game_time_to_unix(self, time):
        pass

    def send_email(self, notes_to_send):
        print "Preparing email"
        m = email.message.Message()
        m['From'] = config["email"]["address"]
        m['To'] = config["email"]["address"]
        m['Subject'] = "Notable player transactions"

        my_payload = get_email_string(notes_to_send)

        m.set_payload(my_payload)

        try:
            # print("trying host and port...")

            smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtpObj.login("alfred.e.kenny@gmail.com", config.CONFIG["email"]["app_pw"])

            # print("sending mail...")

            smtpObj.sendmail(config["email"]["address"], config["email"]["address"], m.as_string())

            # print("Succesfully sent email")

        except smtplib.SMTPException:
            print("Error: unable to send email")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    odds = OddsComparer()
    odds.add_website({"link":"https://sports.bodog.eu/hockey/nhl",
        "shorthand": "bodog"})
    odds.update_moneylines("bodog")
    odds.add_moneylines_to_database()
    odds.flush_games()
    # print information
    # store in db
    # check against fake entry
    # send email with odds


