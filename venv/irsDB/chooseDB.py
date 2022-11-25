# переключение активной БД
from peewee import *
from mainWinFunc.models import *
from zipfile import ZipFile
import os

print("cdb")

# создание временной разархивированной БД
def anzip(path):
    try:
        os.remove("tmp/IRSwelding.db")
    except: pass
    with ZipFile(path, 'r') as zipObj:
        zipObj.extractall(path="tmp/")

# Изменеие привявязок моделей к другой БД
def chooseDB(db):
    User._meta.database = db
    Detail._meta.database = db
    Connection._meta.database = db
    Equipment._meta.database = db
    OscilationType._meta.database = db
    Seam._meta.database = db
    DetConn._meta.database = db
    RealDetail._meta.database = db

def connToDb(path):
    db = SqliteDatabase(path)
    chooseDB(db)

def cooseArch(path):
    anzip(path)
    connToDb("tmp/IRSwelding.db")
    pass


if __name__ =="__main__":
    db = SqliteDatabase("IRSwelding1.db")
    print(OscilationType._meta.database)

    path = 'D:/irsDB/venv/irsDB/backup/2021_11_12_134841.zip'
    osc = OscilationType.select()

    for o in osc:
        print(o)

    anzip(path)