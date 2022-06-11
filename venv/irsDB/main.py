import time
print("Подготовка необходимых пакетов ПО")
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem as twi
from PyQt5.QtWidgets import QMessageBox, QLineEdit
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QCategoryAxis, QValueAxis
from PyQt5.QtCore import QPoint, QPointF
from PyQt5.Qt import QPen, QFont, Qt, QSize
from PyQt5.QtGui import QColor, QBrush, QPainter, QMouseEvent
from PIL import Image, ImageQt
import pdfGenerator as pg
import numpy as np
from migration300522 import *

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

import threading

#pyuic5 -x base.ui -o gui.py

from mainWinFunc.models import *
from mainWinFunc import loginFunc
from mainWinFunc.popUpWins import *
from mainWinFunc.tabelVeiwers import *
from mainWinFunc.chartPainter import *

class UImodif(Ui_MainWindow):

    otype = ""
    imgs = b'\x00\x00\x00\x00'
    curImg = 0
    curId = 0
    AfUser = User.select()[0]
    A = archivate.Archivator("IRSwelding.db")
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! перед сборкой раскомитить !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    A.asincArch()
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    isActualDB = True
    HarvestrDict = {}

    #инициализация функций нажатий
    def setupUi(self, MainWindow, app):
        super().setupUi(MainWindow)
        self.app = app
        #стартовая конфигурация!!!!!!!!!!!!!!!!!!!!!! перед сборкой раскомитить !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        loginFunc.exitf(self)
        #self.centralwidget.setStyleSheet("background-color:white;")
        #self.centralwidget.setStyleSheet("")
        #кнопки
        self.passFld.setEchoMode(QLineEdit.Password)
        self.loginBtn.clicked.connect(lambda: loginFunc.login(self))
        self.addBtn.clicked.connect(self.add)
        self.saveChalenges.clicked.connect(self.saveDeteil)
        self.saveConn.clicked.connect(self.saveConnChlngs)
        #self.makePdf.clicked.connect(lambda: print("pdf"))
        self.saveBtn.clicked.connect(self.save)
        self.delBtn.clicked.connect(self.dell)
        self.addConnection.clicked.connect(lambda: MainWindow.addConnDia(self.curId))
        self.viewBlueprintBtn.clicked.connect(self.footprintView)
        self.choosePdfAdress.clicked.connect(self.adrForPdf)
        self.home.clicked.connect(lambda: initChart(self, self.curId))
        self.addSeamBtn.clicked.connect(lambda: MainWindow.addConnDia(self.curId))
        self.saveProtocolBtn.clicked.connect(self.saveProtocol)
        self.delSeamBtn.clicked.connect(self.delSeamFromDetail)
        self.createDetailPdf.clicked.connect(self.detReport)
        self.DetailSeamsSave.clicked.connect(self.realDetailUpdate)

        self.chooseBlueprintBtn.clicked.connect(lambda: MainWindow.chooseDataDia(None, 'blueprint'))

        self.actionback.triggered.connect(lambda: backToTable(self))#lambda: self.redirect(4))

        #выбор данных шва
        self.chooseEqvipment.clicked.connect(lambda: MainWindow.chooseDataDia(self.curId, 'eqvipment'))
        self.chooseUser.clicked.connect(lambda: MainWindow.chooseDataDia(self.curId, 'user'))
        self.chooseBlueprint.clicked.connect(lambda: MainWindow.chooseDataDia(self.curId, 'realDetail'))
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
        self.exit.triggered.connect(lambda: loginFunc.exitf(self))
        self.detail.triggered.connect(lambda: adpanel(self, "blueprint"))
        self.connections.triggered.connect(lambda: adpanel(self, "connections"))
        self.realDetail.triggered.connect(lambda: adpanel(self, "realDetail"))
        self.seams.triggered.connect(lambda: adpanel(self, "seams"))
        self.users.triggered.connect(lambda: adpanel(self, "user"))
        self.makeArch.triggered.connect(self.manualArch)
        self.chooseArch.triggered.connect(self.chArch)
        self.equipments.triggered.connect(lambda: adpanel(self, "equipments"))
        self.timePdf.triggered.connect(MainWindow.timePdfDia)
        self.oscTypeTable.triggered.connect(lambda: adpanel(self, "oscilation"))
        self.archSettings.triggered.connect(lambda: MainWindow.archSettings(self.A))
        self.returnToActualDB.triggered.connect(self.returnToActual)
        self.saveArchAs.triggered.connect(self.sArchAs)
        self.tableWidget.doubleClicked.connect(self.doubleClick)


        #перерисовка графика
        self.graph.setRubberBand(QChartView.HorizontalRubberBand)
        self.wireCCchb.stateChanged.connect(lambda: initChart(self, self.curId))
        self.gasCCchb.stateChanged.connect(lambda: initChart(self, self.curId))
        self.torchSpeedchb.stateChanged.connect(lambda: initChart(self, self.curId))
        self.currentchb.stateChanged.connect(lambda: initChart(self, self.curId))
        self.voltagechb.stateChanged.connect(lambda: initChart(self, self.curId))
        self.voltageCorrectionchb.stateChanged.connect(lambda: initChart(self, self.curId))
        self.wireSpeedchb.stateChanged.connect(lambda: initChart(self, self.curId))
        self.gasConsumptionchb.stateChanged.connect(lambda: initChart(self, self.curId))
        self.gasDeltaChb.stateChanged.connect(lambda: initChart(self, self.curId))
        self.wireDeltaChb.stateChanged.connect(lambda: initChart(self, self.curId))


        self.lineEdit_2.hide()
        self.pushButton_12.hide()
        self.gasDeltaChb.hide()
        self.gasConsumptionchb.hide()
        self.voltageCorrectionchb.hide()

    #######Область тестовых функций########
    def stopAll(self):
        print(self.HarvestrDict)
        for harvestr in self.HarvestrDict:
            HarvestrDict[harvestr].stop
        self.A.deactivate()

    def sArchAs(self):
        filename = QtWidgets.QFileDialog.getSaveFileName()[0]
        if filename != "":
            print(filename)
            if self.isActualDB:
                self.A.saveAs("IRSwelding.db",filename+".zip")
            else:
                self.A.saveAs("tmp/IRSwelding.db",filename+".zip")

    def detReport(self):
        batch = self.batchNumber_2.text()
        det = self.numberInBatch.text()
        adress = self.pdfAdress.text()
        pg.create_pdf(adress, batch, det)
        self.statusBar.showMessage("Отчёт готов", 3000)

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
                #endStatus = self.endStatus.isChecked(),
                burnerOscillation = OscilationType.get(OscilationType.oscName == self.oscType.currentText()).id,
                period = self.seamPeriod.value()).where(
                Seam.id == self.curId)  # DoubleField()
            query.execute()
            self.protocolView(self.curId)

    def delSeamFromDetail(self):
        if (self.batchNumber_2.text() != "" and
            self.numberInBatch.text() != "" and
            self.blprName.text() != ""):
            self.realDetailUpdate()
            addInd = []
            for ind in self.seamTable.selectedIndexes():
                if ind.row() not in addInd:
                    addInd.append(ind.row())
            for ind in addInd:
                #print(self.seamTable.item(ind, 0).text())
                query = Seam.update(
                    batchNumber = "",
                    detailNumber = "",
                    realDetId = None).where(
                    Seam.id == int(self.seamTable.item(ind, 0).text()))
                query.execute()
            if self.curId:
                self.realDetailView(self.curId)

    def manualArch(self):
        self.A.arch('User_s reqvest',self.A.getConfig()["saveAdress"])

    def chArch(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(filter = '*.zip')[0]
        if filename != "":
            #print(filename)
            cdb.cooseArch(filename)
            migration300522()
            self.statusBar.showMessage("Переклёчен на архив: " + filename, 3000)
            self.isActualDB = False
            loginFunc.makeEnable(self, self.AfUser.accessUser, self.AfUser.accessArch, self.AfUser.accessArch,
                            self.AfUser.accessArch, self.AfUser.accessArch, self.AfUser.accessArch)

    def returnToActual(self):
        cdb.connToDb("IRSwelding.db")
        migration300522()
        try:
            os.remove("tmp/IRSwelding.db")
        except:
            pass
        self.statusBar.showMessage("Переклёчен на актуальную бд", 3000)
        self.isActualDB = True
        loginFunc.makeEnable(self, self.AfUser.accessUser, self.AfUser.accessDetail, self.AfUser.accessConn,
                        self.AfUser.accessProt, self.AfUser.accessAdd, self.AfUser.accessRemove)

    def adrForPdf(self):
        filename = QtWidgets.QFileDialog.getExistingDirectory()
        #print(filename)
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
                    #print(self.tableWidget.cellWidget(i, 4).isChecked())
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
            #print(type(pixmap_bytes))
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
                self.realDetailView(id)
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
            addInd = []
            for ind in self.tableWidget.selectedIndexes():
                if ind.row() not in addInd:
                    addInd.append(ind.row())
            if self.otype == "user":
                for ind in addInd:
                    dellId = int(self.tableWidget.item(ind, 0).text())
                    try:
                        query = Seam.update(authorizedUser=None).where(Seam.authorizedUser == dellId)
                        query.execute()
                    except:pass
                    dellUser = User.get(User.id == dellId)
                    dellUser.delete_instance()
                    print("dell")
                self.userTable()
            elif self.otype == "blueprint":
                for ind in addInd:
                    dellId = int(self.tableWidget.item(ind, 0).text())
                    try:
                        query = Seam.update(detailId=None).where(Seam.detailId == dellId)
                        query.execute()
                    except: pass
                    try:
                        query = RealDetail.update(detailId=None).where(RealDetail.detailId == dellId)
                        query.execute()
                    except: pass
                    try:
                        dellDetConns = DetConn.select().where(DetConn.detailId == dellId)
                        for dellDetConn in dellDetConns:
                            dellDetConn.delete_instance()
                    except: pass
                    try:
                        dellDetail = Detail.get(Detail.id == dellId)
                        dellDetail.delete_instance()
                    except:pass
                detailTable(self)
            elif self.otype == "connections":
                for ind in addInd:
                    dellId = int(self.tableWidget.item(ind, 0).text())
                    try:
                        query = Seam.update(connId=None).where(Seam.connId == dellId)
                        query.execute()
                    except:pass
                    try:
                        dellDetConns = DetConn.select().where(DetConn.connId == dellId)
                        for dellDetConn in dellDetConns:
                            dellDetConn.delete_instance()
                    except: pass
                    dellConnection = Connection.get(Connection.id == dellId)
                    dellConnection.delete_instance()
                self.connectTable()
            elif self.otype == "equipments":
                for ind in addInd:
                    dellId = int(self.tableWidget.item(ind, 0).text())
                    try:
                        query = Seam.update(equipmentId=None).where(Seam.equipmentId == dellId)
                        query.execute()
                    except:pass
                    dellEquipment = Equipment.get(Equipment.id == dellId)
                    dellEquipment.delete_instance()
                self.equipmentTable()
            elif self.otype == "oscilation":
                for ind in addInd:
                    dellId = int(self.tableWidget.item(ind, 0).text())
                    try:
                        query = Seam.update(burnerOscillation=None).where(Seam.burnerOscillation == dellId)
                        query.execute()
                    except:pass
                    dellOscilationType = OscilationType.get(OscilationType.id == dellId)
                    dellOscilationType.delete_instance()
                self.oscilationTable()
            elif self.otype == "seams":
                for ind in addInd:
                    dellId = int(self.tableWidget.item(ind, 0).text())
                    dellSeam = Seam.get(Seam.id == dellId)
                    dellSeam.delete_instance()
                self.veiwSeamTable()
            elif self.otype == "realDetail":
                for ind in addInd:
                    try:
                        dellId = int(self.tableWidget.item(ind, 0).text())
                        query = Seam.update(
                            batchNumber = "",
                            detailNumber = "",
                            realDetId = None).where(
                            Seam.realDetId == dellId)
                        query.execute()
                        dellRealDetail = RealDetail.get(RealDetail.id == dellId)
                        dellRealDetail.delete_instance()
                        print("dell ok")
                        """delDeteil = int(self.tableWidget.item(ind, 4).text())
                        delBatch = int(self.tableWidget.item(ind, 3).text())
                        print("dell", delDeteil, delBatch)
                        query = Seam.update(
                            batchNumber="",
                            detailNumber="").where(
                            Seam.batchNumber == delBatch and Seam.detailNumber == delDeteil)
                        query.execute()"""
                    except:
                        pass
                realDetailTable(self)

    # временная функция
    def redirect(self, n):
        imgs = b'\x00\x00\x00\x00'
        self.stackedWidget.setCurrentIndex(n)
    #Отображение данных в спец формах
    def realDetailView(self, id):
        self.stackedWidget.setCurrentIndex(5)
        self.toolBar.show()
        detail = RealDetail.get(RealDetail.id == id)
        seams = Seam.select().where(Seam.realDetId == id)
        self.batchNumber_2.setText(detail.batchNumber)
        self.numberInBatch.setText(detail.detailNumber)

        self.seamTable.setRowCount(len(seams))

        self.seamTable.setColumnCount(4)
        self.seamTable.setHorizontalHeaderLabels(
            ["id","Тип", "Начало", "Окончание"])
        for i in range(len(seams)):
            self.seamTable.setItem(i, 0, twi(str(seams[i].id)))
            self.seamTable.setItem(i, 1, twi(str(seams[i].connId.ctype) if seams[i].connId else "Не присвоено"))
            self.seamTable.setItem(i, 2, twi(str(seams[i].startTime)[:-7]))
            self.seamTable.setItem(i, 3, twi(str(seams[i].endTime)[:-7]))
        self.seamTable.hideColumn(0)
        self.seamTable.resizeColumnsToContents()
        if detail.detailId is not None:
            self.blprName.setText(detail.detailId.detailName)
            self.imgs = detail.detailId.img
            self.curImg = 0
            self.veiwImg(self.dateilImg)

    def realDetailUpdate(self):
        #print(self.tableWidget.currentRow())
        newButchN = self.batchNumber_2.text()
        newDetailN = self.numberInBatch.text()
        newBlprName = self.blprName.text()
        detailId = None
        if newBlprName != "":
            detailId = Detail.get(Detail.detailName == newBlprName).id
        if self.curId < 1:
            print("create")
            rd = RealDetail(batchNumber = newButchN, detailNumber = newDetailN, detailId = detailId)
            rd.save()
            self.curId = rd.id
        else:
            print("update")
            query = RealDetail.update(batchNumber = newButchN, detailNumber = newDetailN, detailId = detailId).where(
                RealDetail.id == self.curId)
            query.execute()
        """if self.tableWidget.currentRow() >= 0:
            butchN = self.tableWidget.item(self.tableWidget.currentRow(), 3).text()
            detailN = self.tableWidget.item(self.tableWidget.currentRow(), 4).text()
            newButchN = self.batchNumber_2.text()
            newDetailN = self.numberInBatch.text()
            print(butchN, newButchN)
            print(detailN, newDetailN)
            detailId = None
            if self.curId is not None or self.curId !=0:
                detailId = self.curId
            query = Seam.update(
                batchNumber=newButchN,
                detailNumber=newDetailN,
                detailId = self.curId).where(
                Seam.batchNumber == butchN, Seam.detailNumber == detailN)  # DoubleField()
            query.execute()
            self.realDetailView(butchN = newButchN, detailN = newDetailN)
        else:
            print("Выберите шов из таблицы")
            self.statusBar.showMessage("Выберите шов из таблицы", 3000)"""

    def protocolView(self, id):
        self.stackedWidget.setCurrentIndex(0)
        self.toolBar.show()
        seam = Seam.get(Seam.id == id)
        #print("its work", seam)
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
        self.endStatus.setCheckState(QtCore.Qt.Unchecked if seam.endStatus else QtCore.Qt.Checked)
        self.endStatus.setText("Ошибка:"+str(seam.endStatus) if seam.endStatus else "")
        self.seamPeriod.setValue(seam.period)
        oscs = OscilationType.select()
        self.oscType.clear()
        for osc in oscs:
            self.oscType.addItem(osc.oscName)
        self.oscType.setCurrentText(seam.burnerOscillation.oscName)
        datalenght, swireSpeed, sgasConsumption = initChart(self, id)
        GasCons = round(sum(sgasConsumption) * seam.period / 60, 3)
        WireCons = round(sum(swireSpeed) * seam.period/60, 1)
        if seam.connId is None:
            self.gasDelta.setText("Нет данных")#str(GasCons)+" литров")
            self.wireDelta.setText(str(WireCons)+" м (реальный расход)")
        else:
            conn = Connection.get(Connection.id == seam.connId)
            t = datetime.datetime.strptime(conn.weldingTime, "%H:%M:%S")
            delta = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            #print(delta.total_seconds())
            WireCons -= (conn.wireConsumption/60*delta.total_seconds())
            GasCons = round(conn.shieldingGasConsumption/60 * datalenght * seam.period,3)
            self.gasDelta.setText(str(GasCons) + " литров")
            self.wireDelta.setText(str(WireCons) + " м")

    def footprintView(self):
        det = Detail.get(Detail.detailName == self.blprName.text())
        self.detailView(det.id)

    def detailView(self, id):
        if id:
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
        else:
            print("чертёж не задан")

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
        self.blprName.setText("")
        self.seamTable.clear()


    #####################################

    # Функции работы с изображениями
    def newImg(self, label):
        filename = QtWidgets.QFileDialog.getOpenFileName(filter = '(*.png *.jpg *.bmp)')[0]
        if filename != "":
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
            query = Detail.update(blueprinNumber = self.blueprinNumber.text(),
                detailName = self.detailName.text(),
                materialGrade = self.materialGrade.text(),
                weldingProgram = self.weldingProgram.text(),
                processingTime = datetime.time(self.HprocessingTime.value(), self.MprocessingTime.value(), self.SprocessingTime.value()),
                img = self.imgs).where(Detail.id == self.curId)
            query.execute()
        adpanel(self, "blueprint")
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
                wireMassConsumption = float(self.wireMassConsumption.text().replace(',','.')),
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
                wireMassConsumption=float(self.wireMassConsumption.text().replace(',', '.')),
                shieldingGasType = self.shieldingGasType.text(),#CharField()
                shieldingGasConsumption = float(self.shieldingGasConsumption.text().replace(',','.')),#DoubleField()
                programmName = self.programmName.text(),#CharField()
                weldingTime = datetime.time(self.HweldingTime.value(), self.MweldingTime.value(), self.SweldingTime.value()),
                preferredPeriod = self.preferredPeriod.value()).where(
                Connection.id == self.curId)  # DoubleField()
            query.execute()
        adpanel(self, "connections")


class MWin(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.ui = UImodif()
        self.ui.setupUi(self, app)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.ui.stopAll()

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


if __name__ == "__main__":
    print("Запуск")
    migration300522()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MWin(app)
    MainWindow.show()
    sys.exit(app.exec_())

    """def demoConn(self):
            print("a")
            btn = self.app.focusWidget()
            ind = self.tableWidget.indexAt(btn.pos())
            ip = self.tableWidget.item(ind.row(), 4).text()
            print("Connect to", ip)
            self.statusBar.showMessage("Подключение к: " + ip, 3000)
            self.tableWidget.item(ind.row(), 9).setText("Подключено")
            self.tableWidget.item(ind.row(), 9).setBackground(Qt.green)
            threading.Timer(6.0, lambda: self.statusBar.showMessage("Начат новый шов", 3000)).start()
            threading.Timer(38.0, lambda: self.statusBar.showMessage("Шов добавлен", 3000)).start()
            threading.Timer(41.0, lambda: self.statusBar.showMessage("", 3000)).start()"""