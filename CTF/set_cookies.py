"""
Simple program to make requests to a given URL with given cookie settings.

Author: G Hampton
Date: 24 Mar 2025

TODO: Add support for multiple cookie values
TODO: Support diff-only output; make default
TODO: Add an optional expected value
TODO: Implement better rate-limiting prevention
"""
import requests
import argparse
import time

class CookieCustomiser():
	def __init__(self):
		self.url = ""
		self.cookie_name = ""
		self.cookie_val = ""

	def get_url_and_cookie_name(self):
		self.url = input('URL:  ')
		self.cookie_name = input('Cookie name:  ')

	def request_manual(self):
		EXIT_STR = ':q'
		self.cookie_val = input(f'Cookie val [{EXIT_STR} to exit]:  ')
		while self.cookie_val != EXIT_STR:
			self._request_with_val()
			self.cookie_val = input(f'Cookie val [{EXIT_STR} to exit]:  ')

	def request_integer_range(self):
		start = input('Range start [0]:  ')
		start = int(start) if start != '' else 0
		end = int(input('Range end:  '))
		step = input('Range step [1]:  ')
		step = int(step) if step != '' else 1

		for i in range(start, end, step):
			self.cookie_val = i
			time.sleep(0.25)
			self._request_with_val()

	def _request_with_val(self):
		cookie = f'{self.cookie_name}={self.cookie_val}'
		headers = {'Cookie':cookie}

		r = requests.get(self.url, headers=headers)
		print('=' * 30 + f'  {self.cookie_val}  ' + '=' * 30)
		print(f'Status: {r.status_code}')
		print(r.text)
		print()


if __name__ == "__main__":
	# Arg parsing
	parser = argparse.ArgumentParser()
	parser.add_argument('--entry-type', '-et', default="manual", choices=[
		'manual',
		'int-range',
	], help="Manner of cookie entry. One of:" + \
		"- manual:  ask for input and request after each given input" + \
		"- int-range: ask for an int start, end, and step; try for each integer"
	)
	arguments = parser.parse_args()
	cc = CookieCustomiser()
	# handling
	match arguments.entry_type:
		case 'int-range':
			operate = cc.request_integer_range
		case _:
			operate = cc.request_manual

	# Run it
	cc.get_url_and_cookie_name()
	operate()
