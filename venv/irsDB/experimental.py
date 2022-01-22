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
"""import threading
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
    detailId = None,#ForeignKeyField(Detail)
    equipmentId = None,
    batchNumber = "",#CharField()
    detailNumber = "",#CharField()
    authorizedUser = None,#CharField()
    weldingProgram = "",#CharField()
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

def addSeam(torchSpeed,burnerOscillation,current,voltage,voltageCorrection,wireSpeed):
    gasConsumption = []

    btorchSpeed = struct.pack('%sf' % len(torchSpeed), *torchSpeed)
    bburnerOscillation = struct.pack('%sf' % len(burnerOscillation), *burnerOscillation)
    bcurrent = struct.pack('%sf' % len(current), *current)
    bvoltage = struct.pack('%sf' % len(voltage), *voltage)
    bvoltageCorrection = struct.pack('%sf' % len(voltageCorrection), *voltageCorrection)
    bwireSpeed = struct.pack('%sf' % len(wireSpeed), *wireSpeed)
    bgasConsumption = struct.pack('%sf' % len(gasConsumption), *gasConsumption)

    Seam(connId=None,  # ForeignKeyField(Connection)
         detailId=None,  # ForeignKeyField(Detail)
         equipmentId=None,
         batchNumber="",  # CharField()
         detailNumber="",  # CharField()
         authorizedUser=None,  # CharField()
         weldingProgram="",  # CharField()
         startTime=datetime.datetime.now(),  # DateTimeField()
         endTime=datetime.datetime.now(),  # DateTimeField()
         endStatus=True,  # BooleanField()
         torchSpeed=btorchSpeed,  # BlobField()
         burnerOscillation=1,  # BlobField()
         current=bcurrent,  # BlobField()
         voltage=bvoltage,  # BlobField()
         voltageCorrection=bvoltageCorrection,  # BlobField()
         wireSpeed=bwireSpeed,  # BlobField()
         gasConsumption=bgasConsumption  # BlobField()
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

import time
from opcua import Client, ua

class SubHandler(object):

    def __init__(self, Nodes, weldProg, eqwNum):
        self.volt = 0
        self.curr = 0
        self.speed = 0
        self.wireSpeed = 0
        self.arcStb = False
        self.period = 0
        self.times = []
        self.eqwNum = eqwNum

        self.weldingProgramm = weldProg
        self.errCode = 0

        self.startTime = None
        self.endTime = None

        self.voltMass = []
        self.currMass = []
        self.speedMass = []
        self.wireSpeedMass = []
        self.arcStbMass = []

        self.nodes = Nodes

    def datachange_notification(self, node, val, data):
        #print("dataChange", node, val)
        if node == self.nodes["ROB_Weld_Start"] and val:
            print("new seam")
            self.voltMass = []
            self.currMass = []
            self.speedMass = []
            self.wireSpeedMass = []
            self.startTime = time.time()
            self.times = []
            self.errCode = 0
        elif node == self.nodes["ROB_Weld_Start"] and not val:
            print("end seam")
            self.endTime = time.time()
            self.period = (self.times[-1]-self.times[0])/len(self.times)
            print("times", self.startTime, self.endTime, self.endTime - self.startTime)
            print("period", self.period)
            print("errCode", self.errCode)
            print("weldProg",self.weldingProgramm)
            print("eqwNum", self.eqwNum)
            print("volt",self.voltMass)
            print("curr",self.currMass)
            print("speed",self.speedMass)
            print("wire",self.wireSpeedMass)
            print(len(self.voltMass))
            #addSeam([],[],[],self.volt,[],[])
        elif node == self.nodes["PS_Weld_Voltage"]:
            self.volt = val
        elif node == self.nodes["PS_Weld_Current"]:
            self.curr = val
        elif node == self.nodes["ROB_Actual_Speed"]:
            self.speed = val
        elif node == self.nodes["PS_Wire_Feed"]:
            self.wireSpeed = val
        elif node == self.nodes["PS_Error_Number"]:
            self.errCode = val
        elif node == self.nodes["ROB_Job_Number"]:
            self.weldingProgramm = val
        elif node == self.nodes["PLC_time"]:
            self.voltMass.append(self.volt)
            self.currMass.append(self.curr)
            self.speedMass.append(self.speed)
            self.wireSpeedMass.append(self.wireSpeed)
            self.times.append(val)

    def event_notification(self, event):
        print("new event", event)

class DataHarvestr():
    #ActSeam = ActualSeam()

    def __init__(self, IP):
        self.IP = IP
        self.client = Client("opc.tcp://"+self.IP+":4840")
        self.client.connect()
        root = self.client.get_root_node()
        try:
            print("eqw",Equipment.get(Equipment.ip == self.IP).id)
            eqwNum = Equipment.get(Equipment.ip == self.IP).id
        except:
            eqwNum = None
        speedNode = root.get_child(["0:Objects", "2:ROB_DB", "2:ROB_Actual_Speed"])
        jobNumbNode = root.get_child(["0:Objects", "2:ROB_DB", "2:ROB_Job_Number"])
        wireSpeedNode = root.get_child(["0:Objects", "2:ROB_DB", "2:ROB_Wire_Speed"])
        processNode = root.get_child(["0:Objects", "2:ROB_DB", "2:ROB_Weld_Start"])

        processPsNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Process_Active"])
        voltPsNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Weld_Voltage"])
        currPsNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Weld_Current"])
        wirePsNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Wire_Feed"])
        errPsNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Error_Number"])
        arcStbNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Arc_Stable"])

        plcTimeNode = root.get_child(["0:Objects", "2:PLC_DB", "2:PLC_time"])




        Nodes = {"ROB_Actual_Speed":speedNode,
                 "ROB_Weld_Start":processNode,
                 "ROB_Job_Number":jobNumbNode,
                 "ROB_Wire_Speed":wireSpeedNode,
                 "ROB_Process_Active":processPsNode,
                 "PS_Weld_Voltage":voltPsNode,
                 "PS_Weld_Current":currPsNode,
                 "PS_Wire_Feed":wirePsNode,
                 "PS_Error_Number":errPsNode,
                 "PS_Arc_Stable":arcStbNode,
                 "PLC_time":plcTimeNode
                 }

        weldProg = jobNumbNode.get_value()
        handler = SubHandler(Nodes, weldProg, eqwNum)
        sub = self.client.create_subscription(100, handler)
        speedHandle = sub.subscribe_data_change(speedNode)
        processHandle = sub.subscribe_data_change(processNode)
        jobNumbHandle = sub.subscribe_data_change(jobNumbNode)
        wireSpeedNode = sub.subscribe_data_change(wireSpeedNode)

        processPsHandle = sub.subscribe_data_change(processPsNode)
        voltPsHandle = sub.subscribe_data_change(voltPsNode)
        currPsHandle = sub.subscribe_data_change(currPsNode)
        wirePsHandle = sub.subscribe_data_change(wirePsNode)
        errPsHandle = sub.subscribe_data_change(errPsNode)
        plcTimeHandle = sub.subscribe_data_change(plcTimeNode)

        arcStbHandle = sub.subscribe_data_change(arcStbNode)
"""
import time
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np

st = time.time()
# Создание файла.
pdf = PdfPages("Figures.pdf")

# Создание сюжетов и их сохранение.
FUNCTIONS = [np.sin, np.cos, np.sqrt, lambda x: x**2]
X = np.linspace(-5, 5, 100)
for function in FUNCTIONS:
    plt.plot(X, function(X))
    pdf.savefig()
    plt.close()


# Сохранение файла
pdf.close()
print("exp1", time.time() - st)

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np

st = time.time()




















