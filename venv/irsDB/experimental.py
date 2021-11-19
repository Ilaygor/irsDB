"""import sys
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QPointF, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow

class ReleasePosEvent(QEvent):
    EventType = QEvent.Type(QEvent.registerEventType())
    def __init__(self, point):
        QEvent.__init__(self, ReleasePosEvent.EventType)
        self.point = point


class ChartView(QChartView):
    def mouseReleaseEvent(self, event):
        p1 = event.pos()
        p2 = self.mapToScene(p1)
        p3 = self.chart().mapFromScene(p2)
        p4 = self.chart().mapToValue(p3)
        if self.chart():
            for serie in self.chart().series():
                QApplication.postEvent(serie, ReleasePosEvent(p4))
        QChartView.mouseReleaseEvent(self, event)


class LineSeries(QLineSeries):
    def __init__(self, *args, **kwargs):
        QLineSeries.__init__(self, *args, **kwargs)
        self.start = QPointF()
        self.pressed.connect(self.on_pressed)

    def on_pressed(self, point):
        self.start = point
        print("on_pressed", point)

    def shift(self, delta):
        if not delta.isNull():
            for ix in range(self.count()):
                p = self.at(ix)
                p += delta
                self.replace(ix, p)

    def customEvent(self, event):
        if event.type() == ReleasePosEvent.EventType:
            if not self.start.isNull():
                dpoint = event.point - self.start
                self.shift(dpoint)
                self.start = QPointF()

app = QApplication(sys.argv)
series0 = LineSeries()

series0 << QPointF(1, 15) << QPointF(3, 17) << QPointF(7, 16) << QPointF(9, 17) \
        << QPointF(12, 16) << QPointF(16, 17) << QPointF(18, 15)

chart = QChart()
chart.addSeries(series0)
chart.createDefaultAxes()
chartView = ChartView(chart)

window = QMainWindow()
window.setCentralWidget(chartView)
window.resize(400, 300)
window.show()

sys.exit(app.exec_())"""


import threading

def printit():
  threading.Timer(1.0, printit).start()
  print("Hello, World!")

printit()
