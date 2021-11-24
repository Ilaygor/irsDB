from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem as twi
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QCategoryAxis, QValueAxis
from PyQt5.QtCore import QPoint, QPointF
from PyQt5.Qt import QPen, QFont, Qt, QSize
from PyQt5.QtGui import QColor, QBrush, QPainter, QMouseEvent
from PIL import Image, ImageQt
import numpy as np
import peewee
from models import *
from GUI import *
import sys
import datetime
from io import BytesIO
import byteimgs as bi
import struct
import archivate

#pyuic5 -x base.ui -o gui.py


"""
with db:
    db.create_tables([User, Detail, Connection, Seam])

    db.commit()
    login = input("log: ")
    #password = input("pass: ")
    try:
        user = User.get(User.login == login)
        print(user.passWord)
    except:
        print("ups")
    print('done')
"""

class LineSeries(QLineSeries):
    def __init__(self, *args, **kwargs):
        QLineSeries.__init__(self, *args, **kwargs)
        self.start = QPointF()
        self.pressed.connect(self.on_pressed)

    def on_pressed(self, point):
        self.start = point
        print("on_pressed", round(point.x(), 1))


class UImodif(Ui_MainWindow):

    otype = ""
    imgs = b'\x00\x00\x00\x00'
    curImg = 0
    A = archivate.Archivator("IRSwelding.db")

    #инициализация функций нажатий
    def btnFunction(self):
        #книпки
        self.loginBtn.clicked.connect(self.login)
        self.addBtn.clicked.connect(self.add)
        self.addDetImg.clicked.connect(self.newImg)
        self.saveChalenges.clicked.connect(self.saveDeteil)
        self.saveConn.clicked.connect(self.saveConnChlngs)
        self.makePdf.clicked.connect(lambda: print("pdf"))
        self.saveBtn.clicked.connect(self.save)
        self.delBtn.clicked.connect(self.dell)
        self.prvDetImg.clicked.connect(self.veiwPrevImgD)
        self.nextDetImg.clicked.connect(self.veiwNextImgD)
        self.prvConnImg.clicked.connect(lambda: print(self.curImg))
        self.nextConnImg.clicked.connect(lambda: print(self.curImg))

        #пункты меню
        self.exit.triggered.connect(lambda: self.redirect(1))
        self.detail.triggered.connect(lambda: self.adpanel("detail"))
        self.connections.triggered.connect(lambda: self.adpanel("connections"))
        self.realDetail.triggered.connect(lambda: self.adpanel("realDetail"))
        self.seams.triggered.connect(lambda: self.adpanel("seams"))
        self.users.triggered.connect(lambda: self.adpanel("user"))
        self.makeArch.triggered.connect(self.ar)

        self.tableWidget.doubleClicked.connect(self.doubleClick)

        #перерисовка и инициализация графика
        """self.wireCCchb.stateChanged.connect(self.initChart)
        self.gasCCchb.stateChanged.connect(self.initChart)
        self.torchSpeedchb.stateChanged.connect(self.initChart)
        self.burnerOscillationchb.stateChanged.connect(self.initChart)
        self.currentchb.stateChanged.connect(self.initChart)
        self.voltagechb.stateChanged.connect(self.initChart)
        self.voltageCorrectionchb.stateChanged.connect(self.initChart)
        self.wireSpeedchb.stateChanged.connect(self.initChart)
        self.gasConsumptionchb.stateChanged.connect(self.initChart)"""


    #######Область тестовых функций########
    def ar(self):
        self.A.arch('User_s reqvest')
    ###########################################


    # Удаление, добавление редактирование данных
    def save (self):
        if self.otype == "user":
            self.saveUser()
            self.userTable()

    def saveUser(self):
        for i in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(i, 0) is None or self.tableWidget.item(i, 0).text() == "":
                if self.tableWidget.item(i, 1) is not None and self.tableWidget.item(i,
                                                                                     2) is not None and self.tableWidget.item(
                        i, 3) is not None:
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
                             accessRemove=self.tableWidget.cellWidget(i, 10).isChecked()
                             ).save()
                    except:
                        print("не создано")
                elif self.tableWidget.item(i, 1) != "" and self.tableWidget.item(i, 2) != "" and self.tableWidget.item(i, 3) != "":
                    pass

    def add(self):
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
        elif self.otype == "detail":
            self.redirect(2)
            #self.detailView(3)
        elif self.otype == "connections":
            self.redirect(3)
            #self.ConnView(1)
        elif self.otype == "realDetail":
            self.redirect(2)
        elif self.otype == "seams":
            pass
            #self.protocolView(10)

    def doubleClick(self):
        if self.tableWidget.currentRow() >= 0 and self.tableWidget.item(self.tableWidget.currentRow(), 0) is not None:
            id = int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())
            if self.otype == "user":
                pass
            elif self.otype == "detail":
                print(id)
                self.detailView(id)
            elif self.otype == "connections":
                print(id)
                self.ConnView(id)
            elif self.otype == "realDetail":
                pass
            elif self.otype == "seams":
                print(id)
                self.protocolView(id)


        # отрисовка графиков протоколов

    def dell(self):
        if self.tableWidget.currentRow() >= 0 and self.tableWidget.item(self.tableWidget.currentRow(), 0) is not None:
            dellId = int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())
            if self.otype == "user":
                dellUser = User.get(User.id == dellId)
                dellUser.delete_instance()
                print("dell")
                self.userTable()
            elif self.otype == "detail":
                dellDetail = Detail.get(Detail.id == dellId)
                dellDetail.delete_instance()
                self.detailTable()
            elif self.otype == "connections":
                dellConnection = Connection.get(Connection.id == dellId)
                dellConnection.delete_instance()
                self.connectTable()

    def initChart(self, seam):
            # 7+3(2)#получение данных
            duration = 2
            fraqency = 10
            wireConsumption = 15
            shieldingGasConsumption = 17
            weldingTime = 2.0
            # print(np.linspace(0, duration, duration * fraqency + 1))
            """y = np.ones(duration * fraqency + 1) * 13
            y2 = np.ones(duration * fraqency + 1) * 14
            y3 = np.ones(duration * fraqency + 1) * 15
            y4 = np.ones(duration * fraqency + 1) * 16
            y5 = np.ones(duration * fraqency + 1) * 17
            y6 = np.ones(duration * fraqency + 1) * 18
            y7 = np.ones(duration * fraqency + 1) * 19"""
            print(seam.torchSpeed)
            storchSpeed = struct.unpack('%sf' % (len(seam.torchSpeed)//4), seam.torchSpeed)
            sburnerOscillation = struct.unpack('%sf' % (len(seam.burnerOscillation)//4), seam.burnerOscillation)
            scurrent = struct.unpack('%sf' % (len(seam.current)//4), seam.current)
            svoltage = struct.unpack('%sf' % (len(seam.voltage)//4), seam.voltage)
            svoltageCorrection = struct.unpack('%sf' % (len(seam.voltageCorrection)//4), seam.voltageCorrection)
            swireSpeed = struct.unpack('%sf' % (len(seam.wireSpeed)//4), seam.wireSpeed)
            sgasConsumption = struct.unpack('%sf' % (len(seam.gasConsumption)//4), seam.gasConsumption)
            print(storchSpeed)
            print(sburnerOscillation)
            print(scurrent)
            print(svoltage)
            print(svoltageCorrection)
            print(swireSpeed)
            print(sgasConsumption)

            # вывод данных на график
            # рассчётные значения
            wireCC = QLineSeries()
            wireCC.setName("Рассчётный расход проволоки")
            wireCC.pressed.connect(self.on_pressed)
            gasCC = QLineSeries()
            gasCC.setName("Рассчётный расход газа")
            # реальные показатели
            # обявления
            torchSpeed = QLineSeries()
            torchSpeed.setName("Скорость горелки")
            burnerOscillation = QLineSeries()
            burnerOscillation.setName("Колебания горелки")
            current = QLineSeries()
            current.setName("Ток")
            voltage = QLineSeries()
            voltage.setName("Напряжение")
            voltageCorrection = QLineSeries()
            voltageCorrection.setName("Коррекция напряжения")
            wireSpeed = QLineSeries()
            wireSpeed.setName("Скорость подачи проволоки")
            gasConsumption = QLineSeries()
            gasConsumption.setName("Расход газа")

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
            pen = QPen(QColor(10, 255, 255))
            pen.setWidth(3)
            burnerOscillation.setPen(pen)
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

            # данные
            x = np.linspace(0, duration, duration * fraqency + 1)
            for x, y3, y4, y5, y6, y7, y8, y9 in zip(x, storchSpeed, sburnerOscillation, scurrent, svoltage, svoltageCorrection, swireSpeed, sgasConsumption):
                #gasCC.append(x, y)
                #wireCC.append(x, y2)
                torchSpeed.append(x, y3)
                burnerOscillation.append(x, y4)
                current.append(x, y5)
                voltage.append(x, y6)
                voltageCorrection.append(x, y7)
                wireSpeed.append(x, y8)
                gasConsumption.append(x, y9)

            # легенды
            self.chart = QChart()
            self.chart.setAcceptHoverEvents(True)
            self.chart.legend().setVisible(True)
            self.chart.legend().setAlignment(Qt.AlignBottom)

            # вывод на график
            if self.wireCCchb.checkState():
                self.chart.addSeries(wireCC)
            if self.gasCCchb.checkState():
                self.chart.addSeries(gasCC)
            if self.torchSpeedchb.checkState():
                self.chart.addSeries(torchSpeed)
            if self.burnerOscillationchb.checkState():
                self.chart.addSeries(burnerOscillation)
            if self.currentchb.checkState():
                self.chart.addSeries(current)
            if self.voltagechb.checkState():
                self.chart.addSeries(voltage)
            if self.voltageCorrectionchb.checkState():
                self.chart.addSeries(voltageCorrection)
            if self.wireSpeedchb.checkState():
                self.chart.addSeries(wireSpeed)
            if self.gasConsumptionchb.checkState():
                self.chart.addSeries(gasConsumption)

            font = QFont('Open Sans')
            font.setPixelSize(14)
            self.chart.setTitleFont(font)
            self.chart.setTitle('Параметры сварки')
            self.chart.createDefaultAxes()
            self.graph.setRenderHint(QPainter.Antialiasing)
            """axisX = QValueAxis()
            axisX.setLabelFormat("%f")
            axisY = QValueAxis()
            axisY.setLabelFormat("%f")
            chart.addAxis(axisX, Qt.AlignBottom)
            chart.addAxis(axisY, Qt.AlignLeft)
            series.attachAxis(axisX)
            series.attachAxis(axisY)"""
            self.graph.setChart(self.chart)

        # !!!!!!!не работает
    def on_pressed(self, point):
            print("test")
            print("on_pressed", round(point.x(), 1))

    # временная функция
    def redirect(self, n):
        imgs = b'\x00\x00\x00\x00'
        self.stackedWidget.setCurrentIndex(n)
    ####################################


    #Отображение данных в спец формах
    def protocolView(self, id):
        self.stackedWidget.setCurrentIndex(0)
        seam = Seam.get(Seam.id == id)
        print("its work", seam)
        self.connId_2.setText(str(seam.connId))
        self.detailId.setText(str(seam.detailId))
        self.batchNumber.setText(str(seam.batchNumber))
        self.detailNumber.setText(str(seam.detailNumber))
        self.authorizedUser.setText(seam.authorizedUser)
        self.weldingProgram_2.setText(seam.weldingProgram)
        self.startTime.setText(str(seam.startTime))
        self.endTime.setText(str(seam.endTime))
        self.endStatus.setCheckState(
            QtCore.Qt.Checked if seam.endStatus else QtCore.Qt.Unchecked)
        self.initChart(seam)

    def detailView(self, id):
        self.stackedWidget.setCurrentIndex(2)
        detail = Detail.get(Detail.id == id)
        self.blueprinNumber.setText(str(detail.blueprinNumber))
        self.detailName.setText(detail.detailName)
        self.materialGrade.setText(detail.materialGrade)
        self.weldingProgram.setText(detail.weldingProgram)
        self.processingTime.setValue(detail.processingTime)
        self.imgs = detail.img
        print(bi.unzip(self.imgs))
        detImg = bi.unzip(self.imgs)
        self.curImg = 0
        self.veiwDetImg()

    def ConnView(self, id):
        self.stackedWidget.setCurrentIndex(3)
        connection = Connection.get(Connection.id == id)
        self.connId.setText(str(connection.id))
        self.ctype.setText(connection.ctype)
        self.thicknessOfElement1.setValue(connection.thicknessOfElement1)
        self.thicknessOfElement2.setValue(connection.thicknessOfElement2)
        self.jointBevelling.setText(connection.jointBevelling)
        self.seamDimensions.setText(connection.seamDimensions)
        self.fillerWireMark.setText(connection.fillerWireMark)
        self.fillerWireDiam.setValue(connection.fillerWireDiam)
        self.wireConsumption.setValue(connection.wireConsumption)
        self.shieldingGasType.setText(connection.shieldingGasType)
        self.shieldingGasConsumption.setValue(connection.shieldingGasConsumption)
        self.programmName.setText(connection.programmName)
        self.weldingTime.setValue(connection.weldingTime)
    #####################################


    # Функции работы с изображениями
    def newImg(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()[0]
        f = open(filename, 'rb')
        d = f.read()
        self.imgs = bi.add(self.imgs, d)
        stream = BytesIO(d)
        im = Image.open(stream).convert("RGBA")
        stream.close()
        data = im.tobytes("raw", "BGRA")
        qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_ARGB32)
        pix = QtGui.QPixmap.fromImage(qim)
        self.DetImg.setPixmap(pix)

    def veiwNextImgD(self):
        self.curImg += 1
        self.veiwDetImg()

    def veiwPrevImgD(self):
        self.curImg -= 1
        self.veiwDetImg()

    def veiwDetImg(self):
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
            self.DetImg.setPixmap(pix)
    #########################################


    #авторизация
    def login(self):
        self.stackedWidget.setCurrentIndex(4)
        self.detailTable()
        """
        print(self.loginFld.text(), self.passFld.text())
        try:
            user = User.get(User.login == self.loginFld.text())
            if user.passWord == self.passFld.text():
                self.stackedWidget.setCurrentIndex(4)
            else:
                print("Неверный пароль")
        except:
            print("Логин не зарегистрирован")
"""
    #####################################


    #save
    def saveDeteil(self):
        try:
            Detail(blueprinNumber = int(self.blueprinNumber.text()),
            detailName = self.detailName.text(),
            materialGrade = self.materialGrade.text(),
            weldingProgram = self.weldingProgram.text(),
            processingTime = float(self.processingTime.text().replace(',','.')),
            img = self.imgs).save()
        except:
            print("не создано")

    def saveConnChlngs(self):
        print("save conn")
        try:
            Connection(ctype = self.ctype.text(),#CharField()
            thicknessOfElement1 = float(self.thicknessOfElement1.text().replace(',','.')),#DoubleField()
            thicknessOfElement2 = float(self.thicknessOfElement2.text().replace(',','.')),#DoubleField()
            jointBevelling = self.jointBevelling.text(),#CharField()
            jointBevellingImg = self.imgs,#BlobField()
            seamDimensions = self.seamDimensions.text(),#CharField()
            fillerWireMark = self.fillerWireMark.text(),#CharField()
            fillerWireDiam = float(self.fillerWireDiam.text().replace(',','.')),#DoubleField()
            wireConsumption = float(self.wireConsumption.text().replace(',','.')),#DoubleField()
            shieldingGasType = self.shieldingGasType.text(),#CharField()
            shieldingGasConsumption = float(self.shieldingGasConsumption.text().replace(',','.')),#DoubleField()
            programmName = self.programmName.text(),#CharField()
            weldingTime = float(self.weldingTime.text().replace(',','.'))).save()#DoubleField()
        except:
            print("не создано")
    #####################################


    #Функции вывода таблиц данных
    #Панель администрирования данных
    def adpanel(self, otype):
        self.otype = otype
        self.chooseTable()
        self.stackedWidget.setCurrentIndex(4)
    #Выбор отображения от типа данных
    def chooseTable(self):
        self.tableWidget.clear()
        if self.otype == "user":
            self.userTable()
        elif self.otype == "detail":
            self.detailTable()
        elif self.otype == "connections":
            self.connectTable()
        elif self.otype == "realDetail":
            self.realDetailTable()
        elif self.otype == "seams":
            self.seamTable()
    #вывод табиц администрирования
    def detailTable(self):
        self.adPanelName.setText("Панель управления чертежами:")
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["id", "Номер чертежа", "Наименование", "Марка материала","Программа сварки","Время обработки"])
        details = Detail.select()
        self.tableWidget.setRowCount(len(details))
        for i in range(len(details)):
            self.tableWidget.setItem(i, 0, twi(str(details[i].id)))
            self.tableWidget.setItem(i, 1, twi(str(details[i].blueprinNumber)))
            self.tableWidget.setItem(i, 2, twi(details[i].detailName))
            self.tableWidget.setItem(i, 3, twi(details[i].materialGrade))
            self.tableWidget.setItem(i, 4, twi(details[i].weldingProgram))
            self.tableWidget.setItem(i, 5, twi(str(details[i].processingTime)))
        self.tableWidget.resizeColumnsToContents()

    def realDetailTable(self):
        self.adPanelName.setText("Панель управления деталями:")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Номер чертежа", "Наименование","Номер партии", "Номер детали"])
        details = Detail.select()
        self.tableWidget.setRowCount(len(details))
        for i in range(len(details)):
            self.tableWidget.setItem(i, 0, twi(str(details[i].blueprinNumber)))
            self.tableWidget.setItem(i, 1, twi(details[i].detailName))
        self.tableWidget.resizeColumnsToContents()

    def userTable(self):
        self.adPanelName.setText("Панель управления пользователями:")
        self.tableWidget.setColumnCount(11)
        self.tableWidget.setHorizontalHeaderLabels(
            ["id", "Логин", "Имя", "Пароль", "Пользователи", "Детали", "Соединения", "Протоколы", "Архивы", "Добавление", "Удаление"])
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

        self.tableWidget.resizeColumnsToContents()

    def connectTable(self):
        self.adPanelName.setText("Панель управления соединениями:")
        self.tableWidget.setColumnCount(11)
        self.tableWidget.setHorizontalHeaderLabels(
            ["id", "Вид сварного соединения", "Толщина элементов", "Разделка кромок", "Размеры шва", "Марка/сечение проволоки", "Расход проволоки","Газ","Расход газа","Программа сварки","Рассчётное время"])
        connections = Connection.select()
        self.tableWidget.setRowCount(len(connections))
        for i in range(len(connections)):
            self.tableWidget.setItem(i, 0, twi(str(connections[i].id)))
            self.tableWidget.setItem(i, 1, twi(connections[i].ctype))
            self.tableWidget.setItem(i, 2, twi(str(connections[i].thicknessOfElement1)+'/'+str(connections[i].thicknessOfElement2)))
            self.tableWidget.setItem(i, 3, twi(connections[i].jointBevelling))
            self.tableWidget.setItem(i, 4, twi(connections[i].seamDimensions))
            self.tableWidget.setItem(i, 5, twi(connections[i].fillerWireMark+'/'+str(connections[i].fillerWireDiam)))
            self.tableWidget.setItem(i, 6, twi(str(connections[i].wireConsumption)))
            self.tableWidget.setItem(i, 7, twi(connections[i].shieldingGasType))
            self.tableWidget.setItem(i, 8, twi(str(connections[i].shieldingGasConsumption)))
            self.tableWidget.setItem(i, 9, twi(connections[i].programmName))
            self.tableWidget.setItem(i, 10, twi(str(connections[i].weldingTime)))
        self.tableWidget.resizeColumnsToContents()

    def seamTable(self):
        self.adPanelName.setText("Панель управления швами:")
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setHorizontalHeaderLabels(
            ["id", "Тип соединения", "Тип детали", "Номер партии", "Номер детали", "Начало", "Окончание", "Статус",
             "Программа сварки", "Пользователь"])
        seams = Seam.select()
        self.tableWidget.setRowCount(len(seams))
        for i in range(len(seams)):
            self.tableWidget.setItem(i, 0, twi(str(seams[i].id)))
            self.tableWidget.setItem(i, 1, twi(str(seams[i].connId)))
            self.tableWidget.setItem(i, 2, twi(str(seams[i].detailId)))
            self.tableWidget.setItem(i, 3, twi(str(seams[i].batchNumber)))
            self.tableWidget.setItem(i, 4, twi(str(seams[i].detailNumber)))
            self.tableWidget.setItem(i, 5, twi(str(seams[i].startTime)))
            self.tableWidget.setItem(i, 6, twi(str(seams[i].endTime)))
            if seams[i].endStatus:
                self.tableWidget.setItem(i, 7, twi("Успешно"))
            else:
                self.tableWidget.setItem(i, 7, twi("Ошибка!"))
            self.tableWidget.setItem(i, 8, twi(seams[i].weldingProgram))
            self.tableWidget.setItem(i, 9, twi(seams[i].authorizedUser))
        self.tableWidget.resizeColumnsToContents()
    #######################################


app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = UImodif()
ui.setupUi(MainWindow)
ui.btnFunction()
MainWindow.show()
sys.exit(app.exec_())