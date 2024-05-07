import random
import string
import pyfiglet
from getpass import getpass
import argparse
from functools import wraps
import sys
from support import DB
from support.dbManage import store_in_db, fetch_from_db
from support.encrypt_decrypt import endec, is_encrypted


def lock() -> None:
	if not is_encrypted(DB):
		endec()
lock()


def interaction_wrapper(func: callable, *args, **kwargs):
	try:
		endec()
		func(*args, **kwargs)
		endec()
	except:
		lock()


def looper(func: callable) -> callable:
	@wraps(func)
	def mod_func():
		func()
		while not input('Wanna quit?(y/n) ').strip().lower().startswith('y'):
			func()
			print()
	return mod_func


def get_int(prompt: str) -> int:
	while True:
		try:
			return int(input(prompt))
		except:
			continue


@looper
def interface_generator() -> None:
	included = ''
	sample_space = {
			'uppercase alphabets': string.ascii_uppercase,
			'lowercase alphabets': string.ascii_lowercase,
			'decimal digits': string.digits,
			'special characters': string.punctuation, 'whitespace': ' '
	}

	for name, sample in sample_space.items():
		if not input(f"Want to include {name} (y/n) [defaults to y]: ").strip().lower().startswith('n'):
			included += sample
			print("Included")
		else:
			print("Left")

	length = get_int("What length of password is desired? ")

	pswd = ''.join(random.choices(included, k = length))

	print(f"Password Generated: {pswd}")

	if input('Wanna store this password in the database?(y/n) ').strip().lower().startswith('y'):
		interface_registrar(pswd)


def interface_registrar(pswd: str | None = None) -> None:
	place, uname = None, None

	while not place:
		place = input('For which place registration is to be made? ')
	while not uname:
		uname = input('Your username for this place? ')
	if not pswd:
		while (pswd := getpass('Enter the password to store: ')) != getpass('Confirm Password: '):
			print('Confirm Password and Password does\'t match. Retry!\n')

	interaction_wrapper(store_in_db, place, uname, pswd, DB)


@looper
def ui_registrar() -> None:
	interface_registrar()


@looper
def interface_fetcher() -> None:
	place = input('Search with place: ')
	uname = input('Search with username: ')
	show = input('Wanna show passwords?(y/n) ').strip().lower().startswith('y')

	interaction_wrapper(fetch_from_db, place, uname, show, DB)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog = 'UI', description = 'Command-Line Interface generator for password management')
	parser.add_argument('-s', '--store', action = 'store_true', dest = 'store',
				help = 'Pull out password storing interface')
	parser.add_argument('-g', '--generator', action = 'store_true', dest = 'generate',
				help = 'Pull out password generator interface')
	parser.add_argument('-f', '--fetch', action = 'store_true', dest = 'fetch',
				help = 'Pull out password fetching interface')
	args = parser.parse_args()

	if args.store:
		ui_registrar()
	if args.generate:
		interface_generator()
	if args.fetch:
		interface_fetcher()

	print(pyfiglet.figlet_format('Command line Interface'))
	print('Usage:-')
	print('\tstore - Pulls out storing in database interface')
	print('\tfetch - Pulls out fetch from database interface')
	print('\tgenerate - Pulls out password generation interface')
	print('\tquit - Bails out')
	cmd_to_func = {
		'store': interface_registrar,
		'fetch': interface_fetcher.__wrapped__,
		'generate': interface_generator.__wrapped__,
		'quit': sys.exit,
	}
	while True:
		cmd = input('> ').strip()
		if cmd in cmd_to_func:
			cmd_to_func[cmd]()