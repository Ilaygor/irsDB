# авторизация
from mainWinFunc.models import *


def makeEnable(self, accessUser, accessDetail, accessConn,
               accessProt, accessAdd, accessRemove):
    #self.adpanel("blueprint")

    self.users.setEnabled(accessUser)

    self.delDetImg.setEnabled(accessDetail)
    self.addDetImg.setEnabled(accessDetail)
    self.blueprinNumber.setEnabled(accessDetail)
    self.detailName.setEnabled(accessDetail)
    self.materialGrade.setEnabled(accessDetail)
    self.weldingProgram.setEnabled(accessDetail)
    self.addConnection.setEnabled(accessDetail)
    self.saveChalenges.setEnabled(accessDetail)
    self.HprocessingTime.setEnabled(accessDetail)
    self.MprocessingTime.setEnabled(accessDetail)
    self.SprocessingTime.setEnabled(accessDetail)

    self.batchNumber_2.setEnabled(accessDetail)
    self.numberInBatch.setEnabled(accessDetail)
    self.chooseBlueprintBtn.setEnabled(accessDetail)
    self.DetailSeamsSave.setEnabled(accessDetail)
    self.addSeamBtn.setEnabled(accessDetail)
    self.delSeamBtn.setEnabled(accessDetail)

    self.connId.setEnabled(accessConn)
    self.ctype.setEnabled(accessConn)
    self.thicknessOfElement.setEnabled(accessConn)
    self.jointBevelling.setEnabled(accessConn)
    self.seamDimensions.setEnabled(accessConn)
    self.fillerWireMark.setEnabled(accessConn)
    self.fillerWireDiam.setEnabled(accessConn)
    self.wireConsumption.setEnabled(accessConn)
    self.shieldingGasType.setEnabled(accessConn)
    self.shieldingGasConsumption.setEnabled(accessConn)
    self.programmName.setEnabled(accessConn)
    self.HweldingTime.setEnabled(accessConn)
    self.MweldingTime.setEnabled(accessConn)
    self.SweldingTime.setEnabled(accessConn)
    self.saveConn.setEnabled(accessConn)
    self.delConnImg.setEnabled(accessConn)
    self.newConnImg.setEnabled(accessConn)
    self.preferredPeriod.setEnabled(accessConn)

    self.chooseEqvipment.setEnabled(accessProt)
    self.batchNumber.setEnabled(accessProt)
    self.detailNumber.setEnabled(accessProt)
    self.startTime.setEnabled(accessProt)
    self.endTime.setEnabled(accessProt)
    self.endStatus.setEnabled(accessProt)
    self.oscType.setEnabled(accessProt)
    self.seamPeriod.setEnabled(accessProt)
    self.chooseUser.setEnabled(accessProt)
    self.chooseBlueprint.setEnabled(accessProt)
    self.chooseConn.setEnabled(accessProt)
    self.weldingProgram_2.setEnabled(accessProt)
    self.saveProtocolBtn.setEnabled(accessProt)

    self.addBtn.setEnabled(accessAdd)

    self.delBtn.setEnabled(accessRemove)

def login(self):
    #print(self.loginFld.text(), self.passFld.text())
    try:
        user = User.get(User.login == self.loginFld.text())
        if user.passWord == self.passFld.text():
            self.stackedWidget.setCurrentIndex(4)
            self.menubar.show()

            self.AfUser = user

            self.centralwidget.setStyleSheet("")

            makeEnable(self, self.AfUser.accessUser, self.AfUser.accessDetail, self.AfUser.accessConn,
                            self.AfUser.accessProt, self.AfUser.accessAdd, self.AfUser.accessRemove)
        else:
            self.statusBar.showMessage("Неверный пароль", 4000)
    except:
        self.statusBar.showMessage("Логин не зарегистрирован", 4000)

def exitf(self):
    self.centralwidget.setStyleSheet("background-color:white;")
    self.AfUser = None
    self.menubar.hide()
    self.toolBar.hide()
    for harvestr in self.HarvestrDict:
        HarvestrDict[harvestr].stop
    self.HarvestrDict = {}
    self.redirect(1)

def test():
    print("it work")