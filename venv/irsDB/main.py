import datetime
import peewee
from models import *
from GUI import *
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem as twi
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


class UImodif(Ui_MainWindow):

    otype = "user"

    def btnFunction(self):
        self.loginBtn.clicked.connect(self.login)
        self.addBtn.clicked.connect(lambda: self.redirect(2))
        self.addDetImg.clicked.connect(self.newImg)
        self.saveChalenges.clicked.connect(self.saveDeteil)


    def login(self):
        self.stackedWidget.setCurrentIndex(4)
        self.usrTable()
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


    def redirect(self, n):
        if self.otype == "user":
            print("user")

        else:
            self.stackedWidget.setCurrentIndex(n)


    def newImg(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()[0]
        print(filename)
        self.DetImg.setPixmap(QtGui.QPixmap(filename))

    def saveDeteil(self):
        print("ok")
        blueprinNumber = int(self.blueprinNumber.text())
        detailName = self.detailName.text()
        materialGrade = self.materialGrade.text()
        weldingProgram = self.weldingProgram.text()
        processingTime = float(self.processingTime.text().replace(',','.'))
        print(blueprinNumber, detailName, materialGrade, weldingProgram, processingTime)
        try:
            Detail(blueprinNumber = blueprinNumber, detailName = detailName, materialGrade = materialGrade,
               weldingProgram = weldingProgram, processingTime = processingTime, img = 1).save()
        except:
            print("не создано")

    def table(self):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Номер чертежа", "Наименование", "Марка материала","Программа сварки","Время обработки"])
        details = Detail.select()
        self.tableWidget.setRowCount(len(details))
        for detail in details:
            print(detail.detailName)
        self.tableWidget.resizeColumnsToContents()

    def usrTable(self):
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




with db:
    #db.create_tables([User, Detail, Connection, Seam])
    #User(login="admin", passWord="admin", name="admin").save()
    db.commit()



app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = UImodif()
ui.setupUi(MainWindow)
ui.btnFunction()
MainWindow.show()
sys.exit(app.exec_())





