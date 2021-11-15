from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()

        self.setWindowTitle("IRS Протокол параметров сварки")
        self.setGeometry(0, 0, 500, 500)


def window():
    app = QApplication(sys.argv)
    win = GUI()




    win.show()
    sys.exit(app.exec_())



if __name__ =="__main__":
    window()