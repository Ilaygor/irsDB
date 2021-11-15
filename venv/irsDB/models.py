import sqlite3
from peewee import *

db = SqliteDatabase("IRSwelding.db")

class BaseModel(Model):
    id = PrimaryKeyField(unique=True)
    class Meta:
        database = db
        order_by = 'id'


class User(BaseModel):
    login = CharField(null=False, unique=True)
    name = CharField()
    passWord = CharField(null=False)
    accessUser = BooleanField(default = True)
    accessDetail = BooleanField(default = True)
    accessConn = BooleanField(default = True)
    accessProt = BooleanField(default = True)
    accessArch = BooleanField(default = True)
    accessAdd = BooleanField(default = True)
    accessRemove = BooleanField(default = True)

    class Meta:
        db_table = 'Users'



class Detail(BaseModel):
    blueprinNumber = IntegerField()
    detailName = CharField()
    materialGrade = CharField()
    img = BlobField()
    weldingProgram = CharField()
    #weldingConnectionID = [] # а может и не нужен
    processingTime = DoubleField()

    class Meta:
        db_table = 'Details'

class Connection(BaseModel):
    ctype = CharField()
    thicknessOfElement1 = DoubleField()
    thicknessOfElement1 = DoubleField()
    jointBevelling = CharField()
    jointBevellingImg = BlobField()
    seamDimensions = CharField()
    fillerWireMark = CharField()
    fillerWireDiam = DoubleField()
    wireConsumption = DoubleField()
    shieldingGasType = CharField()
    shieldingGasConsumption = DoubleField()
    programmName = CharField()
    weldingTime = DoubleField()

    class Meta:
        db_table = 'Connections'

class Seam(BaseModel):
    connId = ForeignKeyField(Detail)
    detailId = ForeignKeyField(Connection)
    batchNumber = IntegerField()
    detailNumber = IntegerField()
    authorizedUser = CharField()
    weldingProgram = CharField()
    startTime = DateTimeField()
    endTime = DateTimeField()
    endStatus = BooleanField()
    torchTpeed = BlobField()
    burnerOscillation = BlobField()
    current = BlobField()
    voltage = BlobField()
    voltageCorrection = BlobField()
    wireSpeed = BlobField()
    gasConsumption = BlobField()

    class Meta:
        db_table = 'Seams'

