from cryptography.fernet import Fernet, InvalidToken
import sys
from argparse import ArgumentParser
from . import DB, KEY


def read_data(fname: str) -> bytes:
	with open(fname, 'rb') as f:
		return f.read()


def write_data(fname: str, content: bytes) -> None:
	with open(fname, 'wb') as f:
		f.write(content)


def is_encrypted(dbfile: str) -> bool:
	try:
		with open(dbfile, 'rb') as db:
			return db.read(6) != b'SQLite'
	except FileNotFoundError as ferr:
		sys.exit(f'File {ferr.filename} not found')
	except BaseException as err:
		raise err


def encrypt(dbfile: str, keyfile: str, change_key: bool) -> None:
	try:
		data = read_data(dbfile)

		if change_key:
			open(keyfile).close()
			key = Fernet.generate_key()
			write_data(dbfile, Fernet(key).encrypt(data))
			write_data(keyfile, key)
		else:
			key = read_data(keyfile)
			write_data(dbfile, Fernet(key).encrypt(data))
	except FileNotFoundError as ferr:
		sys.exit(f'File {ferr.filename} not found')
	except BaseException as err:
		raise err


def decrypt(dbfile: str, keyfile: str) -> None:
	try:
		data = read_data(dbfile)
		key = read_data(keyfile)

		write_data(dbfile, Fernet(key).decrypt(data))
	except FileNotFoundError as ferr:
		sys.exit(f'File {ferr.filename} not found')
	except InvalidToken:
		sys.exit('Wrong key has been used!!!')
	except BaseException as err:
		raise err


def endec(dbfile: str = DB, keyfile: str = KEY, change_key: bool = False) -> None:
	if is_encrypted(dbfile):
		decrypt(dbfile, keyfile)
	else:
		encrypt(dbfile, keyfile, change_key)


if __name__ == '__main__':
	parser = ArgumentParser(prog='endec', description='Encrypts and Decrypts password carrying database')
	parser.add_argument('-c', '--change', action='store_true', dest='change',
				   help='Whether or not to change the key while encrypting')
	args = parser.parse_args()

	endec(change_key=args.change)