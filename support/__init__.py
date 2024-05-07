from os import path

# Relative paths
db = './data/passwords.sqlite3'
key = './data/key.secret'
db_test = './test_utils/testdb.sqlite3'
key_test = './test_utils/testkey.secret'

BASE = path.dirname(path.dirname(__file__))

# Absolute paths
DB = path.join(BASE, db)
KEY = path.join(BASE, key)
DB_TEST = path.join(BASE, db_test)
KEY_TEST = path.join(BASE, key_test)

if __name__ == '__main__':
    print('DB: ' + DB, 'KEY: ' + KEY, 'DB_TEST: ' + DB_TEST, 'KEY_TEST: ' + KEY_TEST, sep='\n')