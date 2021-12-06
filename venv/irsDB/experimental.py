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
"""def printit():
  threading.Timer(1.0, printit).start()
  print("Hello, World!")

printit()"""

"""l = [1.1, 2.2, 3.1, 4.2]
l3 = [2, 5, 5]
buf = struct.pack('%sf' % len(l), *l)
print(buf)
print(len(buf))
lenght = len(buf)/4

l2 = struct.unpack('%sf' % (len(buf)//4), buf)
print(l2)
"""
"""import struct

def unzip(c):
    par = struct.unpack('%si' % (c[0]+1), c[:4*(c[0]+1)])
    imgs = []
    start = 4*(c[0]+1)
    for img in par[1:]:
        imgs.append(c[start:start+img])
        start += img
    return imgs

def add(c, b):
    par = list(struct.unpack('%si' % (c[0] + 1), c[:4 * (c[0] + 1)]))
    data = c[4 * (c[0] + 1):] + b
    par[0]+=1
    par.append(len(b))
    print(par, data)
    buf = struct.pack('%si' % len(par), *par)
    return buf + data

def dell(c, i):
    par = list(struct.unpack('%si' % (c[0] + 1), c[:4 * (c[0] + 1)]))
    startDell = sum(par[1:1+i])
    imgLen = par.pop(i + 1)
    data = c[4 * (c[0] + 1):]
    newData = data[:startDell] + data[startDell+imgLen:]
    par[0] -= 1
    print(par, newData)
    buf = struct.pack('%si' % len(par), *par)
    return buf + newData



par = [0]
buf = struct.pack('%si' % len(par), *par)
cafe = bytes('café', encoding="utf_8")
car = bytes('car', encoding="utf_8")
c = buf
print(c)
c2 = add(c, car)
print(c2)
print(unzip(c2))
dell(c2, 0)"""


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
    detailId = None,#ForeignKeyField(Detail)
    batchNumber = 1,#IntegerField()
    detailNumber = 2,#IntegerField()
    authorizedUser = "user",#CharField()
    weldingProgram = "p2",#CharField()
    startTime = datetime.datetime.now(),#DateTimeField()
    endTime = datetime.datetime.now(),#DateTimeField()
    endStatus = True,#BooleanField()
    torchSpeed = btorchSpeed,#BlobField()
    burnerOscillation = bburnerOscillation,#BlobField()
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
    db.create_tables([Equipment, OscilationType])
    db.commit()
print(t.strftime("%H %M %S"))

#addSeam()








