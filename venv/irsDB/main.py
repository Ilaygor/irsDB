import datetime
import peewee
from models import *
from GUI import *
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem as twi
from PIL import Image, ImageQt
#pyuic5 -x base.ui -o gui.py


with db:
    db.create_tables([User, Detail, Connection, Seam])

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


class UImodif(Ui_MainWindow):

    otype = ""
    imgs = []

    def btnFunction(self):
        self.loginBtn.clicked.connect(self.login)
        self.addBtn.clicked.connect(lambda: self.redirect(2))
        self.addDetImg.clicked.connect(self.newImg)
        self.saveChalenges.clicked.connect(self.saveDeteil)
        self.makePdf.clicked.connect(lambda: print("pdf"))


        self.exit.triggered.connect(lambda: self.redirect(1))
        self.detail.triggered.connect(lambda: self.adpanel("detail"))
        self.connections.triggered.connect(lambda: self.adpanel("connections"))
        self.realDetail.triggered.connect(lambda: self.adpanel("realDetail"))
        self.seams.triggered.connect(lambda: self.adpanel("seams"))
        self.users.triggered.connect(lambda: self.adpanel("user"))


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

    def adpanel(self, otype):
        self.otype = otype
        self.chooseTable()
        self.stackedWidget.setCurrentIndex(4)

    def redirect(self, n):
        self.stackedWidget.setCurrentIndex(n)

    def newImg(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()[0]
        img = Image.open(filename)

        self.imgs.append(img)
        qim = ImageQt.ImageQt(img)
        pix = QtGui.QPixmap.fromImage(qim)
        self.DetImg.setPixmap(pix)
        print(img)

    def saveDeteil(self):
        print("ok")
        try:
            blueprinNumber = int(self.blueprinNumber.text())
            detailName = self.detailName.text()
            materialGrade = self.materialGrade.text()
            weldingProgram = self.weldingProgram.text()
            processingTime = float(self.processingTime.text().replace(',','.'))
        except:
            print("Для добавления заполните все поля!")
        try:
            Detail(blueprinNumber = blueprinNumber, detailName = detailName, materialGrade = materialGrade,
               weldingProgram = weldingProgram, processingTime = processingTime, img = 1).save()
        except:
            print("не создано")

    def detailTable(self):
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

    def userTable(self):
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
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Вид сварного соединения", "Толщина элементов", "Разделка кромок", "Размеры шва", "Марка/сечение проволоки", "Расход проволоки","Газ","Расход газа","Программа сварки","Рассчётное время"])
        connections = Connection.select()
        self.tableWidget.setRowCount(len(connections))
        for i in range(len(connections)):
            self.tableWidget.setItem(i, 0, twi(connections[i].ctype))
            self.tableWidget.setItem(i, 1, twi(connections[i].thicknessOfElement1+connections[i].thicknessOfElement2))
            self.tableWidget.setItem(i, 2, twi(connections[i].jointBevelling))
            self.tableWidget.setItem(i, 3, twi(connections[i].seamDimensions))
            self.tableWidget.setItem(i, 4, twi(connections[i].fillerWireMark+connections[i].fillerWireDiam))
            self.tableWidget.setItem(i, 5, twi(connections[i].wireConsumption))
            self.tableWidget.setItem(i, 6, twi(connections[i].shieldingGasType))
            self.tableWidget.setItem(i, 7, twi(connections[i].shieldingGasConsumption))
            self.tableWidget.setItem(i, 8, twi(connections[i].programmName))
            self.tableWidget.setItem(i, 9, twi(connections[i].weldingTime))
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

    def chooseTable(self):
        self.tableWidget.clear()
        if self.otype == "user":
            self.userTable()
        elif self.otype == "detail":
            self.detailTable()
        elif self.otype == "connections":
            self.connectTable()


app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = UImodif()
ui.setupUi(MainWindow)
ui.btnFunction()
MainWindow.show()
sys.exit(app.exec_())