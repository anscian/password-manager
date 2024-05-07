import sqlite3
from argparse import ArgumentParser, ArgumentTypeError, Action, Namespace
from tabulate import tabulate
from getpass import getpass
from typing import Any, Sequence
from . import DB
from .encrypt_decrypt import is_encrypted
from typing import List


# Checker decorable functions are expected with dbfile as last positional argument
def checker(func: callable) -> callable:
	def checked_exec(*args, **kwargs):
		db = args[-1] if kwargs.get('dbfile') is None else kwargs.get('dbfile')

		if not is_encrypted(db):
			return_val = func(*args, **kwargs)
		else:
			print('Database is currently encrypted')
			return_val = 'ENCRYPTED'

		return return_val
	
	return checked_exec


@checker
def store_in_db(place: str, uname: str, pswd: str, dbfile: str) -> None:
	db = sqlite3.connect(dbfile)
	sh = db.cursor()

	sh.execute('''
				CREATE TABLE IF NOT EXISTS pswds(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
				username TEXT, place TEXT, password TEXT)
			''')
	sh.execute(f'INSERT INTO pswds(place, password, username) VALUES ("{place}", "{pswd}", "{uname}")')
	
	db.commit()
	print('Successfully updated.......')


@checker
def fetch_from_db(place: str | None, uname: str | None, show_pass: bool,  dbfile: str) -> List[tuple]:
	db = sqlite3.connect(dbfile)
	sh = db.cursor()
	to_fetch = 'place, username' + show_pass * ', password'
	headers = (head.capitalize() for head in to_fetch.split(', '))

	if place == '':
		place = None
	if uname == '':
		uname = None

	if uname is None and place is None:
		sh.execute(f'SELECT {to_fetch} FROM pswds')
	elif uname is None:
		sh.execute(f'SELECT {to_fetch} FROM pswds WHERE place="{place}"')
	elif place is None:
		sh.execute(f'SELECT {to_fetch} FROM pswds WHERE username="{uname}"')
	else:
		sh.execute(f'SELECT {to_fetch} FROM pswds WHERE place="{place}" AND username="{uname}"')

	data = sh.fetchall()
	if data:
		print(tabulate(data, headers, tablefmt='grid'))
	else:
		print('Nothing Found with', bool(place) * f'place={place}', bool(uname) * f'uname={uname}')

	return data


if __name__ == '__main__':
	parser = ArgumentParser(prog='dbman', description='Stores and Retrieves password data from database')
	parser.add_argument('--store', nargs=2,
						help='Store place, username (order matters)',
						metavar=('place', 'username'))
	
	def fetch_type(x):
		if x.strip('=').count('=') == 1:
			return x.split('=')
		else:
			raise ArgumentTypeError('Expected argument in key=value format')
		
	class store_fetch_values(Action):
		def __call__(self, parser: ArgumentParser, namespace: Namespace, values: str | Sequence[Any] | None, option_string: str | None = None) -> None:
			if values == []:
				setattr(namespace, self.dest, [[None, None]])
			else:
				setattr(namespace, self.dest, values)

	parser.add_argument('--fetch', nargs='*', metavar=('place=', 'uname='), type=fetch_type, action=store_fetch_values,
						help='Fetch data corresponding to a place and/or a username, supplied as key=value')
	parser.add_argument('--hide', action='store_true', help='Option to hide passwords')
	args = parser.parse_args()

	if args.store:
		if (pswd := getpass('Password to store: ')) == getpass('Confirm password: '):
			store_in_db(*args.store, pswd=pswd, dbfile=DB)
		else:
			print('Confirm password and password do not match')
			print('Nothing was stored...')
	if args.fetch:
		inp = {'place': None, 'uname': None}
		for x, y in args.fetch:
			if x in inp:
				inp[x] = y

		fetch_from_db(**inp, show_pass=not args.hide, dbfile=DB)