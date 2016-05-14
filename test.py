from Emailer import Emailer
from time import sleep

notes = [["test", "123"], ["jest","124"]]

my_emailer = Emailer()

for i in range(20):
	my_emailer.send_email(notes)