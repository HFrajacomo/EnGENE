'''
Functions for error handling
'''

from colorama import Fore, init
init(autoreset=True)

def error(ecode, message, quit=True):
	print(f'{Fore.RED}Error #{ecode}: {message}')
	if(quit):
		exit()

def warning(wcode, message):
	print(f'{Fore.YELLOW}Warning #{wcode}: {message}')