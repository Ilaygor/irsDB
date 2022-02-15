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
"""import time
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

st = time.time()"""
"""
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from models import Seam, Detail
import struct
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker
import numpy as np
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label
import byteimgs as bi
from io import BytesIO

import time
########################################################################
class PageNumCanvas(canvas.Canvas):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        #
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    # ----------------------------------------------------------------------
    def showPage(self):
        
        self.pages.append(dict(self.__dict__))
        self._startPage()

    # ----------------------------------------------------------------------
    def save(self):
        #Add the page number to each page (page x of y)
        page_count = len(self.pages)

        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)

    # ----------------------------------------------------------------------
    def draw_page_number(self, page_count):
        
        #Add the page number
        page = "Страница %s из %s" % (self._pageNumber, page_count)
        self.setFont('DejaVuSans', 9)
        self.drawRightString(195 * mm, 5 * mm, page)
        self.drawCentredString(100 * mm, 5 * mm, "www.irobs.ru")
        self.drawString(10 * mm, 5 * mm, "+7 (800) 777-02-01")


# ----------------------------------------------------------------------



def addSeam(seam, styles):
    addSeamTable(seam, styles)
    storchSpeed = struct.unpack('%sf' % (len(seam.torchSpeed) // 4), seam.torchSpeed)
    scurrent = struct.unpack('%sf' % (len(seam.current) // 4), seam.current)
    svoltage = struct.unpack('%sf' % (len(seam.voltage) // 4), seam.voltage)
    swireSpeed = struct.unpack('%sf' % (len(seam.wireSpeed) // 4), seam.wireSpeed)
    addChart(storchSpeed, "Скорость горелки", "Скорость горелки [см/мин]")
    addChart(scurrent, "Ток источника", "Ток источника [А]")
    addChart(svoltage, "Напряжение источника", "Напряжение источника [В]")
    addChart(swireSpeed, "Расход проволоки", "Расход проволоки [см/мин]")


def addChart(values, name, yAxesName):
    drawing = Drawing(5, 200)
    len(values)
    np.linspace(0,len(values)/10,len(values))
    dataVal = [(1,1),(2,2)]
    if len(values) > 2:
        dataVal = []
        for time,val in zip(np.linspace(0,20,200), values):
            print(time,val)
            dataVal.append((time,val))
    data = [
        dataVal
    ]
    lp = LinePlot()
    lp.x = 0
    lp.y = 50
    lp.height = 125
    lp.width = 450
    lp.data = data
    lp.joinedLines = 1
    lp.strokeColor = colors.black
    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.labelTextFormat = '%2.1f'
    drawing.add(lp)

    laby = Label()
    laby.setOrigin(-30, 125)
    laby.fontName = 'DejaVuSans'
    laby.angle = 90
    laby.dx = 0
    laby.dy = -20
    laby.setText(yAxesName)
    drawing.add(laby)

    labx = Label()
    labx.setOrigin(210, 45)
    labx.fontName = 'DejaVuSans'
    labx.angle = 0
    labx.dx = 0
    labx.dy = -20
    labx.setText("Время [с]")
    drawing.add(labx)

    labt = Label()
    labt.setOrigin(210, 205)
    labt.fontName = 'DejaVuSans'
    labt.angle = 0
    labt.dx = 0
    labt.dy = -20
    labt.setText(name)
    drawing.add(labt)
    return drawing


def addSeamTable(seam,styles):
    data = [("Тип соединения", seam.connId.ctype if seam.connId else "Не присвоено"),
            ("Чертёж", seam.detailId.detailName if seam.detailId else "Не присвоено"),
            ("Оборудование", seam.equipmentId.name if seam.equipmentId else "Не присвоено"),
            ("Партия", str(seam.batchNumber)),
            ("Номер в партии", str(seam.detailNumber)),
            ("Авторизованный пользователь", seam.authorizedUser.name if seam.authorizedUser else "Не присвоено"),
            ("Программа сварки", str(seam.weldingProgram)),
            ("Время начала", str(seam.startTime)),
            ("Время окончания", str(seam.endTime)),
            ("Стату окончания", "Успешно" if seam.endStatus == 1 else "У вас тут ошибочка"),
            ("Тип колебаний", str(seam.burnerOscillation.oscName)),
            ("Расч. расход газа", str(seam.connId)+" л/мин"),
            ("Расч. расход проволки", str(seam.connId)+" см/мин"),
            ("Период снятия", str(seam.period)+" c")
            ]
    table = Table(data, colWidths=200, rowHeights=15)
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.7, colors.black),
                               ("FONTNAME", (0, 0), (-1, -1), 'DejaVuSans')]))
    return table


def addDetTable(det,styles):
    data = [("Номер чертежа", det.blueprinNumber if det else "Не присвоено"),
            ("Название детали", det.detailName if det else "Не присвоено"),
            ("Марка материала", det.materialGrade if det else "Не присвоено"),
            ("Программа сварки", det.weldingProgram if det else "Не присвоено"),
            ("рассчётное время сварки", det.processingTime if det else "Не присвоено")
            ]
    table = Table(data, colWidths=200, rowHeights=15)
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.7, colors.black),
                               ("FONTNAME", (0, 0), (-1, -1), 'DejaVuSans')]))
    return table


def createMultiPage():
    pdfmetrics.registerFont(TTFont('DejaVuSans', "DejaVuSansCondensed.ttf"))
    doc = SimpleDocTemplate("отчёт репортлаб.pdf", pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=54, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='russ', fontName = 'DejaVuSans', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='russMain', fontName='DejaVuSans', alignment=TA_CENTER, fontSize = 16, spaceAfter = 10))

    Story = []

    Story.append(Paragraph("Отчёт
                        C отсюда и до туда", styles["russMain"]))
    det = Detail.select()[0]
    Story.append(addDetTable(det, styles))
    Story.append(Spacer(0,5))
    detImg = bi.unzip(det.img)
    stream = BytesIO(detImg[-1])
    im = Image(stream,200,200)
    Story.append(im)

    Story.append(PageBreak())
    for seam in Seam.select():

        # Create return address
        storchSpeed = struct.unpack('%sf' % (len(seam.torchSpeed) // 4), seam.torchSpeed)
        scurrent = struct.unpack('%sf' % (len(seam.current) // 4), seam.current)
        svoltage = struct.unpack('%sf' % (len(seam.voltage) // 4), seam.voltage)
        swireSpeed = struct.unpack('%sf' % (len(seam.wireSpeed) // 4), seam.wireSpeed)
        Story.append(addSeamTable(seam, styles))
        Story.append(addChart(storchSpeed, "Скорость горелки", "Скорость горелки [см/мин]"))
        Story.append(addChart(scurrent, "Ток источника", "Ток источника [А]"))
        Story.append(addChart(svoltage, "Напряжение источника", "Напряжение источника [В]"))
        Story.append(addChart(swireSpeed, "Расход проволоки", "Расход проволоки [см/мин]"))
        Story.append(PageBreak())

    doc.build(Story, canvasmaker=PageNumCanvas)

pyinstaller --onefile --icon=IRS256.ico main.py --name IRS
# ----------------------------------------------------------------------
if __name__ == "__main__":
    createMultiPage()"""
from models import *
import archivate as arc
import os
import time
if __name__ == "__main__":
    size = os.path.getsize("D:/irsDB/venv/irsDB/IRSwelding.db")
    print(size//1000000)
    a = arc.Archivator("IRSwelding.db")
    a.arch("test","D:/irsDB/venv/irsDB/backup")
    a.autoarch()
    time.sleep(5)
    """dellId = 2
    dellDetConns = DetConn.select().where(DetConn.connId == dellId)
    for dellDetConn in dellDetConns:
        dellDetConn.delete_instance()"""
