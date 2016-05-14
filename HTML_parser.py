import time, datetime, pytz, re, sys, importlib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
from config import CONFIG as config

class HTML_parser():

	def __init__(self):

		self.betting_websites = config["bookies"]
		self.sports = config["sports"]
		self.display = Display(visible=0, size=(800, 600))
		self.display.start()
		# login to allow modification of roster
		self.driver = webdriver.Firefox()
		self.parsers = {}
		self.load_parsers()

	def load_parsers(self):
		for site in self.betting_websites:
			ParserClass = getattr(importlib.import_module("module.submodule"), "Klass")
			instance = MyClass()

			self.parsers[site] = 

	def get_moneylines(self):

		sports = self.betting_website_links.keys()

		games_to_return = {}

		for sport in sports:

			print "\tParsing {} games".format(sport)

			games_to_return[sport] = []

			for site in self.betting_websites:

				print "\t\tParsing {}".format(site)

				games_at_site = self.scrape_site(site)				

				games_to_return[sport].append({"site":site, "moneylines":games_at_site})

		return games_to_return

	def scrape_site(site):


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
