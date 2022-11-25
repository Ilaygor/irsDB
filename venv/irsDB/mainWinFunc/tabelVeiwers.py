#Функции вывода таблиц данных
from mainWinFunc.models import *
from PyQt5.QtWidgets import QTableWidgetItem as twi
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QPen, QFont, Qt, QSize
import mainWinFunc.OPCclient as opcc
print("opc ok")

def adpanel(self, otype):
    self.otype = otype
    self.toolBar.hide()
    self.tableWidget.clear()
    self.saveBtn.setEnabled(True)
    if self.otype == "user":
        try:
            self.saveBtn.setEnabled(self.AfUser.accessUser)
            userTable(self)
        except:
            pass
    elif self.otype == "blueprint":
        detailTable(self)
    elif self.otype == "connections":
        connectTable(self)
    elif self.otype == "realDetail":
        realDetailTable(self)
    elif self.otype == "seams":
        veiwSeamTable(self)
    elif self.otype == "equipments":
        try:
            self.saveBtn.setEnabled(self.AfUser.accessEquipment)
            equipmentTable(self)
        except:
            pass
    elif self.otype == "oscilation":
        try:
            self.saveBtn.setEnabled(self.AfUser.accessOscilationType)
            oscilationTable(self)
        except:
            pass
    self.tableWidget.hideColumn(0)
    self.stackedWidget.setCurrentIndex(4)


# !!!############### вывод табиц администрирования
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
            #print("new harvestr")
            self.HarvestrDict[ip] = opcc.DataHarvestr(ip, self.statusBar, self.AfUser.id)
            self.HarvestrDict[ip].start()
        if self.HarvestrDict[ip].active:
            self.tableWidget.item(ind.row(), 9).setText("Подключено")
            self.tableWidget.item(ind.row(), 9).setBackground(Qt.green)
    except:
        self.statusBar.showMessage("Нет подключения к: " + ip, 3000)

def robDisconnect(self):
    btn = self.app.focusWidget()
    ind = self.tableWidget.indexAt(btn.pos())
    ip = self.tableWidget.item(ind.row(), 4).text()
    if ip in self.HarvestrDict:
        self.HarvestrDict[ip].stop()
    self.statusBar.showMessage("Отключение от: " + ip, 3000)
    ###
    try:
        self.tableWidget.item(ind.row(), 9).setText("Нет подключения")
        self.tableWidget.item(ind.row(), 9).setBackground(Qt.red)
    except:
        pass

def equipmentTable(self):
    self.adPanelName.setText("Панель управления комплексами:")
    self.tableWidget.setColumnCount(10)
    self.tableWidget.setHorizontalHeaderLabels(
        ["id", "Серийный номер", "Наименование", "Модель", "IP", "Порт", "Период", "Подключение", "Отключение",
         "Статус"])
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
        self.tableWidget.cellWidget(i, 7).clicked.connect(lambda: robConnect(self))
        self.tableWidget.setCellWidget(i, 8, QtWidgets.QPushButton("Отключиться"))
        self.tableWidget.cellWidget(i, 8).clicked.connect(lambda: robDisconnect(self))
        harv = equipments[i].ip in self.HarvestrDict
        if harv:
            print(self.HarvestrDict[equipments[i].ip].active)
            if self.HarvestrDict[equipments[i].ip].active:
                self.tableWidget.setItem(i, 9, twi("Подключено"))
                self.tableWidget.item(i, 9).setBackground(Qt.green)
            else:
                self.tableWidget.setItem(i, 9, twi("Нет подключения"))
                self.tableWidget.item(i, 9).setBackground(Qt.red)
        else:
            self.tableWidget.setItem(i, 9, twi("Нет подключения"))
            self.tableWidget.item(i, 9).setBackground(Qt.red)
    self.tableWidget.resizeColumnsToContents()

def detailTable(self):
    self.adPanelName.setText("Панель управления чертежами:")
    self.tableWidget.setColumnCount(6)
    self.tableWidget.setHorizontalHeaderLabels(
        ["id", "Номер чертежа", "Наименование", "Марка материала", "Программа сварки", "Расчётное время"])
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
    self.tableWidget.setHorizontalHeaderLabels(["id", "Номер чертежа", "Наименование", "Номер партии", "Номер детали"])
    details = RealDetail.select()
    self.tableWidget.setRowCount(len(details))
    voidRow = None
    for i in range(len(details)):
        if details[i].batchNumber != "" and details[i].detailNumber != "":
            self.tableWidget.setItem(i, 0, twi(str(details[i].id)))
            #print("details[i].id ", details[i].id)
            self.tableWidget.setItem(i, 1,
                                     twi(details[i].detailId.blueprinNumber if details[i].detailId else "Не присвоен"))
            self.tableWidget.setItem(i, 2, twi(str(details[i].detailId.detailName if details[i].detailId else "")))
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
        #print(users[i].name)
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
        ["id", "Вид соединения", "Толщина элементов", "Разделка кромок", "Размеры шва с допусками",
         "Марка/сечение проволоки", "Расход проволоки [м/мин]", "Защитный газ", "Расход газа [л/мин]",
         "Программа сварки", "Расчётное время", "Предпочтительное частота сбора данных [с]"])
    connections = Connection.select()
    self.tableWidget.setRowCount(len(connections))
    for i in range(len(connections)):
        self.tableWidget.setItem(i, 0, twi(str(connections[i].id)))
        self.tableWidget.setItem(i, 1, twi(connections[i].ctype))
        self.tableWidget.setItem(i, 2, twi(connections[i].thicknessOfElement))
        self.tableWidget.setItem(i, 3, twi(connections[i].jointBevelling))
        self.tableWidget.setItem(i, 4, twi(connections[i].seamDimensions))
        self.tableWidget.setItem(i, 5, twi(connections[i].fillerWireMark + '/' + str(connections[i].fillerWireDiam)))
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
        ["id", "Тип соединения", "Тип детали", "Номер партии", "Номер детали", "Начало", "Окончание", "Статус",
         "Установка",
         "Программа сварки", "Пользователь"])
    seams = Seam.select().order_by(SQL('startTime').desc())
    self.tableWidget.setRowCount(len(seams))
    for i in range(len(seams)):
        self.tableWidget.setItem(i, 0, twi(str(seams[i].id)))
        if seams[i].connId is not None:
            self.tableWidget.setItem(i, 1, twi(str(seams[i].connId.ctype)))
        #print(seams[i].detailId)
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

def backToTable(self):
    self.toolBar.hide()
    adpanel(self, self.otype)