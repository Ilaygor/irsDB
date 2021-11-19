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


#pyuic5 -x base.ui -o gui.py


with db:
    db.create_tables([Seam])

    db.commit()
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
    imgs = []

    #инициализация функций нажатий
    def btnFunction(self):
        #книпки
        self.loginBtn.clicked.connect(self.login)
        self.addBtn.clicked.connect(self.add)
        self.addDetImg.clicked.connect(self.newImg)
        self.saveChalenges.clicked.connect(self.saveDeteil)
        self.saveConn.clicked.connect(self.saveConnChlngs)
        self.makePdf.clicked.connect(lambda: print("pdf"))

        #пункты меню
        self.exit.triggered.connect(lambda: self.redirect(1))
        self.detail.triggered.connect(lambda: self.adpanel("detail"))
        self.connections.triggered.connect(lambda: self.adpanel("connections"))
        self.realDetail.triggered.connect(lambda: self.adpanel("realDetail"))
        self.seams.triggered.connect(lambda: self.adpanel("seams"))
        self.users.triggered.connect(lambda: self.adpanel("user"))

        #перерисовка и инициализация графика
        self.wireCCchb.stateChanged.connect(self.initChart)
        self.gasCCchb.stateChanged.connect(self.initChart)
        self.torchSpeedchb.stateChanged.connect(self.initChart)
        self.burnerOscillationchb.stateChanged.connect(self.initChart)
        self.currentchb.stateChanged.connect(self.initChart)
        self.voltagechb.stateChanged.connect(self.initChart)
        self.voltageCorrectionchb.stateChanged.connect(self.initChart)
        self.wireSpeedchb.stateChanged.connect(self.initChart)
        self.gasConsumptionchb.stateChanged.connect(self.initChart)
        self.initChart()

    #######Область тестовых функций########
    def add(self):
        if self.otype == "user":
            pass
        elif self.otype == "detail":
            self.redirect(2)
        elif self.otype == "connections":
            self.redirect(3)
        elif self.otype == "realDetail":
            self.redirect(2)
        elif self.otype == "seams":
            pass
        # отрисовка графиков протоколов
    def initChart(self):
            # 7+3(2)#получение данных
            duration = 2
            fraqency = 10
            wireConsumption = 10
            shieldingGasConsumption = 15
            weldingTime = 2.0
            # print(np.linspace(0, duration, duration * fraqency + 1))
            data = []
            y = np.ones(duration * fraqency + 1) * 13
            y2 = np.ones(duration * fraqency + 1) * 14
            y3 = np.ones(duration * fraqency + 1) * 15
            y4 = np.ones(duration * fraqency + 1) * 16
            y5 = np.ones(duration * fraqency + 1) * 17
            y6 = np.ones(duration * fraqency + 1) * 18
            y7 = np.ones(duration * fraqency + 1) * 19

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
            for x, y, y2, y3, y4, y5, y6, y7 in zip(x, y, y2, y3, y4, y5, y6, y7):
                gasCC.append(x, y)
                wireCC.append(x, y2)
                torchSpeed.append(x, y3)
                burnerOscillation.append(x, y4)
                current.append(x, y5)
                voltage.append(x, y6)
                voltageCorrection.append(x, y7)
                wireSpeed.append(x, y6)
                gasConsumption.append(x, y7)

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
            self.stackedWidget.setCurrentIndex(n)
    ###############

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

    def newImg(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()[0]
        img = Image.open(filename)

        self.imgs.append(img)
        qim = ImageQt.ImageQt(img)
        pix = QtGui.QPixmap.fromImage(qim)
        self.DetImg.setPixmap(pix)
        print(img)

    #####################################
    def saveDeteil(self):
        try:
            Detail(blueprinNumber = int(self.blueprinNumber.text()),
            detailName = self.detailName.text(),
            materialGrade = self.materialGrade.text(),
            weldingProgram = self.weldingProgram.text(),
            processingTime = float(self.processingTime.text().replace(',','.')),
            img = 1).save()
        except:
            print("не создано")

    def saveConnChlngs(self):
        print("save conn")
        try:
            Connection(ctype = self.ctype.text(),#CharField()
            thicknessOfElement1 = float(self.thicknessOfElement1.text().replace(',','.')),#DoubleField()
            thicknessOfElement2 = float(self.thicknessOfElement2.text().replace(',','.')),#DoubleField()
            jointBevelling = self.jointBevelling.text(),#CharField()
            jointBevellingImg = 1,#BlobField()
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

    def saveUser(self):
        try:
            Detail(login = "admin2",
            name = "admin2",
            passWord = "admin2").save()
        except:
            print("не создано")

    #####################################
    def adpanel(self, otype):
        self.otype = otype
        self.chooseTable()
        self.stackedWidget.setCurrentIndex(4)

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
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Номер чертежа", "Наименование", "Марка материала","Программа сварки","Время обработки"])
        details = Detail.select()
        self.tableWidget.setRowCount(len(details))
        for i in range(len(details)):
            self.tableWidget.setItem(i, 0, twi(str(details[i].blueprinNumber)))
            self.tableWidget.setItem(i, 1, twi(details[i].detailName))
            self.tableWidget.setItem(i, 2, twi(details[i].materialGrade))
            self.tableWidget.setItem(i, 3, twi(details[i].weldingProgram))
            self.tableWidget.setItem(i, 4, twi(str(details[i].processingTime)))
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
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Логин", "Имя", "Пароль", "Пользователи", "Детали", "Соединения", "Протоколы", "Архивы", "Добавление", "Удаление"])
        users = User.select()
        self.tableWidget.setRowCount(len(users))
        for i in range(len(users)):
            print(users[i].name)
            self.tableWidget.setItem(i, 0, twi(users[i].login))
            self.tableWidget.setItem(i, 1, twi(users[i].name))
            self.tableWidget.setItem(i, 2, twi(users[i].passWord))
            self.tableWidget.setCellWidget(i, 3, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 4, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 5, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 6, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 7, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 8, QtWidgets.QCheckBox())
            self.tableWidget.setCellWidget(i, 9, QtWidgets.QCheckBox())
            self.tableWidget.cellWidget(i, 3).setCheckState(
                QtCore.Qt.Checked if users[i].accessUser else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 4).setCheckState(
                QtCore.Qt.Checked if users[i].accessDetail else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 5).setCheckState(
                QtCore.Qt.Checked if users[i].accessConn else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 6).setCheckState(
                QtCore.Qt.Checked if users[i].accessProt else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 7).setCheckState(
                QtCore.Qt.Checked if users[i].accessArch else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 8).setCheckState(
                QtCore.Qt.Checked if users[i].accessAdd else QtCore.Qt.Unchecked)
            self.tableWidget.cellWidget(i, 9).setCheckState(
                QtCore.Qt.Checked if users[i].accessRemove else QtCore.Qt.Unchecked)

        self.tableWidget.resizeColumnsToContents()

    def connectTable(self):
        self.adPanelName.setText("Панель управления соединениями:")
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Вид сварного соединения", "Толщина элементов", "Разделка кромок", "Размеры шва", "Марка/сечение проволоки", "Расход проволоки","Газ","Расход газа","Программа сварки","Рассчётное время"])
        connections = Connection.select()
        print(connections)
        self.tableWidget.setRowCount(len(connections))
        for i in range(len(connections)):
            self.tableWidget.setItem(i, 0, twi(connections[i].ctype))
            self.tableWidget.setItem(i, 1, twi(str(connections[i].thicknessOfElement1)+'/'+str(connections[i].thicknessOfElement2)))
            self.tableWidget.setItem(i, 2, twi(connections[i].jointBevelling))
            self.tableWidget.setItem(i, 3, twi(connections[i].seamDimensions))
            self.tableWidget.setItem(i, 4, twi(connections[i].fillerWireMark+'/'+str(connections[i].fillerWireDiam)))
            self.tableWidget.setItem(i, 5, twi(str(connections[i].wireConsumption)))
            self.tableWidget.setItem(i, 6, twi(connections[i].shieldingGasType))
            self.tableWidget.setItem(i, 7, twi(str(connections[i].shieldingGasConsumption)))
            self.tableWidget.setItem(i, 8, twi(connections[i].programmName))
            self.tableWidget.setItem(i, 9, twi(str(connections[i].weldingTime)))
        self.tableWidget.resizeColumnsToContents()
        """ctype = CharField()
        thicknessOfElement1 = DoubleField()
        thicknessOfElement2 = DoubleField()
        jointBevelling = CharField()
        jointBevellingImg = BlobField()
        seamDimensions = CharField()
        fillerWireMark = CharField()
        fillerWireDiam = DoubleField()
        wireConsumption = DoubleField()
        shieldingGasType = CharField()
        shieldingGasConsumption = DoubleField()
        programmName = CharField()
        weldingTime = DoubleField()"""

    def seamTable(self):
        self.adPanelName.setText("Панель управления швами:")
        self.tableWidget.setColumnCount(9)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Тип соединения", "Тип детали", "Номер партии", "Номер детали", "Начало", "Окончание", "Статус",
             "Программа сварки", "Пользователь"])
        details = Detail.select()
        self.tableWidget.setRowCount(len(details))
        for i in range(len(details)):
            self.tableWidget.setItem(i, 0, twi(str(details[i].blueprinNumber)))
            self.tableWidget.setItem(i, 1, twi(details[i].detailName))
            self.tableWidget.setItem(i, 2, twi(details[i].materialGrade))
            self.tableWidget.setItem(i, 3, twi(details[i].weldingProgram))
            self.tableWidget.setItem(i, 4, twi(str(details[i].processingTime)))
        self.tableWidget.resizeColumnsToContents()





app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = UImodif()
ui.setupUi(MainWindow)
ui.btnFunction()
MainWindow.show()
sys.exit(app.exec_())