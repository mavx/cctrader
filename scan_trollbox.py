import collections
import time
import logging
import re
import datetime

logging.basicConfig(filename='keyword_frequency.log', format='%(asctime)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)

def write(text_input):
	import sys
	sys.stdout.write('\r')
	sys.stdout.write(text_input)
	sys.stdout.flush()

def scan():
	file = open('msg_trollbox.log', 'r').read()
	
	#wordList = ['beef', 'coin', 'troll']
	currencies = open('currencies.txt', 'r').read()
	wordList = currencies.split(',')
	
	c = collections.Counter()
	for word in wordList:
		wholeWord = r'\b(' + word + r'\b)'
		match = re.findall(wholeWord, file, flags=re.IGNORECASE)
		final = map(str.lower, match)
		c.update(final)
		#print(r'\b(' + word + r')\b')
	logging.info(c)
	#timestamp = datetime.datetime.now()
	timestamp = time.strftime("%d/%m/%Y %H:%M:%S")
	write('last run: %r' % timestamp)
	#print(c)

	time.sleep(60)

while True:
	scan()


