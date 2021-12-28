"""import sys
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QPointF, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow

class ReleasePosEvent(QEvent):
    EventType = QEvent.Type(QEvent.registerEventType())
    def __init__(self, point):
        QEvent.__init__(self, ReleasePosEvent.EventType)
        self.point = point


class ChartView(QChartView):
    def mouseReleaseEvent(self, event):
        p1 = event.pos()
        p2 = self.mapToScene(p1)
        p3 = self.chart().mapFromScene(p2)
        p4 = self.chart().mapToValue(p3)
        if self.chart():
            for serie in self.chart().series():
                QApplication.postEvent(serie, ReleasePosEvent(p4))
        QChartView.mouseReleaseEvent(self, event)


class LineSeries(QLineSeries):
    def __init__(self, *args, **kwargs):
        QLineSeries.__init__(self, *args, **kwargs)
        self.start = QPointF()
        self.pressed.connect(self.on_pressed)

    def on_pressed(self, point):
        self.start = point
        print("on_pressed", point)

    def shift(self, delta):
        if not delta.isNull():
            for ix in range(self.count()):
                p = self.at(ix)
                p += delta
                self.replace(ix, p)

    def customEvent(self, event):
        if event.type() == ReleasePosEvent.EventType:
            if not self.start.isNull():
                dpoint = event.point - self.start
                self.shift(dpoint)
                self.start = QPointF()

app = QApplication(sys.argv)
series0 = LineSeries()

series0 << QPointF(1, 15) << QPointF(3, 17) << QPointF(7, 16) << QPointF(9, 17) \
        << QPointF(12, 16) << QPointF(16, 17) << QPointF(18, 15)

chart = QChart()
chart.addSeries(series0)
chart.createDefaultAxes()
chartView = ChartView(chart)

window = QMainWindow()
window.setCentralWidget(chartView)
window.resize(400, 300)
window.show()

sys.exit(app.exec_())"""
import threading
import struct
import random
from models import *
import datetime

def addSeam():
    torchSpeed = []
    burnerOscillation = []
    current = []
    voltage = []
    voltageCorrection = []
    wireSpeed = []
    gasConsumption = []
    for t in range(21):
        torchSpeed.append(random.uniform(0, 1.5))
        burnerOscillation.append(random.uniform(0, 10))
        current.append(random.uniform(5, 15))
        voltage.append(random.uniform(210,230))
        voltageCorrection.append(random.uniform(0, 15))
        wireSpeed.append(random.uniform(0, 30))
        gasConsumption.append(random.uniform(10, 25))

    btorchSpeed = struct.pack('%sf' % len(torchSpeed), *torchSpeed)
    bburnerOscillation = struct.pack('%sf' % len(burnerOscillation), *burnerOscillation)
    bcurrent = struct.pack('%sf' % len(current), *current)
    bvoltage = struct.pack('%sf' % len(voltage), *voltage)
    bvoltageCorrection = struct.pack('%sf' % len(voltageCorrection), *voltageCorrection)
    bwireSpeed = struct.pack('%sf' % len(wireSpeed), *wireSpeed)
    bgasConsumption = struct.pack('%sf' % len(gasConsumption), *gasConsumption)

    Seam(connId = None,#ForeignKeyField(Connection)
    detailId = 2,#ForeignKeyField(Detail)
    equipmentId = 1,
    batchNumber = 1,#CharField()
    detailNumber = 2,#CharField()
    authorizedUser = 4,#CharField()
    weldingProgram = "p2",#CharField()
    startTime = datetime.datetime.now(),#DateTimeField()
    endTime = datetime.datetime.now(),#DateTimeField()
    endStatus = True,#BooleanField()
    torchSpeed = btorchSpeed,#BlobField()
    burnerOscillation = 1,#BlobField()
    current = bcurrent,#BlobField()
    voltage = bvoltage,#BlobField()
    voltageCorrection = bvoltageCorrection,#BlobField()
    wireSpeed = bwireSpeed,#BlobField()
    gasConsumption = bgasConsumption#BlobField()
    ).save()
#             dell                 #
####################################
def dellSeam(dellId):
    dellSeam = Seam.get(Seam.id == dellId)
    dellSeam.delete_instance()

def dellConn(dellId):
    dellConnection = Connection.get(Connection.id == dellId)
    dellConnection.delete_instance()

def dellDetail(dellId):
    dellDetail = Detail.get(Detail.id == dellId)
    dellDetail.delete_instance()

def dellRealDetail(detN, detB):
    dellSeams = Seam.select().where(Seam.detailNumber == detN & Seam.batchNumber == detB)
    dellSeams.delete_instance()
####################################
t = datetime.time(0, 37, 15)
print(t)
with db:
    db.create_tables([Equipment])
    db.commit()
print(t.strftime("%H %M %S"))


#addSeam()
user = User.get()
print(user)









