#всплывающие окна
from PyQt5 import QtCore, QtGui, QtWidgets
from GUI import *
from connWin import *
from selectUI import *
from timePdf import *
from settings import *

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
                if seams[i].endStatus == 0:
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
            if (self.mainUi.batchNumber_2.text() != "" and
                self.mainUi.numberInBatch.text() != "" and
                self.mainUi.blprName.text() != ""):
                self.mainUi.realDetailUpdate()
                addInd = []
                for ind in self.ui.listOfConn.selectedIndexes():
                    if ind.row() not in addInd:
                        addInd.append(ind.row())
                for ind in addInd:
                    print(self.ui.listOfConn.item(ind, 0).text())
                    query = Seam.update(
                        batchNumber = self.mainUi.batchNumber_2.text(),
                        detailNumber = self.mainUi.numberInBatch.text(),
                        #detailId = detId,
                        realDetId = self.mainUi.curId).where(
                        Seam.id == int(self.ui.listOfConn.item(ind, 0).text()))
                    query.execute()
                self.mainUi.realDetailView(self.mainUi.curId)
            else:
                self.mainUi.statusBar.showMessage("Заполните данные по детали", 3000)
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
        elif self.dataType == 'realDetail':
            self.ui.chooseTable.setColumnCount(4)
            self.ui.chooseTable.setHorizontalHeaderLabels(
                ["id", "Партия", "Номер детали", "Чертёж"])
            details = RealDetail.select()
            self.ui.chooseTable.setRowCount(len(details))
            for i in range(len(details)):
                self.ui.chooseTable.setItem(i, 0, twi(str(details[i].id)))
                self.ui.chooseTable.setItem(i, 1, twi(details[i].batchNumber))
                self.ui.chooseTable.setItem(i, 2, twi(details[i].detailNumber))
                self.ui.chooseTable.setItem(i, 3, twi(details[i].detailId.detailName if details[i].detailId else "Не присвоен"))
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
                if self.seamId is None:
                    #self.mainUi.curId = id
                    det = Detail.get(Detail.id == id)
                    self.mainUi.blprName.setText(det.detailName)
                    self.mainUi.imgs = det.img
                    self.mainUi.curImg = 0
                    self.mainUi.veiwImg(self.mainUi.dateilImg)
                    self.close()
                    return
                else:
                    query = Seam.update(detailId=id, connId=None).where(
                        Seam.id == self.seamId)
                    query.execute()
            elif self.dataType == 'connection':
                query = Seam.update(connId=id).where(
                    Seam.id == self.seamId)
                query.execute()
            elif self.dataType == 'realDetail':
                realDet = RealDetail.get(RealDetail.id == id)
                query = Seam.update(realDetId = id, batchNumber = realDet.batchNumber, detailNumber = realDet.detailNumber,
                                    detailId = realDet.detailId).where(
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
