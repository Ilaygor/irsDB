from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem as twi
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QCategoryAxis, QValueAxis
from PyQt5.QtCore import QPoint, QPointF
from PyQt5.Qt import QPen, QFont, Qt, QSize
from PyQt5.QtGui import QColor, QBrush, QPainter, QMouseEvent
from PIL import Image, ImageQt
import pdfGenerator as pg
import numpy as np
from models import *
from GUI import *
from connWin import *
from selectUI import *
from timePdf import *
from settings import *
import sys
import datetime
from io import BytesIO
import byteimgs as bi
import struct
import archivate
import chooseDB as cdb
import os
import OPCclient as opcc

#pyuic5 -x base.ui -o gui.py

class UImodif(Ui_MainWindow):

    otype = ""
    imgs = b'\x00\x00\x00\x00'
    curImg = 0
    curId = 0
    AfUser = User.select()[0]
    A = archivate.Archivator("IRSwelding.db")
    isActualDB = True
    HarvestrDict = {}

    #инициализация функций нажатий
    def setupUi(self, MainWindow, app):
        super().setupUi(MainWindow)
        self.app = app
        #кнопки
        self.loginBtn.clicked.connect(self.login)
        self.addBtn.clicked.connect(self.add)
        self.saveChalenges.clicked.connect(self.saveDeteil)
        self.saveConn.clicked.connect(self.saveConnChlngs)
        #self.makePdf.clicked.connect(lambda: print("pdf"))
        self.saveBtn.clicked.connect(self.save)
        self.delBtn.clicked.connect(self.dell)
        self.addConnection.clicked.connect(lambda: MainWindow.addConnDia(self.curId))
        self.viewBlueprintBtn.clicked.connect(lambda: self.detailView(self.curId))
        self.choosePdfAdress.clicked.connect(self.adrForPdf)
        self.home.clicked.connect(lambda: self.initChart(self.curId))
        self.addSeamBtn.clicked.connect(lambda: MainWindow.addConnDia(self.curId))
        self.saveProtocolBtn.clicked.connect(self.saveProtocol)
        self.delSeamBtn.clicked.connect(self.delSeamFromDetail)
        self.createDetailPdf.clicked.connect(self.detReport)

        self.actionback.triggered.connect(self.backToTable)#lambda: self.redirect(4))

        #выбор данных шва
        self.chooseEqvipment.clicked.connect(lambda: MainWindow.chooseDataDia(self.curId, 'eqvipment'))
        self.chooseUser.clicked.connect(lambda: MainWindow.chooseDataDia(self.curId, 'user'))
        self.chooseBlueprint.clicked.connect(lambda: MainWindow.chooseDataDia(self.curId, 'blueprint'))
        self.chooseConn.clicked.connect(lambda: MainWindow.chooseDataDia(self.curId, 'connection'))


        # действия с изображениями
        self.addDetImg.clicked.connect(lambda: self.newImg(self.DetImg))
        self.prvDetImg.clicked.connect(lambda: self.veiwPrevImg(self.DetImg))
        self.nextDetImg.clicked.connect(lambda: self.veiwNextImg(self.DetImg))
        self.delDetImg.clicked.connect(lambda: self.delImg(self.DetImg))
        self.newConnImg.clicked.connect(lambda: self.newImg(self.connImg))
        self.prvConnImg.clicked.connect(lambda: self.veiwPrevImg(self.connImg))
        self.nextConnImg.clicked.connect(lambda: self.veiwNextImg(self.connImg))
        self.delConnImg.clicked.connect(lambda: self.delImg(self.connImg))


        #пункты меню
        self.exit.triggered.connect(self.exitf)
        self.detail.triggered.connect(lambda: self.adpanel("blueprint"))
        self.connections.triggered.connect(lambda: self.adpanel("connections"))
        self.realDetail.triggered.connect(lambda: self.adpanel("realDetail"))
        self.seams.triggered.connect(lambda: self.adpanel("seams"))
        self.users.triggered.connect(lambda: self.adpanel("user"))
        self.makeArch.triggered.connect(self.ar)
        self.chooseArch.triggered.connect(self.chArch)
        self.equipments.triggered.connect(lambda: self.adpanel("equipments"))
        self.timePdf.triggered.connect(MainWindow.timePdfDia)
        self.oscTypeTable.triggered.connect(lambda: self.adpanel("oscilation"))
        self.archSettings.triggered.connect(lambda: MainWindow.archSettings(self.A))
        self.returnToActualDB.triggered.connect(self.returnToActual)



        self.tableWidget.doubleClicked.connect(self.doubleClick)


        #перерисовка графика
        self.graph.setRubberBand(QChartView.HorizontalRubberBand)
        self.wireCCchb.stateChanged.connect(lambda: self.initChart(self.curId))
        self.gasCCchb.stateChanged.connect(lambda: self.initChart(self.curId))
        self.torchSpeedchb.stateChanged.connect(lambda: self.initChart(self.curId))
        self.currentchb.stateChanged.connect(lambda: self.initChart(self.curId))
        self.voltagechb.stateChanged.connect(lambda: self.initChart(self.curId))
        self.voltageCorrectionchb.stateChanged.connect(lambda: self.initChart(self.curId))
        self.wireSpeedchb.stateChanged.connect(lambda: self.initChart(self.curId))
        self.gasConsumptionchb.stateChanged.connect(lambda: self.initChart(self.curId))
        self.gasDeltaChb.stateChanged.connect(lambda: self.initChart(self.curId))
        self.wireDeltaChb.stateChanged.connect(lambda: self.initChart(self.curId))



        self.lineEdit_2.hide()
        self.pushButton_12.hide()
        self.gasDeltaChb.hide()
        self.gasConsumptionchb.hide()
        self.voltageCorrectionchb.hide()


    #######Область тестовых функций########
    def backToTable(self):
        self.toolBar.hide()
        self.adpanel(self.otype)

    def detReport(self):
        batch = self.batchNumber_2.text()
        det = self.numberInBatch.text()
        adress = self.pdfAdress.text()
        print(batch, det, adress)
        pg.create_pdf(adress,batch,det)


    def saveProtocol(self):
        if self.curId < 1:
            try:
                pass  # DoubleField()
            except:
                print("не создано")
        else:
            query = Seam.update(
                batchNumber = self.batchNumber.text(),
                detailNumber = self.detailNumber.text(),
                startTime = datetime.datetime.strptime(self.startTime.text(), "%d.%m.%Y %H:%M:%S"),
                endTime = datetime.datetime.strptime(self.endTime.text(), "%d.%m.%Y %H:%M:%S"),
                endStatus = self.endStatus.isChecked(),
                burnerOscillation = OscilationType.get(OscilationType.oscName == self.oscType.currentText()).id,
                period = self.seamPeriod.value()).where(
                Seam.id == self.curId)  # DoubleField()
            query.execute()
            self.protocolView(self.curId)

    def delSeamFromDetail(self):
        addInd = []
        for ind in self.seamTable.selectedIndexes():
            if ind.row() not in addInd:
                addInd.append(ind.row())
        for ind in addInd:
            print(self.seamTable.item(ind, 0).text())
            query = Seam.update(
                batchNumber="",
                detailNumber="").where(
                Seam.id == int(self.seamTable.item(ind, 0).text()))
            query.execute()

    def exitf(self):
        self.AfUser = None
        self.menubar.hide()
        self.toolBar.hide()
        self.HarvestrDict = {}
        self.redirect(1)

    def ar(self):
        self.A.arch('User_s reqvest')

    def chArch(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(filter = '*.zip')[0]
        print(filename)
        cdb.cooseArch(filename)
        self.statusBar.showMessage("Переклёчен на архив: "+filename, 3000)
        self.isActualDB = False

    def returnToActual(self):
        cdb.connToDb("IRSwelding.db")
        try:
            os.remove("tmp/IRSwelding.db")
        except:
            pass
        self.statusBar.showMessage("Переклёчен на актуальную бд", 3000)
        self.isActualDB = True

    def adrForPdf(self):
        filename = QtWidgets.QFileDialog.getExistingDirectory()
        print(filename)
        self.pdfAdress.setText(filename)

    def create_pdf(self):
        adr = self.ui.adress.text()
        if adr != "":
            pg.createPdf(adr)


    ###########################################

    # Удаление, добавление редактирование данных
    def save (self):
        if self.otype == "user":
            self.saveUser()
            self.userTable()
        if self.otype == "equipments":
            self.saveEquipment()
            self.equipmentTable()
        if self.otype == "oscilation":
            self.saveOscilation()
            self.oscilationTable()

    def saveUser(self):
        for i in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(i, 0) is None or self.tableWidget.item(i, 0).text() == "":
                if (self.tableWidget.item(i, 1) is not None and
                    self.tableWidget.item(i,2) is not None and
                    self.tableWidget.item(i, 3) is not None):
                    print(self.tableWidget.cellWidget(i, 4).isChecked())
                    try:
                        User(login=self.tableWidget.item(i, 1).text(),
                             name=self.tableWidget.item(i, 2).text(),
                             passWord=self.tableWidget.item(i, 3).text(),
                             accessUser=self.tableWidget.cellWidget(i, 4).isChecked(),
                             accessDetail=self.tableWidget.cellWidget(i, 5).isChecked(),
                             accessConn=self.tableWidget.cellWidget(i, 6).isChecked(),
                             accessProt=self.tableWidget.cellWidget(i, 7).isChecked(),
                             accessArch=self.tableWidget.cellWidget(i, 8).isChecked(),
                             accessAdd=self.tableWidget.cellWidget(i, 9).isChecked(),
                             accessRemove=self.tableWidget.cellWidget(i, 10).isChecked(),
                             accessEquipment = self.tableWidget.cellWidget(i, 11).isChecked(),
                             accessOscilationType = self.tableWidget.cellWidget(i, 12).isChecked()
                             ).save()
                    except:
                        print("не создано")
                elif self.tableWidget.item(i, 1) != "" and self.tableWidget.item(i, 2) != "" and self.tableWidget.item(i, 3) != "":
                    pass
            else:
                id = int(self.tableWidget.item(i, 0).text())
                query = User.update(login=self.tableWidget.item(i, 1).text(),
                             name=self.tableWidget.item(i, 2).text(),
                             passWord=self.tableWidget.item(i, 3).text(),
                             accessUser=self.tableWidget.cellWidget(i, 4).isChecked(),
                             accessDetail=self.tableWidget.cellWidget(i, 5).isChecked(),
                             accessConn=self.tableWidget.cellWidget(i, 6).isChecked(),
                             accessProt=self.tableWidget.cellWidget(i, 7).isChecked(),
                             accessArch=self.tableWidget.cellWidget(i, 8).isChecked(),
                             accessAdd=self.tableWidget.cellWidget(i, 9).isChecked(),
                             accessRemove=self.tableWidget.cellWidget(i, 10).isChecked(),
                             accessEquipment = self.tableWidget.cellWidget(i, 11).isChecked(),
                             accessOscilationType = self.tableWidget.cellWidget(i, 12).isChecked()
                             ).where(
                    User.id == id)  # DoubleField()
                query.execute()
        self.statusBar.showMessage("Данные сохранены", 3000)

    def saveEquipment(self):
        for i in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(i, 0) is None or self.tableWidget.item(i, 0).text() == "":
                try:
                    Equipment(
                    serialNumber = self.tableWidget.item(i, 1).text(),
                    name = self.tableWidget.item(i, 2).text(),
                    model = self.tableWidget.item(i, 3).text(),
                    ip = self.tableWidget.item(i, 4).text(),
                    port = self.tableWidget.cellWidget(i, 5).value(),
                    period = self.tableWidget.cellWidget(i, 6).value()).save()
                except:
                    pass
            else:
                try:
                    id = int(self.tableWidget.item(i, 0).text())
                    query = Equipment.update(
                    serialNumber = self.tableWidget.item(i, 1).text(),
                    name = self.tableWidget.item(i, 2).text(),
                    model = self.tableWidget.item(i, 3).text(),
                    ip = self.tableWidget.item(i, 4).text(),
                    port = self.tableWidget.cellWidget(i, 5).value(),
                    period = self.tableWidget.cellWidget(i, 6).value()).where(Equipment.id == id)
                    query.execute()
                except:
                    pass
        self.statusBar.showMessage("Данные сохранены", 3000)

    def saveOscilation(self):
        for i in range(self.tableWidget.rowCount()):
            pixmap = self.tableWidget.cellWidget(i, 3).pixmap()
            ba = QtCore.QByteArray()
            buff = QtCore.QBuffer(ba)
            buff.open(QtCore.QIODevice.WriteOnly)
            try:
                ok = pixmap.save(buff, "PNG")
            except: pass
            #assert ok
            pixmap_bytes = ba.data()
            print(type(pixmap_bytes))
            if self.tableWidget.item(i, 0) is None or self.tableWidget.item(i, 0).text() == "":
                try:
                    OscilationType(
                    oscNumber = int(self.tableWidget.item(i, 1).text()),
                    oscName = self.tableWidget.item(i, 2).text(),
                    oscImg = pixmap_bytes).save()
                except: pass
            else:
                try:
                    id = int(self.tableWidget.item(i, 0).text())
                    query = OscilationType.update(
                        oscNumber=int(self.tableWidget.item(i, 1).text()),
                        oscName=self.tableWidget.item(i, 2).text(),
                        oscImg=pixmap_bytes).where(OscilationType.id == id)
                    query.execute()
                except: pass
        self.statusBar.showMessage("Данные сохранены", 3000)

    def add(self):
        self.imgs = b'\x00\x00\x00\x00'
        self.curId = 0
        self.clearForms()
        if self.otype == "user":
            i =  self.tableWidget.rowCount()
            self.tableWidget.insertRow(i)
            self.tableWidget.setCellWidget(i, 4, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 5, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 6, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 7, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 8, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 9, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 10, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 11, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 12, QtWidgets.QCheckBox())
        elif self.otype == "blueprint":
            self.redirect(2)
            #self.detailView(3)
        elif self.otype == "connections":
            self.redirect(3)
            #self.ConnView(1)
        elif self.otype == "realDetail":
            self.redirect(5)
        elif self.otype == "seams":
            pass
        elif self.otype == "equipments":
            i = self.tableWidget.rowCount()
            self.tableWidget.insertRow(i)
            self.tableWidget.setCellWidget(i, 5, QtWidgets.QSpinBox())
            self.tableWidget.cellWidget(i, 5).setMaximum(65535)
            self.tableWidget.cellWidget(i, 5).setValue(4840)
            self.tableWidget.setCellWidget(i, 6, QtWidgets.QDoubleSpinBox())
        elif self.otype == "oscilation":
            i = self.tableWidget.rowCount()
            self.tableWidget.insertRow(i)
            self.tableWidget.setCellWidget(i, 3, QtWidgets.QLabel())

    def doubleClick(self):
        self.imgs = b'\x00\x00\x00\x00'
        if self.tableWidget.currentRow() >= 0: #and self.tableWidget.item(self.tableWidget.currentRow(), 0) is not None
            if self.tableWidget.item(self.tableWidget.currentRow(), 0) is not None:
                id = int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())
                self.curId = id
            else:
                self.curId = None

            if self.otype == "blueprint":
                self.detailView(id)
            elif self.otype == "connections":
                self.ConnView(id)
            elif self.otype == "realDetail":
                self.realDetailView()
            elif self.otype == "seams":
                self.protocolView(id)
            elif self.otype == "oscilation" and self.tableWidget.currentColumn() == 3:
                try:
                    filename = QtWidgets.QFileDialog.getOpenFileName(filter = '(*.png *.jpg *.bmp)')[0]
                    self.tableWidget.cellWidget(self.tableWidget.currentRow(), 3).setText(filename)
                    f = QtGui.QPixmap(filename)
                    self.tableWidget.cellWidget(self.tableWidget.currentRow(), 3).setPixmap(f.scaled(75,75))
                except: pass


        # отрисовка графиков протоколов

    def dell(self):
        if self.tableWidget.currentRow() >= 0 and self.tableWidget.item(self.tableWidget.currentRow(), 0) is not None:
            try:
                dellId = int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())
            except: pass
            if self.otype == "user":
                query = Seam.update(authorizedUser=None).where(Seam.authorizedUser == dellId)
                query.execute()
                dellUser = User.get(User.id == dellId)
                dellUser.delete_instance()
                print("dell")
                self.userTable()
            elif self.otype == "blueprint":
                query = Seam.update(detailId=None).where(Seam.detailId == dellId)
                query.execute()
                try:
                    dellDetConn = DetConn.select().where(DetConn.connId  == dellId)
                    dellDetConn.delete_instance()
                except: pass
                try:
                    dellDetail = Detail.get(Detail.id == dellId)
                    dellDetail.delete_instance()
                except:pass
                self.detailTable()
            elif self.otype == "connections":
                try:
                    query = Seam.update(connId=None).where(connId.detailId == dellId)
                    query.execute()
                except:pass
                try:
                    dellDetConn = DetConn.select().where(DetConn.connId == dellId)
                    dellDetConn.delete_instance()
                except: pass
                dellConnection = Connection.get(Connection.id == dellId)
                dellConnection.delete_instance()
                self.connectTable()
            elif self.otype == "equipments":
                query = Seam.update(equipmentId=None).where(Seam.equipmentId == dellId)
                query.execute()
                dellEquipment = Equipment.get(Equipment.id == dellId)
                dellEquipment.delete_instance()
                self.equipmentTable()
            elif self.otype == "oscilation":
                query = Seam.update(burnerOscillation=None).where(Seam.burnerOscillation == dellId)
                query.execute()
                dellOscilationType = OscilationType.get(OscilationType.id == dellId)
                dellOscilationType.delete_instance()
                self.oscilationTable()
            elif self.otype == "seams":
                dellOscilationType = Seam.get(Seam.id == dellId)
                dellOscilationType.delete_instance()
                self.veiwSeamTable()
            elif self.otype == "realDetail":
                try:
                    delDeteil = int(self.tableWidget.item(self.tableWidget.currentRow(), 4).text())
                    delBatch = int(self.tableWidget.item(self.tableWidget.currentRow(), 3).text())
                except:
                    pass
                print("dell", delDeteil, delBatch)
                query = Seam.update(
                    batchNumber="",
                    detailNumber="").where(
                    Seam.batchNumber == delBatch and Seam.detailNumber == delDeteil)
                query.execute()
                self.realDetailTable()


    def initChart(self, seamId):
            # 7+3(2)#получение данных
            seam = Seam.get(Seam.id == seamId)
            duration = 2
            fraqency = 10
            weldingTime = 2.0
            storchSpeed = struct.unpack('%sf' % (len(seam.torchSpeed)//4), seam.torchSpeed)
            scurrent = struct.unpack('%sf' % (len(seam.current)//4), seam.current)
            svoltage = struct.unpack('%sf' % (len(seam.voltage)//4), seam.voltage)
            svoltageCorrection = [0,0,0]#struct.unpack('%sf' % (len(seam.voltageCorrection)//4), seam.voltageCorrection)
            swireSpeed = struct.unpack('%sf' % (len(seam.wireSpeed)//4), seam.wireSpeed)
            sgasConsumption = [0,0,0]# struct.unpack('%sf' % (len(seam.gasConsumption)//4), seam.gasConsumption)
            print("svoltage",svoltage)

            # вывод данных на график
            # рассчётные значения
            wireCC = QLineSeries()
            wireCC.setName("Расчётный расход проволоки")
            gasCC = QLineSeries()
            gasCC.setName("Расчётный расход газа")
            # реальные показатели
            # обявления
            torchSpeed = QLineSeries()
            torchSpeed.setName("Скорость горелки")
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
            processTime = np.linspace(0, seam.period *len(storchSpeed), len(storchSpeed)+1)
            z = zip(processTime, storchSpeed, scurrent, svoltage, svoltageCorrection, swireSpeed, sgasConsumption)
            """for x, y3, y5, y6, y7, y8, y9 in zip(storchSpeed, scurrent, svoltage, svoltageCorrection, swireSpeed, sgasConsumption,processTime):
                torchSpeed.append(x, y3)
                current.append(x, y5)
                voltage.append(x, y6)
                print(x, y6)
                voltageCorrection.append(x, y7)
                wireSpeed.append(x, y8)
                gasConsumption.append(x, y9)"""
            for time, volt, cur, trchs, wires  in zip(processTime, svoltage,scurrent,storchSpeed,swireSpeed):
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

            axisYcur = QValueAxis()
            axisYcur.setLabelFormat("%.2f")
            axisYcur.setTitleText("Ток [А]")

            axisYu = QValueAxis()
            axisYu.setLabelFormat("%.2f")
            axisYu.setTitleText("Напряжение [В]")

            axisYtorchSp = QValueAxis()
            axisYtorchSp.setLabelFormat("%.2f")
            axisYtorchSp.setTitleText("Скорость горелки [см/мин]")

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
            if self.wireCCchb.checkState():
                self.chart.addSeries(wireCC)
                wireCC.attachAxis(axisYwire)
                wireCC.attachAxis(axisX)
            if self.gasCCchb.checkState():
                self.chart.addSeries(gasCC)
                gasCC.attachAxis(axisX)
                gasCC.attachAxis(axisYgas)
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

            if seam.connId is not None:
                for x, wire,gas in zip(processTime, swireSpeed, sgasConsumption):
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

    # временная функция
    def redirect(self, n):
        imgs = b'\x00\x00\x00\x00'
        self.stackedWidget.setCurrentIndex(n)
    #Отображение данных в спец формах
    def realDetailView(self):
        self.stackedWidget.setCurrentIndex(5)
        self.toolBar.show()
        butchN = self.tableWidget.item(self.tableWidget.currentRow(), 3).text()
        detailN = self.tableWidget.item(self.tableWidget.currentRow(), 4).text()
        print(butchN, detailN)
        details = Seam.select().join(Detail).where(Seam.batchNumber == butchN, Seam.detailNumber == detailN)
        self.batchNumber_2.setText(butchN)
        self.numberInBatch.setText(detailN)
        self.curId = 1
        self.seamTable.setRowCount(len(details))

        self.seamTable.setColumnCount(4)
        self.seamTable.setHorizontalHeaderLabels(
            ["id","Тип", "Начало", "Окончание"])
        for i in range(len(details)):
            self.seamTable.setItem(i, 0, twi(str(details[i].id)))
            self.seamTable.setItem(i, 1, twi(str(details[i].connId)))
            self.seamTable.setItem(i, 2, twi(str(details[i].startTime)))
            self.seamTable.setItem(i, 3, twi(str(details[i].endTime)))
        self.seamTable.hideColumn(0)
        self.seamTable.resizeColumnsToContents()

        self.imgs = details[0].detailId.img
        self.curImg = 0
        self.veiwImg(self.dateilImg)



    def protocolView(self, id):
        self.stackedWidget.setCurrentIndex(0)
        self.toolBar.show()
        seam = Seam.get(Seam.id == id)
        print("its work", seam)
        try:
            eqv = Equipment.get(Equipment.id == seam.equipmentId)
            self.serialNumber.setText(eqv.serialNumber)
            self.eqvName.setText(eqv.name)
            self.eqvModel.setText(eqv.model)
            self.eqvIPadress.setText(eqv.ip)
            self.eqvPort.setText(str(eqv.port))
        except:
            self.serialNumber.setText("")
            self.eqvName.setText("")
            self.eqvModel.setText("")
            self.eqvIPadress.setText("")
            self.eqvPort.setText("")
        self.weldingProgram_2.setText(seam.weldingProgram)
        try:
            conn = Connection.get(Connection.id == seam.connId)
            self.connId_2.setText(conn.ctype)
        except:
            self.connId_2.setText("")
        try:
            det = Detail.get(Detail.id == seam.detailId)
            self.detailId.setText(det.detailName)
        except:
            self.detailId.setText("")
        self.batchNumber.setText(str(seam.batchNumber))
        self.detailNumber.setText(str(seam.detailNumber))
        try:
            user = User.get(User.id == seam.authorizedUser)
            self.authorizedUser.setText(user.name)
        except:
            self.authorizedUser.setText("")
        self.startTime.setDateTime(seam.startTime)
        self.endTime.setDateTime(seam.endTime)
        self.endStatus.setCheckState(
            QtCore.Qt.Unchecked if seam.endStatus else QtCore.Qt.Checked)
        self.seamPeriod.setValue(seam.period)
        oscs = OscilationType.select()
        self.oscType.clear()
        for osc in oscs:
            self.oscType.addItem(osc.oscName)
        datalenght, swireSpeed, sgasConsumption = self.initChart(id)
        GasCons = round(sum(sgasConsumption) * seam.period / 60, 3)
        WireCons = round(sum(swireSpeed) * seam.period/60, 1)
        if seam.connId is None:
            self.gasDelta.setText("Нет данных")#str(GasCons)+" литров")
            self.wireDelta.setText(str(WireCons)+" м (реальный расход)")
        else:
            conn = Connection.get(Connection.id == seam.connId)
            t = datetime.datetime.strptime(conn.weldingTime, "%H:%M:%S")
            delta = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            print(delta.total_seconds())
            WireCons -= (conn.wireConsumption/60*delta.total_seconds())
            GasCons = round(conn.shieldingGasConsumption/60 * datalenght * seam.period,3)
            self.gasDelta.setText(str(GasCons) + " литров")
            self.wireDelta.setText(str(WireCons) + " м")

    def detailView(self, id):
        self.stackedWidget.setCurrentIndex(2)
        self.toolBar.show()
        detail = Detail.get(Detail.id == id)
        self.blueprinNumber.setText(str(detail.blueprinNumber))
        self.detailName.setText(detail.detailName)
        self.materialGrade.setText(detail.materialGrade)
        self.weldingProgram.setText(detail.weldingProgram)
        #self.processingTime.setValue(detail.processingTime)

        time = detail.processingTime.split(":")
        #print(time)
        self.HprocessingTime.setValue(int(time[0]))
        self.MprocessingTime.setValue(int(time[1]))
        self.SprocessingTime.setValue(int(time[2]))
        self.imgs = detail.img
        #print(bi.unzip(self.imgs))
        #detImg = bi.unzip(self.imgs)
        self.curImg = 0
        self.veiwImg(self.DetImg)
        detCons = DetConn.select().where(DetConn.detailId == id)
        self.detailsConnections_2.setColumnCount(2)
        self.detailsConnections_2.setHorizontalHeaderLabels(
            ["id", "Вид соединения"])
        self.detailsConnections_2.setRowCount(len(detCons))
        for i in range(len(detCons)):
            self.detailsConnections_2.setItem(i, 0, twi(str(detCons[i].id)))
            self.detailsConnections_2.setItem(i, 1, twi(str(detCons[i].connId.ctype)))
        self.detailsConnections_2.hideColumn(0)
        self.detailsConnections_2.resizeColumnsToContents()

    def ConnView(self, id):
        self.stackedWidget.setCurrentIndex(3)
        self.toolBar.show()
        connection = Connection.get(Connection.id == id)
        self.connId.setText(str(connection.id))
        self.ctype.setText(connection.ctype)
        self.thicknessOfElement.setText(connection.thicknessOfElement)
        self.jointBevelling.setText(connection.jointBevelling)
        self.seamDimensions.setText(connection.seamDimensions)
        self.fillerWireMark.setText(connection.fillerWireMark)
        self.fillerWireDiam.setText(connection.fillerWireDiam)
        self.wireConsumption.setValue(connection.wireConsumption)
        self.shieldingGasType.setText(connection.shieldingGasType)
        self.shieldingGasConsumption.setValue(connection.shieldingGasConsumption)
        self.programmName.setText(connection.programmName)
        time = connection.weldingTime.split(":")
        self.HweldingTime.setValue(int(time[0]))
        self.MweldingTime.setValue(int(time[1]))
        self.SweldingTime.setValue(int(time[2]))
        self.preferredPeriod.setValue(connection.preferredPeriod)
        self.imgs = connection.jointBevellingImg
        self.curImg = 0
        self.veiwImg(self.connImg)

    def clearForms(self):
        """self.connId_2.setText("")
        self.detailId.setText("")
        self.batchNumber.setText("")
        self.detailNumber.setText("")
        self.authorizedUser.setText("")
        self.weldingProgram_2.setText("")
        self.startTime.setText("")
        self.endTime.setText("")
        self.endStatus.setCheckState(QtCore.Qt.Unchecked)"""
        self.blueprinNumber.setText("")
        self.detailName.setText("")
        self.materialGrade.setText("")
        self.weldingProgram.setText("")
        self.HprocessingTime.setValue(0)
        self.MprocessingTime.setValue(0)
        self.SprocessingTime.setValue(0)
        self.detailsConnections_2.clear()

        #self.processingTime.setValue(0)
        self.veiwImg(self.DetImg)
        self.veiwImg(self.connImg)
        self.connId.setText("")
        self.ctype.setText("")
        self.thicknessOfElement.setText("")
        self.jointBevelling.setText("")
        self.seamDimensions.setText("")
        self.fillerWireMark.setText("")
        self.fillerWireDiam.setText("")
        self.wireConsumption.setValue(0)
        self.shieldingGasType.setText("")
        self.shieldingGasConsumption.setValue(0)
        self.programmName.setText("")
        self.HweldingTime.setValue(0)
        self.MweldingTime.setValue(0)
        self.SweldingTime.setValue(0)
        self.preferredPeriod.setValue(0.1)

        self.batchNumber_2.setText("")
        self.numberInBatch.setText("")
        self.blueprintName.setText("")
        self.seamTable.clear()


    #####################################

    # Функции работы с изображениями
    def newImg(self, label):
        filename = QtWidgets.QFileDialog.getOpenFileName(filter = '(*.png *.jpg *.bmp)')[0]
        f = open(filename, 'rb')
        d = f.read()
        self.imgs = bi.add(self.imgs, d)
        stream = BytesIO(d)
        im = Image.open(stream).convert("RGBA")
        stream.close()
        data = im.tobytes("raw", "BGRA")
        qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_ARGB32)
        pix = QtGui.QPixmap.fromImage(qim)
        label.setPixmap(pix.scaled(900, int(900*im.size[1]/im.size[0])))

    def veiwNextImg(self, label):
        self.curImg += 1
        self.veiwImg(label)

    def veiwPrevImg(self, label):
        self.curImg -= 1
        self.veiwImg(label)

    def delImg(self, label):
        self.imgs = bi.dell(self.imgs, self.curImg)
        self.curImg = 0
        self.veiwImg(label)

    def veiwImg(self, label):
        detImg = bi.unzip(self.imgs)
        if len(detImg) > 0:
            if self.curImg > len(detImg) - 1:
                self.curImg = len(detImg) - 1
            elif self.curImg < 0:
                self.curImg = 0
            stream = BytesIO(detImg[self.curImg])
            im = Image.open(stream).convert("RGBA")
            stream.close()
            data = im.tobytes("raw", "BGRA")
            qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_ARGB32)
            pix = QtGui.QPixmap.fromImage(qim)
            label.setPixmap(pix.scaled(900, int(900*im.size[1]/im.size[0])))
        else:
            label.clear()
            #self.DetImg.clear()
    #########################################

    #авторизация
    def login(self):
        print(self.loginFld.text(), self.passFld.text())
        try:
            user = User.get(User.login == self.loginFld.text())
            if user.passWord == self.passFld.text():
                self.stackedWidget.setCurrentIndex(4)
                self.menubar.show()

                self.AfUser = user
                self.adpanel("blueprint")

                self.users.setEnabled(user.accessUser)

                self.delDetImg.setEnabled(user.accessDetail)
                self.addDetImg.setEnabled(user.accessDetail)
                self.blueprinNumber.setEnabled(user.accessDetail)
                self.detailName.setEnabled(user.accessDetail)
                self.materialGrade.setEnabled(user.accessDetail)
                self.weldingProgram.setEnabled(user.accessDetail)
                self.addConnection.setEnabled(user.accessDetail)
                self.saveChalenges.setEnabled(user.accessDetail)
                self.HprocessingTime.setEnabled(user.accessDetail)
                self.MprocessingTime.setEnabled(user.accessDetail)
                self.SprocessingTime.setEnabled(user.accessDetail)

                self.connId.setEnabled(user.accessConn)
                self.ctype.setEnabled(user.accessConn)
                self.thicknessOfElement.setEnabled(user.accessConn)
                self.jointBevelling.setEnabled(user.accessConn)
                self.seamDimensions.setEnabled(user.accessConn)
                self.fillerWireMark.setEnabled(user.accessConn)
                self.fillerWireDiam.setEnabled(user.accessConn)
                self.wireConsumption.setEnabled(user.accessConn)
                self.shieldingGasType.setEnabled(user.accessConn)
                self.shieldingGasConsumption.setEnabled(user.accessConn)
                self.programmName.setEnabled(user.accessConn)
                self.HweldingTime.setEnabled(user.accessConn)
                self.MweldingTime.setEnabled(user.accessConn)
                self.SweldingTime.setEnabled(user.accessConn)
                self.saveConn.setEnabled(user.accessConn)
                self.delConnImg.setEnabled(user.accessConn)
                self.newConnImg.setEnabled(user.accessConn)
                self.preferredPeriod.setEnabled(user.accessConn)

                self.chooseEqvipment.setEnabled(user.accessProt)
                self.batchNumber.setEnabled(user.accessProt)
                self.detailNumber.setEnabled(user.accessProt)
                self.startTime.setEnabled(user.accessProt)
                self.endTime.setEnabled(user.accessProt)
                self.endStatus.setEnabled(user.accessProt)
                self.oscType.setEnabled(user.accessProt)
                self.seamPeriod.setEnabled(user.accessProt)
                self.chooseUser.setEnabled(user.accessProt)
                self.chooseBlueprint.setEnabled(user.accessProt)
                self.chooseConn.setEnabled(user.accessProt)

                self.addBtn.setEnabled(user.accessAdd)

                self.delBtn.setEnabled(user.accessRemove)

                """for eqw in Equipment.select():
                    print(eqw.ip)
                    try:
                        opcc.DataHarvestr(eqw.ip)
                    except:
                        print(eqw.ip, "blat")"""

            else:
                self.statusBar.showMessage("Неверный пароль", 4000)
        except:
            self.statusBar.showMessage("Логин не зарегистрирован", 4000)

    def makeEnable(self):
        self.adpanel("blueprint")

        self.users.setEnabled(self.AfUser.accessUser)

        self.delDetImg.setEnabled(self.AfUser.accessDetail)
        self.addDetImg.setEnabled(self.AfUser.accessDetail)
        self.blueprinNumber.setEnabled(self.AfUser.accessDetail)
        self.detailName.setEnabled(self.AfUser.accessDetail)
        self.materialGrade.setEnabled(self.AfUser.accessDetail)
        self.weldingProgram.setEnabled(self.AfUser.accessDetail)
        self.addConnection.setEnabled(self.AfUser.accessDetail)
        self.saveChalenges.setEnabled(self.AfUser.accessDetail)
        self.HprocessingTime.setEnabled(self.AfUser.accessDetail)
        self.MprocessingTime.setEnabled(self.AfUser.accessDetail)
        self.SprocessingTime.setEnabled(self.AfUser.accessDetail)

        self.connId.setEnabled(self.AfUser.accessConn)
        self.ctype.setEnabled(self.AfUser.accessConn)
        self.thicknessOfElement.setEnabled(self.AfUser.accessConn)
        self.jointBevelling.setEnabled(self.AfUser.accessConn)
        self.seamDimensions.setEnabled(self.AfUser.accessConn)
        self.fillerWireMark.setEnabled(self.AfUser.accessConn)
        self.fillerWireDiam.setEnabled(self.AfUser.accessConn)
        self.wireConsumption.setEnabled(self.AfUser.accessConn)
        self.shieldingGasType.setEnabled(self.AfUser.accessConn)
        self.shieldingGasConsumption.setEnabled(self.AfUser.accessConn)
        self.programmName.setEnabled(self.AfUser.accessConn)
        self.HweldingTime.setEnabled(self.AfUser.accessConn)
        self.MweldingTime.setEnabled(self.AfUser.accessConn)
        self.SweldingTime.setEnabled(self.AfUser.accessConn)
        self.saveConn.setEnabled(self.AfUser.accessConn)
        self.delConnImg.setEnabled(self.AfUser.accessConn)
        self.newConnImg.setEnabled(self.AfUser.accessConn)
        self.preferredPeriod.setEnabled(self.AfUser.accessConn)

        self.chooseEqvipment.setEnabled(self.AfUser.accessProt)
        self.batchNumber.setEnabled(self.AfUser.accessProt)
        self.detailNumber.setEnabled(self.AfUser.accessProt)
        self.startTime.setEnabled(self.AfUser.accessProt)
        self.endTime.setEnabled(self.AfUser.accessProt)
        self.endStatus.setEnabled(self.AfUser.accessProt)
        self.oscType.setEnabled(self.AfUser.accessProt)
        self.seamPeriod.setEnabled(self.AfUser.accessProt)
        self.chooseUser.setEnabled(self.AfUser.accessProt)
        self.chooseBlueprint.setEnabled(self.AfUser.accessProt)
        self.chooseConn.setEnabled(self.AfUser.accessProt)

        self.addBtn.setEnabled(self.AfUser.accessAdd)

        self.delBtn.setEnabled(self.AfUser.accessRemove)
    #####################################

    #save
    def saveDeteil(self):
        if self.curId < 1:
            try:
                det = Detail(blueprinNumber = self.blueprinNumber.text(),
                detailName = self.detailName.text(),
                materialGrade = self.materialGrade.text(),
                weldingProgram = self.weldingProgram.text(),
                processingTime = datetime.time(self.HprocessingTime.value(), self.MprocessingTime.value(), self.SprocessingTime.value()),
                img = self.imgs)
                det.save()
                self.curId = det.id
            except:
                print("не создано")
        else:
            query = Detail.update(blueprinNumber = int(self.blueprinNumber.text()),
                detailName = self.detailName.text(),
                materialGrade = self.materialGrade.text(),
                weldingProgram = self.weldingProgram.text(),
                processingTime = datetime.time(self.HprocessingTime.value(), self.MprocessingTime.value(), self.SprocessingTime.value()),
                img = self.imgs).where(Detail.id == self.curId)
            query.execute()
        self.adpanel("blueprint")
        return self.curId

    def saveConnChlngs(self):
        print("save conn")
        if self.curId < 1:
            try:
                Connection(ctype = self.ctype.text(),#CharField()
                thicknessOfElement = self.thicknessOfElement.text(),
                jointBevelling = self.jointBevelling.text(),#CharField()
                jointBevellingImg = self.imgs,#BlobField()
                seamDimensions = self.seamDimensions.text(),#CharField()
                fillerWireMark = self.fillerWireMark.text(),#CharField()
                fillerWireDiam = self.fillerWireDiam.text(),#DoubleField()
                wireConsumption = float(self.wireConsumption.text().replace(',','.')),#DoubleField()
                shieldingGasType = self.shieldingGasType.text(),#CharField()
                shieldingGasConsumption = float(self.shieldingGasConsumption.text().replace(',','.')),#DoubleField()
                programmName = self.programmName.text(),#CharField()
                weldingTime = datetime.time(self.HweldingTime.value(), self.MweldingTime.value(), self.SweldingTime.value()),
                preferredPeriod = self.preferredPeriod.value()).save()#DoubleField()
            except:
                print("не создано")
        else:
            query = Connection.update(ctype = self.ctype.text(),#CharField()
                thicknessOfElement = self.thicknessOfElement.text(),
                jointBevelling = self.jointBevelling.text(),#CharField()
                jointBevellingImg = self.imgs,#BlobField()
                seamDimensions = self.seamDimensions.text(),#CharField()
                fillerWireMark = self.fillerWireMark.text(),#CharField()
                fillerWireDiam = float(self.fillerWireDiam.text().replace(',','.')),#DoubleField()
                wireConsumption = float(self.wireConsumption.text().replace(',','.')),#DoubleField()
                shieldingGasType = self.shieldingGasType.text(),#CharField()
                shieldingGasConsumption = float(self.shieldingGasConsumption.text().replace(',','.')),#DoubleField()
                programmName = self.programmName.text(),#CharField()
                weldingTime = datetime.time(self.HweldingTime.value(), self.MweldingTime.value(), self.SweldingTime.value()),
                preferredPeriod = self.preferredPeriod.value()).where(
                Connection.id == self.curId)  # DoubleField()
            query.execute()
        self.adpanel("connections")
    #####################################

    #Функции вывода таблиц данных
    #Панель администрирования данных
    def adpanel(self, otype):
        self.otype = otype
        self.toolBar.hide()
        self.tableWidget.clear()
        self.saveBtn.setEnabled(True)
        if self.otype == "user":
            try:
                self.saveBtn.setEnabled(self.AfUser.accessUser)
                self.userTable()
            except: pass
        elif self.otype == "blueprint":
            self.detailTable()
        elif self.otype == "connections":
            self.connectTable()
        elif self.otype == "realDetail":
            self.realDetailTable()
        elif self.otype == "seams":
            self.veiwSeamTable()
        elif self.otype == "equipments":
            try:
                self.saveBtn.setEnabled(self.AfUser.accessEquipment)
                self.equipmentTable()
            except: pass
        elif self.otype == "oscilation":
            try:
                self.saveBtn.setEnabled(self.AfUser.accessOscilationType)
                self.oscilationTable()
            except: pass
        self.tableWidget.hideColumn(0)
        self.stackedWidget.setCurrentIndex(4)


    #вывод табиц администрирования
    def equipmentTable(self):
        self.adPanelName.setText("Панель управления комплексами:")
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setHorizontalHeaderLabels(
            ["id", "Серийный номер", "Наименование", "Модель", "IP", "Порт", "Период","Подключение","Отключение","Статус"])
        equipments = Equipment.select()
        self.tableWidget.setRowCount(len(equipments))
        for i in range(len(equipments)):
            self.tableWidget.setItem(i, 0, twi(str(equipments[i].id)))
            self.tableWidget.setItem(i, 1, twi(equipments[i].serialNumber))
            self.tableWidget.setItem(i, 2, twi(equipments[i].name))
            self.tableWidget.setItem(i, 3, twi(equipments[i].model))
            self.tableWidget.setItem(i, 4, twi(equipments[i].ip))
            self.tableWidget.setCellWidget(i, 5, QtWidgets.QSpinBox())
            self.tableWidget.cellWidget(i, 5).setMaximum(65535)
            self.tableWidget.cellWidget(i, 5).setValue(equipments[i].port)
            self.tableWidget.setCellWidget(i, 6, QtWidgets.QDoubleSpinBox())
            self.tableWidget.cellWidget(i, 6).setMinimum(0.1)
            self.tableWidget.cellWidget(i, 6).setValue(equipments[i].period)
            self.tableWidget.setCellWidget(i, 7, QtWidgets.QPushButton("Подключиться"))
            self.tableWidget.cellWidget(i,7).clicked.connect(self.robConnect)
            self.tableWidget.setCellWidget(i, 8, QtWidgets.QPushButton("Отключиться"))
            self.tableWidget.cellWidget(i, 8).clicked.connect(self.robDisconnect)
            self.tableWidget.setItem(i, 9, twi("Нет подключения"))
            self.tableWidget.item(i,9).setBackground(Qt.red)
        self.tableWidget.resizeColumnsToContents()

    def robConnect(self):
        btn = self.app.focusWidget()
        ind = self.tableWidget.indexAt(btn.pos())
        ip = self.tableWidget.item(ind.row(), 4).text()
        print("Connect to",ip)
        self.statusBar.showMessage("Подключение к: " + ip, 3000)
        ###
        try:
            if ip in self.HarvestrDict:
                print(self.HarvestrDict[ip])
                self.HarvestrDict[ip].start()
            else:
                try:
                    equId = Equipment.get(Equipment.ip == ip).id
                except: pass
                guiInfo = [self.statusBar,self.AfUser,equId]
                print("new harvestr")
                self.HarvestrDict[ip] = opcc.DataHarvestr(ip, self.statusBar, self.AfUser.id)
                self.HarvestrDict[ip].start()

            self.tableWidget.item(ind.row(), 9).setText("Подключено")
            self.tableWidget.item(ind.row(), 9).setBackground(Qt.green)
        except:
            self.statusBar.showMessage("Нет подключения к: " + ip, 3000)

    def robDisconnect(self):
        btn = self.app.focusWidget()
        ind = self.tableWidget.indexAt(btn.pos())
        ip = self.tableWidget.item(ind.row(), 4).text()
        self.statusBar.showMessage("Отключение от: " + ip, 3000)
        ###
        try:

            self.tableWidget.item(ind.row(), 9).setText("Нет подключения")
            self.tableWidget.item(ind.row(), 9).setBackground(Qt.red)
        except:
            pass

    def detailTable(self):
        self.adPanelName.setText("Панель управления чертежами:")
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["id", "Номер чертежа", "Наименование", "Марка материала","Программа сварки","Расчётное время"])
        details = Detail.select()
        self.tableWidget.setRowCount(len(details))

        for i in range(len(details)):
            self.tableWidget.setItem(i, 0, twi(str(details[i].id)))
            self.tableWidget.setItem(i, 1, twi(details[i].blueprinNumber))
            self.tableWidget.setItem(i, 2, twi(details[i].detailName))
            self.tableWidget.setItem(i, 3, twi(details[i].materialGrade))
            self.tableWidget.setItem(i, 4, twi(details[i].weldingProgram))
            self.tableWidget.setItem(i, 5, twi(str(details[i].processingTime)))
        self.tableWidget.resizeColumnsToContents()

    def realDetailTable(self):
        self.adPanelName.setText("Панель управления деталями:")
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["id", "Номер чертежа", "Наименование","Номер партии", "Номер детали"])
        details = Seam.select().join(Detail).group_by(Seam.batchNumber, Seam.detailNumber)
        self.tableWidget.setRowCount(len(details))
        voidRow = None
        for i in range(len(details)):
            if details[i].batchNumber !="" and details[i].detailNumber !="":
                self.tableWidget.setItem(i, 0, twi("0"))
                self.tableWidget.setItem(i, 1, twi(details[i].detailId.blueprinNumber))
                self.tableWidget.setItem(i, 2, twi(str(details[i].detailId.detailName)))
                self.tableWidget.setItem(i, 3, twi(str(details[i].batchNumber)))
                self.tableWidget.setItem(i, 4, twi(str(details[i].detailNumber)))
            else:
                voidRow = i
        if voidRow is not None:
            self.tableWidget.removeRow(voidRow)
        self.tableWidget.resizeColumnsToContents()

    def userTable(self):
        self.adPanelName.setText("Панель управления пользователями:")
        self.tableWidget.setColumnCount(13)
        self.tableWidget.setHorizontalHeaderLabels(
            ["id", "Логин", "Имя", "Пароль", "Пользователи", "Детали", "Соединения",
             "Протоколы", "Архивы", "Добавление", "Удаление", "Комплексы", "Типы колебаний"])
        users = User.select()
        self.tableWidget.setRowCount(len(users))
        for i in range(len(users)):
            print(users[i].name)
            self.tableWidget.setItem(i, 0, twi(str(users[i].id)))
            self.tableWidget.setItem(i, 1, twi(users[i].login))
            self.tableWidget.setItem(i, 2, twi(users[i].name))
            self.tableWidget.setItem(i, 3, twi(users[i].passWord))
            self.tableWidget.setCellWidget(i, 4, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 5, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 6, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 7, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 8, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 9, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 10, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 11, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 12, QtWidgets.QCheckBox())
            self.tableWidget.cellWidget(i, 4).setCheckState(
                QtCore.Qt.Checked if users[i].accessUser else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 5).setCheckState(
                QtCore.Qt.Checked if users[i].accessDetail else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 6).setCheckState(
                QtCore.Qt.Checked if users[i].accessConn else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 7).setCheckState(
                QtCore.Qt.Checked if users[i].accessProt else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 8).setCheckState(
                QtCore.Qt.Checked if users[i].accessArch else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 9).setCheckState(
                QtCore.Qt.Checked if users[i].accessAdd else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 10).setCheckState(
                QtCore.Qt.Checked if users[i].accessRemove else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 11).setCheckState(
                QtCore.Qt.Checked if users[i].accessEquipment else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 12).setCheckState(
                QtCore.Qt.Checked if users[i].accessOscilationType else QtCore.Qt.Unchecked)

        self.tableWidget.resizeColumnsToContents()

    def connectTable(self):
        self.adPanelName.setText("Панель управления соединениями:")
        self.tableWidget.setColumnCount(12)
        self.tableWidget.setHorizontalHeaderLabels(
            ["id", "Вид соединения", "Толщина элементов", "Разделка кромок", "Размеры шва с допусками", "Марка/сечение проволоки", "Расход проволоки [м/мин]","Защитный газ","Расход газа [л/мин]","Программа сварки","Расчётное время","Предпочтительное частота сбора данных [с]"])
        connections = Connection.select()
        self.tableWidget.setRowCount(len(connections))
        for i in range(len(connections)):
            self.tableWidget.setItem(i, 0, twi(str(connections[i].id)))
            self.tableWidget.setItem(i, 1, twi(connections[i].ctype))
            self.tableWidget.setItem(i, 2, twi(connections[i].thicknessOfElement))
            self.tableWidget.setItem(i, 3, twi(connections[i].jointBevelling))
            self.tableWidget.setItem(i, 4, twi(connections[i].seamDimensions))
            self.tableWidget.setItem(i, 5, twi(connections[i].fillerWireMark+'/'+str(connections[i].fillerWireDiam)))
            self.tableWidget.setItem(i, 6, twi(str(connections[i].wireConsumption)))
            self.tableWidget.setItem(i, 7, twi(connections[i].shieldingGasType))
            self.tableWidget.setItem(i, 8, twi(str(connections[i].shieldingGasConsumption)))
            self.tableWidget.setItem(i, 9, twi(connections[i].programmName))
            self.tableWidget.setItem(i, 10, twi(str(connections[i].weldingTime)))
            self.tableWidget.setItem(i, 11, twi(str(connections[i].preferredPeriod)))
        self.tableWidget.resizeColumnsToContents()

    def veiwSeamTable(self):
        self.adPanelName.setText("Панель управления швами:")
        self.tableWidget.setColumnCount(11)
        self.tableWidget.setHorizontalHeaderLabels(
            ["id", "Тип соединения", "Тип детали", "Номер партии", "Номер детали", "Начало", "Окончание", "Статус","Установка",
             "Программа сварки", "Пользователь"])
        seams = Seam.select()
        self.tableWidget.setRowCount(len(seams))
        for i in range(len(seams)):
            self.tableWidget.setItem(i, 0, twi(str(seams[i].id)))
            if seams[i].connId is not None:
                self.tableWidget.setItem(i, 1, twi(str(seams[i].connId.ctype)))
            if seams[i].detailId is not None:
                self.tableWidget.setItem(i, 2, twi(str(seams[i].detailId.detailName)))
            self.tableWidget.setItem(i, 3, twi(str(seams[i].batchNumber)))
            self.tableWidget.setItem(i, 4, twi(str(seams[i].detailNumber)))
            self.tableWidget.setItem(i, 5, twi(str(seams[i].startTime)[:19]))
            self.tableWidget.setItem(i, 6, twi(str(seams[i].endTime)[:19]))
            if seams[i].endStatus == 0:
                self.tableWidget.setItem(i, 7, twi("Успешно"))
            else:
                self.tableWidget.setItem(i, 7, twi("Ошибка!"))
            if seams[i].equipmentId is not None:
                self.tableWidget.setItem(i, 8, twi(str(seams[i].equipmentId.name)))
            self.tableWidget.setItem(i, 9, twi(seams[i].weldingProgram))
            if seams[i].authorizedUser is not None:
                self.tableWidget.setItem(i, 10, twi(str(seams[i].authorizedUser.name)))
        self.tableWidget.resizeColumnsToContents()

    def oscilationTable(self):
        self.adPanelName.setText("Панель управления параметрами колебаний:")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["id", "Номер", "Название", "Изображение"])
        osc = OscilationType.select()
        self.tableWidget.setRowCount(len(osc))
        for i in range(len(osc)):
            ba = QtCore.QByteArray(osc[i].oscImg)
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(ba, "PNG")

            self.tableWidget.setItem(i, 0, twi(str(osc[i].id)))
            self.tableWidget.setItem(i, 1, twi(str(osc[i].oscNumber)))
            self.tableWidget.setItem(i, 2, twi(osc[i].oscName))
            self.tableWidget.setCellWidget(i, 3, QtWidgets.QLabel())
            self.tableWidget.cellWidget(i, 3).setPixmap(pixmap)
        self.tableWidget.resizeColumnsToContents()
    #######################################

class MWin(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.ui = UImodif()
        self.ui.setupUi(self, app)

    def addConnDia(self, id):
        self.dialog = AddConn(id, self.ui)
        self.dialog.show()

    def addSeamDia(self):
        self.dialog = AddConn(self.ui)
        self.dialog.show()

    def chooseDataDia(self, id, dataType):
        self.dialog = chooseData(id, dataType, self.ui)
        self.dialog.show()

    def timePdfDia(self):
        self.dialog = timePdfWin()
        self.dialog.show()

    def archSettings(self, archivator):
        self.dialog = settingsWin(archivator)
        self.dialog.show()


class timePdfWin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_timePdf()
        self.ui.setupUi(self)
        self.ui.chooseAdress.clicked.connect(self.chooseAdress)
        self.ui.makePdf.clicked.connect(self.createPdf)

    def chooseAdress(self):
        filename = QtWidgets.QFileDialog.getExistingDirectory()
        print(filename)
        self.ui.adress.setText(filename)

    def createPdf(self):
        start = self.ui.startTime.dateTime().toPyDateTime()
        end = self.ui.endTime.dateTime().toPyDateTime()
        adr = self.ui.adress.text()
        if adr != "" and (end-start > datetime.timedelta(0,0,0,0,0,0,0)):
            pg.create_periodPdf(adr, start, end)


class AddConn(QtWidgets.QWidget):
    detId = 0
    def __init__(self, id, mainUi):
        super().__init__()
        print(mainUi.otype)
        self.detId = id
        self.mainUi = mainUi
        self.ui = Ui_connAdd()
        self.ui.setupUi(self)
        if mainUi.otype == "blueprint":
            self.ui.listOfConn.setColumnCount(12)
            self.ui.listOfConn.setHorizontalHeaderLabels(
                ["id", "Присвоено", "Вид сварного соединения", "Толщина элементов", "Разделка кромок",
                 "Размеры шва (мм)",
                 "Марка/сечение проволоки", "Расход проволоки (см/мин)", "Газ", "Расход газа (л/мин)",
                 "Программа сварки", "Рассчётное время"])
            self.ui.listOfConn.hideColumn(0)
            connections = Connection.select()
            self.ui.listOfConn.setRowCount(len(connections))
            connDetsId = []
            condets = DetConn.select().where(DetConn.detailId == self.detId)
            for condet in condets:
                connDetsId.append(condet.connId)
            for i in range(len(connections)):
                self.ui.listOfConn.setItem(i, 0, twi(str(connections[i].id)))
                self.ui.listOfConn.setCellWidget(i, 1, QtWidgets.QCheckBox())
                self.ui.listOfConn.cellWidget(i, 1).setCheckState(
                    QtCore.Qt.Checked if (connections[i] in connDetsId) else QtCore.Qt.Unchecked)
                self.ui.listOfConn.setItem(i, 2, twi(connections[i].ctype))
                self.ui.listOfConn.setItem(i, 3, twi(connections[i].thicknessOfElement))
                self.ui.listOfConn.setItem(i, 4, twi(connections[i].jointBevelling))
                self.ui.listOfConn.setItem(i, 5, twi(connections[i].seamDimensions))
                self.ui.listOfConn.setItem(i, 6,
                                        twi(connections[i].fillerWireMark + '/' + str(connections[i].fillerWireDiam)))
                self.ui.listOfConn.setItem(i, 7, twi(str(connections[i].wireConsumption)))
                self.ui.listOfConn.setItem(i, 8, twi(connections[i].shieldingGasType))
                self.ui.listOfConn.setItem(i, 9, twi(str(connections[i].shieldingGasConsumption)))
                self.ui.listOfConn.setItem(i, 10, twi(connections[i].programmName))
                self.ui.listOfConn.setItem(i, 11, twi(str(connections[i].weldingTime)))
        elif mainUi.otype == "realDetail":
            self.ui.listOfConn.setColumnCount(10)
            self.ui.listOfConn.hideColumn(0)
            self.ui.listOfConn.setHorizontalHeaderLabels(
                ["id", "Тип соединения", "Тип детали", "Номер партии", "Номер детали", "Начало", "Окончание", "Статус",
                 "Программа сварки", "Пользователь"])
            seams = Seam.select()
            self.ui.listOfConn.setRowCount(len(seams))
            for i in range(len(seams)):
                self.ui.listOfConn.setItem(i, 0, twi(str(seams[i].id)))
                if seams[i].connId is not None:
                    self.ui.listOfConn.setItem(i, 1, twi(str(seams[i].connId.ctype)))
                if seams[i].detailId is not None:
                    self.ui.listOfConn.setItem(i, 2, twi(str(seams[i].detailId.detailName)))
                self.ui.listOfConn.setItem(i, 3, twi(str(seams[i].batchNumber)))
                self.ui.listOfConn.setItem(i, 4, twi(str(seams[i].detailNumber)))
                self.ui.listOfConn.setItem(i, 5, twi(str(seams[i].startTime)[:19]))
                self.ui.listOfConn.setItem(i, 6, twi(str(seams[i].endTime)[:19]))
                if seams[i].endStatus:
                    self.ui.listOfConn.setItem(i, 7, twi("Успешно"))
                else:
                    self.ui.listOfConn.setItem(i, 7, twi("Ошибка!"))
                self.ui.listOfConn.setItem(i, 8, twi(seams[i].weldingProgram))
                if seams[i].authorizedUser is not None:
                    self.ui.listOfConn.setItem(i, 9, twi(str(seams[i].authorizedUser.name)))
        self.ui.listOfConn.resizeColumnsToContents()
        self.ui.addButton.clicked.connect(self.add)

    def add(self):
        if self.mainUi.otype == "realDetail":
            addInd = []
            for ind in self.ui.listOfConn.selectedIndexes():
                if ind.row() not in addInd:
                    addInd.append(ind.row())
            for ind in addInd:
                print(self.ui.listOfConn.item(ind, 0).text())
                query = Seam.update(
                    batchNumber=self.mainUi.batchNumber_2.text(),
                    detailNumber=self.mainUi.numberInBatch.text()).where(
                    Seam.id == int(self.ui.listOfConn.item(ind, 0).text()))
                query.execute()
            #self.mainUi.realDetailView(self.detId)
        elif self.mainUi.otype == "blueprint":
            if self.detId < 1:
                self.detId = self.mainUi.saveDeteil()
            for i in range(self.ui.listOfConn.rowCount()):
                conId = int(self.ui.listOfConn.item(i, 0).text())
                countInDb = len(DetConn.select().where((DetConn.detailId == self.detId) & (DetConn.connId == conId)))
                isAdd = self.ui.listOfConn.cellWidget(i, 1).isChecked()
                if countInDb == 0 and isAdd:
                    DetConn(
                    connId=conId,
                    detailId=self.detId).save()
                elif countInDb > 0 and not isAdd:
                    print("dell")
                    dellDetConn = DetConn.get((DetConn.detailId == self.detId) & (DetConn.connId == conId))
                    dellDetConn.delete_instance()
                    self.mainUi.detailView(self.detId)
        self.close()


class chooseData(QtWidgets.QWidget):
    seamId = 0
    dataType = 'connection'
    def __init__(self, id, dataType, mainUi):
        super().__init__()
        self.seamId = id
        self.dataType = dataType
        self.mainUi = mainUi
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.chooseTable.doubleClicked.connect(self.doubleClick)
        self.ui.selectButton.hide()
        if self.dataType == 'user':
            self.ui.chooseTable.setColumnCount(3)
            self.ui.chooseTable.setHorizontalHeaderLabels(
                ["id", "Логин", "Имя"])
            users = User.select()
            self.ui.chooseTable.setRowCount(len(users))
            for i in range(len(users)):
                print(users[i].name)
                self.ui.chooseTable.setItem(i, 0, twi(str(users[i].id)))
                self.ui.chooseTable.setItem(i, 1, twi(users[i].login))
                self.ui.chooseTable.setItem(i, 2, twi(users[i].name))
        elif self.dataType == 'eqvipment':
            self.ui.chooseTable.setColumnCount(5)
            self.ui.chooseTable.setHorizontalHeaderLabels(
                ["id", "Серийный номер", "Наименование", "Модель", "IP"])
            equipments = Equipment.select()
            self.ui.chooseTable.setRowCount(len(equipments))
            for i in range(len(equipments)):
                self.ui.chooseTable.setItem(i, 0, twi(str(equipments[i].id)))
                self.ui.chooseTable.setItem(i, 1, twi(equipments[i].serialNumber))
                self.ui.chooseTable.setItem(i, 2, twi(equipments[i].name))
                self.ui.chooseTable.setItem(i, 3, twi(equipments[i].model))
                self.ui.chooseTable.setItem(i, 4, twi(equipments[i].ip))
        elif self.dataType == 'blueprint':
            self.ui.chooseTable.setColumnCount(6)
            self.ui.chooseTable.setHorizontalHeaderLabels(
                ["id", "Номер чертежа", "Наименование", "Марка материала", "Программа сварки", "Расчётное время"])
            details = Detail.select()
            self.ui.chooseTable.setRowCount(len(details))

            for i in range(len(details)):
                self.ui.chooseTable.setItem(i, 0, twi(str(details[i].id)))
                self.ui.chooseTable.setItem(i, 1, twi(details[i].blueprinNumber))
                self.ui.chooseTable.setItem(i, 2, twi(details[i].detailName))
                self.ui.chooseTable.setItem(i, 3, twi(details[i].materialGrade))
                self.ui.chooseTable.setItem(i, 4, twi(details[i].weldingProgram))
                self.ui.chooseTable.setItem(i, 5, twi(str(details[i].processingTime)))
        elif self.dataType == 'connection':
            self.ui.chooseTable.setColumnCount(7)
            self.ui.chooseTable.setHorizontalHeaderLabels(
                ["id", "Вид соединения", "Толщина элементов", "Разделка кромок", "Размеры шва с допусками",
                 "Марка/сечение проволоки", "Защитный газ"])
            seam = Seam.get(Seam.id == self.seamId)
            print(seam)
            if seam.detailId is not None:
                connections = Connection.select().join(DetConn).where(DetConn.detailId == seam.detailId)
                print(connections)
                self.ui.chooseTable.setRowCount(len(connections))
                for i in range(len(connections)):
                    self.ui.chooseTable.setItem(i, 0, twi(str(connections[i].id)))
                    self.ui.chooseTable.setItem(i, 1, twi(connections[i].ctype))
                    self.ui.chooseTable.setItem(i, 2, twi(connections[i].thicknessOfElement))
                    self.ui.chooseTable.setItem(i, 3, twi(connections[i].jointBevelling))
                    self.ui.chooseTable.setItem(i, 4, twi(connections[i].seamDimensions))
                    self.ui.chooseTable.setItem(i, 5,
                                             twi(connections[i].fillerWireMark + '/' + str(connections[i].fillerWireDiam)))
                    self.ui.chooseTable.setItem(i, 6, twi(connections[i].shieldingGasType))
        self.ui.chooseTable.resizeColumnsToContents()

    def doubleClick(self):
        if self.ui.chooseTable.currentRow() >= 0 and self.ui.chooseTable.item(self.ui.chooseTable.currentRow(), 0) is not None:
            id = int(self.ui.chooseTable.item(self.ui.chooseTable.currentRow(), 0).text())
            if self.dataType == 'user':
                query = Seam.update(authorizedUser = id).where(
                    Seam.id == self.seamId)
                query.execute()
            elif self.dataType == 'eqvipment':
                query = Seam.update(equipmentId=id).where(
                    Seam.id == self.seamId)
                query.execute()
            elif self.dataType == 'blueprint':
                query = Seam.update(detailId=id, connId=None).where(
                    Seam.id == self.seamId)
                query.execute()
            elif self.dataType == 'connection':
                query = Seam.update(connId=id).where(
                    Seam.id == self.seamId)
                query.execute()
            self.close()
            self.mainUi.protocolView(self.seamId)


class settingsWin(QtWidgets.QWidget):
    def __init__(self, archivator):
        super().__init__()
        self.arch = archivator
        self.ui = Ui_settingsWin()
        self.ui.setupUi(self)
        self.ui.chooseAdress.clicked.connect(self.chooseAdress)
        self.ui.saveBtn.clicked.connect(self.saveSettings)
        config = self.arch.getConfig()
        print(config)
        self.ui.adress.setText(config['saveAdress'])
        self.ui.hours.setValue(int(config['periodH']))
        self.ui.minuts.setValue(int(config['periodM']))
        self.ui.seconds.setValue(int(config['periodS']))
        self.ui.size.setValue(int(config['sizeparam']))
        self.ui.timeArch.setCheckState(QtCore.Qt.Checked)
        self.ui.sizeArch.setCheckState(QtCore.Qt.Checked)


    def chooseAdress(self):
        filename = QtWidgets.QFileDialog.getExistingDirectory()
        print(filename)
        self.ui.adress.setText(filename)

    def saveSettings(self):
        print("save")
        self.arch.setConfig(self.ui.adress.text(),
                            self.ui.hours.text(),
                            self.ui.minuts.text(),
                            self.ui.seconds.text(),
                            self.ui.size.text())


app = QtWidgets.QApplication(sys.argv)
MainWindow = MWin(app)
MainWindow.show()
sys.exit(app.exec_())