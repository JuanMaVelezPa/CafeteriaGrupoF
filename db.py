import sqlite3
from sqlite3 import Error
from flask import g

<<<<<<< HEAD
def get_db():
    try:
        if "db" not in g:
            g.db = sqlite3.connect("cafeteria.db")
=======
def get_db():#Conecta base de datos
    try:
        if 'db' not in g:
            g.db = sqlite3.connect('cafeteria.db')
>>>>>>> master
            return g.db
    except Error:
        print(Error)

<<<<<<< HEAD
def close_db():
    db = db.pop("cafeteria.db")
    if db is not None:
        db.close()
=======
def close_db():#Desconecta base de datos
    db = g.pop('db',None)
    if db is not None:
        db.close()
>>>>>>> master
