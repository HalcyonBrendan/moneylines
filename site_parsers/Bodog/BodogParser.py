from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display

class BodogParser():

	def __init__(self):
		self.links = {}
		self.links["hockey"] = "https://sports.bodog.eu/hockey/nhl-playoffs"

	def run(self):

		games_at_link = []
		
		# scroll to make sure we reveal all the hidden games
		games = self.obtain_games()

		# print games

		for game in games:

			names = game.find_elements_by_css_selector(
				'header.event-shortnames')
			#print "names: {}".format(names)
			moneyline = game.find_elements_by_css_selector('ul.ng-isolate-scope')[1]
			moneyline = moneyline.find_elements_by_css_selector('span.ng-binding')
			#print "moneyline: {}".format(moneyline)

			try:

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

			except:
				print "Error with line"
				continue
			# print "{0} {1}".format(home_line, away_line)
			name_objects = names[0].find_elements_by_css_selector('h4.ng-binding')
			away_team = str(name_objects[0].text)
			home_team = str(name_objects[1].text)

			# print "{0} {1} {2} {3}".format(home_team, home_line, away_team, away_line)

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