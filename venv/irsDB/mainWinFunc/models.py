import sqlite3
from peewee import *

db = SqliteDatabase("IRSwelding.db")
#db = SqliteDatabase("test/IRSwelding3.db")

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
    accessEquipment = BooleanField(default=False)
    accessOscilationType = BooleanField(default=False)

    class Meta:
        db_table = 'Users'

class Detail(BaseModel):
    blueprinNumber = CharField()
    detailName = CharField()
    materialGrade = CharField()
    img = BlobField(default = b'\x00\x00\x00\x00', null=True)
    weldingProgram = CharField()
    #weldingConnectionID = [] # а может и не нужен
    processingTime = DateTimeField()

    class Meta:
        db_table = 'Details'

class Connection(BaseModel):
    ctype = CharField()
    thicknessOfElement = CharField()
    jointBevelling = CharField()
    jointBevellingImg = BlobField(default = b'\x00\x00\x00\x00')
    seamDimensions = CharField()
    fillerWireMark = CharField()
    fillerWireDiam = CharField()
    wireConsumption = DoubleField()
    wireMassConsumption = DoubleField()
    shieldingGasType = CharField()
    shieldingGasConsumption = DoubleField()
    programmName = CharField()
    weldingTime = DateTimeField()
    preferredPeriod = DoubleField(default = 0.1)


    class Meta:
        db_table = 'Connections'

class Equipment(BaseModel):
    serialNumber = CharField()
    name = CharField()
    model = CharField()
    ip = CharField()
    port = IntegerField()
    period = DoubleField(default=0.1)

class OscilationType(BaseModel):
    oscName = CharField()
    oscNumber = IntegerField()
    oscImg = BlobField(default = b'\x00\x00\x00\x00')

class Batch(BaseModel):
    batchNumber = CharField()  # заменить
    detailId = ForeignKeyField(Detail, null=True) #blueprintId

class RealDetail(BaseModel):
    batchNumber = CharField()
    detailNumber = CharField()  # заменить
    detailId = ForeignKeyField(Detail, null=True)

class Seam(BaseModel):
    connId = ForeignKeyField(Connection, null=True)
    detailId = ForeignKeyField(Detail, null=True)
    equipmentId = ForeignKeyField(Equipment, null=True)#
    batchNumber = CharField(null=True)
    detailNumber = CharField(null=True)
    authorizedUser = ForeignKeyField(User, null=True)#
    weldingProgram = CharField()#
    startTime = DateTimeField()#
    endTime = DateTimeField()#
    endStatus = IntegerField(default = 0)#
    torchSpeed = BlobField(default = b'0')#
    burnerOscillation = ForeignKeyField(OscilationType, null=True)
    current = BlobField(default = b'0')#
    voltage = BlobField(default = b'0')#
    voltageCorrection = BlobField(default = b'0')
    wireSpeed = BlobField(default = b'0')#
    gasConsumption = BlobField(default = b'0')
    period = DoubleField(default=0.1)#
    realDetId = ForeignKeyField(RealDetail, null=True)

    class Meta:
        db_table = 'Seams'

class DetConn(BaseModel):
    connId = ForeignKeyField(Connection)
    detailId = ForeignKeyField(Detail)








