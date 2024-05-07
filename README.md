# Password Manager based on python
This is a simple tool to manage the passwords while also keeping them safe.

We have a main interaction file `/manager.py` which have interfaces for generation, storage and retrieval of password data. 

It is supported by python module `/support` in the same directory. It also generates a simple CLI to toy with the database.
> - `/encrypt_decrypt.py` : For locking and unlocking passwords database
> - `/dbManage.py` : For store and fetch operations on database

In `/data` directory the key `./key.secret` and the database `./passwords.sqlite3` are stored. For testing, other such pair is kept in `/test_utils` directory.

The `/manager.py` is designed in such a way that user can continuously store multiple data entries or continuously do searches. Also, if user wants an interaction with alternative store, fetch and generate, a descent **CLI** will be there. Also, whatsoever be the state of database before, after interaction with `/manager.py` is done, we get an encrypted database.

The usage helps for each of the following can be seen as follows:-
> -    First go to project root directory  :       `cd $PROJECT_ROOT`
> -    `/manager.py`                       :       `python3 ./manager.py --help`
> -    `/support/encrypt_decrypt.py`       :       `python3 -m support.encrypt_decrypt --help`
> -    `/support/dbManage.py`              :       `python3 -m support.dbManage --help`

The required libraries are given in `requirements.txt`. To download them while in **project root**, execute

    python3 -r ./requirements.txt

## Limitations:
Well as it's just a primary and simple system, there is very less protection of data though successful storage and retrieval
- The key is to be kept safe by the user. Access to keyfile will automatically allow someone to decrypt it if encryption is known.
- Damaging the encryted database file by modifying it may lead to permanent loss of data and same holds if keyfile is modified before decrypting.