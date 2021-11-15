import datetime
import peewee
from models import *
from GUI import *
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
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
    def btnFunction(self):
        self.loginBtn.clicked.connect(self.login)
        self.addBtn.clicked.connect(lambda: self.redirect(2))
        self.addDetImg.clicked.connect(self.newImg)
        self.saveChalenges.clicked.connect(self.saveDeteil)


    def login(self):
        self.stackedWidget.setCurrentIndex(4)
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





