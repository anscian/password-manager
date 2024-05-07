from support import DB_TEST, KEY_TEST
from support.encrypt_decrypt import is_encrypted, encrypt, decrypt, endec, read_data, write_data
from support.dbManage import store_in_db, fetch_from_db
import os
from pytest import raises

NO_FILE = os.path.join(os.path.dirname(__file__), './__nofileofthisname__.file')



# To test cryptography management, we assume is_encrypted as correct implementation except for the FileNotFound check done below
# This is because either it could be tested by either externally viewing the file or using the same lines of code in python that the function already carries
def test_is_encrypted():
    with raises(SystemExit):
        is_encrypted(NO_FILE)

    assert isinstance(is_encrypted(DB_TEST), bool)


# This decorator ensures nothing was changed after execution of a testing function
# We do all experiments on test database and test key in test utils directory
def retainer(func: callable) -> callable:
    def mod_func():
        content_dbfile = read_data(DB_TEST)
        content_keyfile = read_data(KEY_TEST)

        func()

        if read_data(DB_TEST) != content_dbfile:
            write_data(DB_TEST, content_dbfile)
        if read_data(KEY_TEST) != content_keyfile:
            write_data(KEY_TEST, content_keyfile)

    return mod_func


# Now, assuming now that is_encrypted is well enough to predict that its a SQLite interactable database or something else (thus, encrypted for us)
# Testing encrypt, decrypt and endec switch
@retainer
def test_encrypt_decrypt():
    with raises(SystemExit):
        decrypt(dbfile=NO_FILE, keyfile=KEY_TEST)
    with raises(SystemExit):
        decrypt(dbfile=DB_TEST, keyfile=NO_FILE)
    with raises(SystemExit):
        encrypt(dbfile=NO_FILE, keyfile=KEY_TEST, change_key=False)
    with raises(SystemExit):
        encrypt(dbfile=DB_TEST, keyfile=NO_FILE, change_key=False)
    with raises(SystemExit):
        endec(dbfile=NO_FILE, keyfile=KEY_TEST, change_key=False)
    with raises(SystemExit):
        endec(dbfile=DB_TEST, keyfile=NO_FILE, change_key=False)

    # Test Database is expected to be completely decrypted
    if flag := is_encrypted(DB_TEST):
        # Test decrypt
        decrypt(DB_TEST, KEY_TEST)
        assert flag is not is_encrypted(DB_TEST)
        # Test encrypt
        encrypt(DB_TEST, KEY_TEST, False)
        assert flag is is_encrypted(DB_TEST)
        # As by now its tested to work
        decrypt(DB_TEST, KEY_TEST)
    else:
        # Test encrypt
        encrypt(DB_TEST, KEY_TEST, False)
        assert flag is not is_encrypted(DB_TEST)
        # Test decrypt
        decrypt(DB_TEST, KEY_TEST)
        assert flag is is_encrypted(DB_TEST)

    # Test encrypt with key change
    key = read_data(KEY_TEST)
    encrypt(DB_TEST, KEY_TEST, True)
    assert is_encrypted(DB_TEST)
    assert key != read_data(KEY_TEST)

    # Testing endec
    # Encrypted Database
    endec(DB_TEST, KEY_TEST, False)
    assert not is_encrypted(DB_TEST)
    # Decrypted Database
    endec(DB_TEST, KEY_TEST, False)
    assert is_encrypted(DB_TEST)
    # Encrypted Database
    key = read_data(KEY_TEST)
    endec(DB_TEST, KEY_TEST, True)
    assert not is_encrypted(DB_TEST)
    assert key == read_data(KEY_TEST)
    # Decrypted Database
    key = read_data(KEY_TEST)
    endec(DB_TEST, KEY_TEST, True)
    assert is_encrypted(DB_TEST)
    assert key != read_data(KEY_TEST)



# Similarly, to test database management for storage and retrieval, we assume fetch_from_db is correct implementation except for the FileNotFound and more checks done below
# Again, this is because its testing requires externally viewing the database or using the same lines of code in python that were used to make the function
@retainer
def test_fetch():
    with raises(SystemExit):
        fetch_from_db(None, None, True, NO_FILE)

    if not is_encrypted(DB_TEST):
        endec(DB_TEST, KEY_TEST, False)
    assert fetch_from_db(None, None, True, DB_TEST) == 'ENCRYPTED'

    endec(DB_TEST, KEY_TEST, False)
    data = fetch_from_db(None, None, True, DB_TEST) # Assumes already a presence of the table named pswds
    assert all(len(x) == 3 and all(isinstance(y, str) for y in x) for x in data)
    data = fetch_from_db(None, None, False, DB_TEST)
    assert all(len(x) == 2 and all(isinstance(y, str) for y in x) for x in data)


# Now, we need to get into testing store_in_db by believing in this fetch_from_db. Also, with a little fetch testing
@retainer
def test_store():
    entry = ('foo', 'bar', 'foo@bar')

    with raises(SystemExit):
        store_in_db(*entry, NO_FILE)

    if not is_encrypted(DB_TEST):
        endec(DB_TEST, KEY_TEST, False)
    assert store_in_db(*entry, DB_TEST) == 'ENCRYPTED'

    endec(DB_TEST, KEY_TEST, False)
    store_in_db(*entry, DB_TEST)

    for search in [(None, None), ('foo', None), (None, 'bar'), ('foo', 'bar')]:
        data = fetch_from_db(*search, True, DB_TEST)
        assert all(len(x) == 3 and all(isinstance(y, str) for y in x) for x in data) and entry in data
        data = fetch_from_db(*search, False, DB_TEST)
        assert all(len(x) == 2 and all(isinstance(y, str) for y in x) for x in data) and entry[:2] in data



# The main file manager.py is just a clui using these tested function internally. Thus, it doesn't require subtle testing like this.
# This is because if anything is bad in clui, we see it while running the manager.py script itself