from playhouse.migrate import *
from mainWinFunc.models import *


def migration300522():
    my_db = User._meta.database
    migrator = SqliteMigrator(my_db)    #создание мигратора с  указанием БД
    try:
        RealDetail.create_table()  #создать таблицу реальных деталей
        wireMassConsumption_field = DoubleField(default = 0)    #создание полей
        realDetailID_field = IntegerField(null=True)

        migrate(
            migrator.add_column('Seams', 'realDetId_id', realDetailID_field),
            migrator.add_column('Connections', 'wireMassConsumption', wireMassConsumption_field),
        )

        seams = Seam.select()
        newDet = []
        for seam in seams:
            print(seam.batchNumber, seam.detailNumber, seam.detailId)
            if seam.batchNumber != "" and seam.detailNumber != "":
                newDet.append((seam.batchNumber, seam.detailNumber,seam.detailId))
        newDet = list(dict.fromkeys(newDet))
        for det in newDet:
            RealDetail.create(batchNumber = det[0], detailNumber = det[1], detailId = det[2])
        rdet = RealDetail.select()
        for det in rdet:
            seams2 = Seam.select().where(Seam.batchNumber == det.batchNumber, Seam.detailNumber == det.detailNumber)
            print("det:",det)
            for seam in seams2:
                print("det:",det," seam:",seam)
                query = Seam.update(realDetId = det.id).where(
                        Seam.id == seam.id)
                query.execute()
        print("БД обновлена")
    except:
        pass

if __name__ == "__main__":
    db = SqliteDatabase("test/IRSwelding1.db")
    User._meta.database = db
    Detail._meta.database = db
    Connection._meta.database = db
    Equipment._meta.database = db
    OscilationType._meta.database = db
    Seam._meta.database = db
    DetConn._meta.database = db
    RealDetail._meta.database = db
    migration300522()
    pass

