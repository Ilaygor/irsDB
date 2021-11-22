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
    name = CharField(null=True)
    passWord = CharField(null=False)
    accessUser = BooleanField(default = False)
    accessDetail = BooleanField(default = False)
    accessConn = BooleanField(default = False)
    accessProt = BooleanField(default = False)
    accessArch = BooleanField(default = False)
    accessAdd = BooleanField(default = False)
    accessRemove = BooleanField(default = False)

    class Meta:
        db_table = 'Users'

class Detail(BaseModel):
    blueprinNumber = IntegerField()
    detailName = CharField()
    materialGrade = CharField()
    img = BlobField(default = None, null=True)
    weldingProgram = CharField()
    #weldingConnectionID = [] # а может и не нужен
    processingTime = DoubleField()

    class Meta:
        db_table = 'Details'

class Connection(BaseModel):
    ctype = CharField()
    thicknessOfElement1 = DoubleField()
    thicknessOfElement2 = DoubleField()
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
    endStatus = BooleanField(default = b'0')
    torchSpeed = BlobField(default = b'0')
    burnerOscillation = BlobField(default = b'0')
    current = BlobField(default = b'0')
    voltage = BlobField(default = b'0')
    voltageCorrection = BlobField(default = b'0')
    wireSpeed = BlobField(default = b'0')
    gasConsumption = BlobField(default = b'0')

    class Meta:
        db_table = 'Seams'

