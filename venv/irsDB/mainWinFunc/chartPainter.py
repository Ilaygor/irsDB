#отрисовка графиков протоколов
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QCategoryAxis, QValueAxis
from PyQt5.QtCore import QPoint, QPointF
from PyQt5.Qt import QPen, QFont, Qt, QSize
from PyQt5.QtGui import QColor, QBrush, QPainter, QMouseEvent
import struct
from mainWinFunc.models import *
import numpy as np

def initChart(self, seamId):
    #получение данных
    seam = Seam.get(Seam.id == seamId)
    duration = 2
    fraqency = 10
    weldingTime = 2.0
    storchSpeed = struct.unpack('%sf' % (len(seam.torchSpeed) // 4), seam.torchSpeed)
    scurrent = struct.unpack('%sf' % (len(seam.current) // 4), seam.current)
    svoltage = struct.unpack('%sf' % (len(seam.voltage) // 4), seam.voltage)
    svoltageCorrection = [0, 0, 0]  # struct.unpack('%sf' % (len(seam.voltageCorrection)//4), seam.voltageCorrection)
    swireSpeed = struct.unpack('%sf' % (len(seam.wireSpeed) // 4), seam.wireSpeed)
    sgasConsumption = [0, 0, 0]  # struct.unpack('%sf' % (len(seam.gasConsumption)//4), seam.gasConsumption)
    # print("svoltage",svoltage)

    # вывод данных на график
    # рассчётные значения
    wireCC = QLineSeries()
    wireCC.setName("Расчётный расход проволоки")
    gasCC = QLineSeries()
    gasCC.setName("Расчётный расход газа")
    # реальные показатели
    # обявления
    torchSpeed = QLineSeries()
    torchSpeed.setName("Скорость сварки")
    current = QLineSeries()
    current.setName("Ток")
    voltage = QLineSeries()
    voltage.setName("Напряжение")
    voltageCorrection = QLineSeries()
    voltageCorrection.setName("Коррекция U")
    wireSpeed = QLineSeries()
    wireSpeed.setName("Скорость подачи проволоки")
    gasConsumption = QLineSeries()
    gasConsumption.setName("Расход газа")

    wireDelta = QLineSeries()
    wireDelta.setName("Перерасход проволоки")
    gasDelta = QLineSeries()
    gasDelta.setName("Перерасход газа")

    # цвета
    pen = QPen(QColor(150, 10, 10))
    pen.setWidth(3)
    gasCC.setPen(pen)
    pen = QPen(QColor(10, 10, 255))
    pen.setWidth(3)
    wireCC.setPen(pen)
    pen = QPen(QColor(10, 255, 10))
    pen.setWidth(3)
    torchSpeed.setPen(pen)
    pen = QPen(QColor(255, 10, 10))
    pen.setWidth(3)
    current.setPen(pen)
    pen = QPen(QColor(255, 10, 255))
    pen.setWidth(3)
    voltage.setPen(pen)
    pen = QPen(QColor(255, 255, 10))
    pen.setWidth(3)
    voltageCorrection.setPen(pen)
    pen = QPen(QColor(10, 10, 10))
    pen.setWidth(3)
    wireSpeed.setPen(pen)
    pen = QPen(QColor(10, 120, 10))
    pen.setWidth(3)
    gasConsumption.setPen(pen)

    pen = QPen(QColor(10, 120, 120))
    pen.setWidth(3)
    wireDelta.setPen(pen)
    pen = QPen(QColor(120, 10, 10))
    pen.setWidth(3)
    gasDelta.setPen(pen)

    # данные
    processTime = np.linspace(0, seam.period * (len(storchSpeed) - 1), len(storchSpeed))
    z = zip(processTime, storchSpeed, scurrent, svoltage, svoltageCorrection, swireSpeed, sgasConsumption)
    for time, volt, cur, trchs, wires in zip(processTime, svoltage, scurrent, storchSpeed, swireSpeed):
        voltage.append(time, volt)
        current.append(time, cur)
        wireSpeed.append(time, wires)
        torchSpeed.append(time, trchs)

    # легенды
    self.chart = QChart()
    self.chart.setAcceptHoverEvents(True)
    self.chart.legend().setVisible(True)
    self.chart.legend().setAlignment(Qt.AlignBottom)

    axisX = QValueAxis()
    axisX.setLabelFormat("%f")
    axisX.setTitleText("Время")
    self.chart.addAxis(axisX, Qt.AlignBottom)

    axisYgas = QValueAxis()
    axisYgas.setLabelFormat("%.2f")
    axisYgas.setTitleText("Газ [л/мин]")
    self.chart.addAxis(axisYgas, Qt.AlignLeft)

    axisYwire = QValueAxis()
    axisYwire.setLabelFormat("%.2f")
    axisYwire.setTitleText("Проволока [м/мин]")
    self.chart.addAxis(axisYwire, Qt.AlignLeft)
    axisYwire.setMax(round(max(swireSpeed)) + 1)
    axisYwire.setTickInterval(1)

    axisYcur = QValueAxis()
    axisYcur.setLabelFormat("%.2f")
    axisYcur.setTitleText("Ток [А]")
    axisYcur.setMax(max(scurrent) // 10 * 10 + 10)
    axisYcur.setTickInterval(50)

    axisYu = QValueAxis()
    axisYu.setLabelFormat("%.2f")
    axisYu.setTitleText("Напряжение [В]")
    axisYu.setMax(max(svoltage) // 10 * 10 + 10)
    axisYu.setTickInterval(20)

    axisYtorchSp = QValueAxis()
    axisYtorchSp.setLabelFormat("%.2f")
    axisYtorchSp.setTitleText("Скорость сварки [см/мин]")
    axisYtorchSp.setMax(max(storchSpeed) // 10 * 10 + 10)
    axisYtorchSp.setTickInterval(20)

    axisYcorU = QValueAxis()
    axisYcorU.setLabelFormat("%.2f")
    axisYcorU.setTitleText("Коррекция U [В]")

    # вывод на график
    if self.wireSpeedchb.checkState():
        self.chart.addSeries(wireSpeed)
        wireSpeed.attachAxis(axisX)
        wireSpeed.attachAxis(axisYwire)
    if self.gasConsumptionchb.checkState():
        self.chart.addSeries(gasConsumption)
        gasConsumption.attachAxis(axisX)
        gasConsumption.attachAxis(axisYgas)
    if self.torchSpeedchb.checkState():
        self.chart.addSeries(torchSpeed)
        self.chart.addAxis(axisYtorchSp, Qt.AlignLeft)
        torchSpeed.attachAxis(axisX)
        torchSpeed.attachAxis(axisYtorchSp)
    if self.currentchb.checkState():
        self.chart.addSeries(current)
        self.chart.addAxis(axisYcur, Qt.AlignLeft)
        current.attachAxis(axisX)
        current.attachAxis(axisYcur)
    if self.voltagechb.checkState():
        self.chart.addSeries(voltage)
        self.chart.addAxis(axisYu, Qt.AlignLeft)
        voltage.attachAxis(axisX)
        voltage.attachAxis(axisYu)
    if self.voltageCorrectionchb.checkState():
        self.chart.addSeries(voltageCorrection)
        self.chart.addAxis(axisYcorU, Qt.AlignLeft)
        voltageCorrection.attachAxis(axisX)
        voltageCorrection.attachAxis(axisYcorU)
    if self.wireCCchb.checkState():
        self.chart.addSeries(wireCC)
        wireCC.attachAxis(axisYwire)
        wireCC.attachAxis(axisX)
    if self.gasCCchb.checkState():
        self.chart.addSeries(gasCC)
        gasCC.attachAxis(axisX)
        gasCC.attachAxis(axisYgas)

    if seam.connId is not None:
        for x, wire, gas in zip(processTime, swireSpeed, sgasConsumption):
            wireDelta.append(x, wire - seam.connId.wireConsumption)
            gasDelta.append(x, gas - seam.connId.shieldingGasConsumption)
        if self.wireDeltaChb.checkState():
            self.chart.addSeries(wireDelta)
            wireDelta.attachAxis(axisX)
            wireDelta.attachAxis(axisYwire)
        if self.gasDeltaChb.checkState():
            self.chart.addSeries(gasDelta)
            gasDelta.attachAxis(axisX)
            gasDelta.attachAxis(axisYgas)

    font = QFont('Open Sans')
    font.setPixelSize(14)
    self.chart.setTitleFont(font)
    self.chart.setTitle('Параметры сварки')

    self.graph.setRenderHint(QPainter.Antialiasing)
    self.graph.setChart(self.chart)
    return len(storchSpeed), swireSpeed, sgasConsumption
####################################