from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.platypus.flowables import Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.graphics import shapes
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.textlabels import Label

from mainWinFunc.models import Seam, Detail, RealDetail
from io import BytesIO
import numpy as np
import byteimgs as bi
import struct

from PIL import Image as plimg

import datetime
########################################################################
class Bookmark(Flowable):
	def __init__(self, title, key):
		self.title = title
		self.key = key
		Flowable.__init__(self)

	def wrap(self, availWidth, availHeight):
		return (1, 1)

	def draw(self):
		self.canv.showOutline()
		#self.canv.drawString(0,0,"seam")
		print(self.key)
		self.canv.bookmarkPage(self.key)
		self.canv.addOutlineEntry(self.title, self.key, 0, 0)

class PageNumCanvas(canvas.Canvas):
    """
    http://code.activestate.com/recipes/546511-page-x-of-y-with-reportlab/
    http://code.activestate.com/recipes/576832/
    """

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor"""
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    # ----------------------------------------------------------------------
    def showPage(self):
        """
        On a page break, add information to the list
        """
        self.pages.append(dict(self.__dict__))
        self._startPage()

    # ----------------------------------------------------------------------
    def save(self):
        """
        Add the page number to each page (page x of y)
        """
        page_count = len(self.pages)

        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)

    # ----------------------------------------------------------------------
    def draw_page_number(self, page_count):
        """
        Add the page number
        """
        page = "Страница %s из %s" % (self._pageNumber, page_count)
        self.setFont('DejaVuSans', 9)
        self.drawRightString(195 * mm, 5 * mm, page)
        self.drawCentredString(100 * mm, 5 * mm, "www.irobs.ru")
        self.drawString(10 * mm, 5 * mm, "+7 (800) 777-02-01")

class Bookmark(Flowable):
	def __init__(self, title, key):
		self.title = title
		self.key = key
		Flowable.__init__(self)

	def wrap(self, availWidth, availHeight):
		return (1, 1)

	def draw(self):
		self.canv.showOutline()
		#self.canv.drawString(0,0,"seam")
		print(self.key)
		self.canv.bookmarkPage(self.key)
		self.canv.addOutlineEntry(self.title, self.key, 0, 0)


def addSeam(seam, styles):
    addSeamTable(seam, styles)
    storchSpeed = struct.unpack('%sf' % (len(seam.torchSpeed) // 4), seam.torchSpeed)
    scurrent = struct.unpack('%sf' % (len(seam.current) // 4), seam.current)
    svoltage = struct.unpack('%sf' % (len(seam.voltage) // 4), seam.voltage)
    swireSpeed = struct.unpack('%sf' % (len(seam.wireSpeed) // 4), seam.wireSpeed)
    addChart(storchSpeed, "Скорость горелки", "Скорость горелки [см/мин]")
    addChart(scurrent, "Cила тока", "Cила тока [А]")
    addChart(svoltage, "Напряжение источника", "Напряжение источника [В]")
    addChart(swireSpeed, "Скорость подачи проволоки", "Скорость подачи проволоки [м/мин]")


def addChart(values, name, yAxesName, period):
    drawing = Drawing(5, 200)
    len(values)

    dataVal = [(1,1),(2,2)]
    if len(values) > 2:
        dataVal = []
        for time,val in zip(np.linspace(0,(len(values)-1)*period,len(values)), values):
            dataVal.append((time,val))
    data = [
        dataVal
    ]
    lp = LinePlot()
    lp.x = 0
    lp.y = 50
    lp.height = 125
    lp.width = 450
    lp.data = data
    lp.joinedLines = 1
    lp.strokeColor = colors.black
    lp.xValueAxis.valueMin = 0
    lp.xValueAxis.labelTextFormat = '%2.1f'
    maxOfGraph = max(values)
    valmax = 0
    if maxOfGraph > 10:
        valmax = max(values) // 10 * 10 + 20
    else:
        valmax = round(max(values)) + 1
    lp.yValueAxis.valueMax = valmax
    lp.yValueAxis.valueMin = 0
    lp.yValueAxis.valueStep = valmax / 4
    drawing.add(lp)

    laby = Label()
    laby.setOrigin(-30, 125)
    laby.fontName = 'DejaVuSans'
    laby.angle = 90
    laby.dx = 0
    laby.dy = -20
    laby.setText(yAxesName)
    drawing.add(laby)

    labx = Label()
    labx.setOrigin(210, 45)
    labx.fontName = 'DejaVuSans'
    labx.angle = 0
    labx.dx = 0
    labx.dy = -20
    labx.setText("Время [с]")
    drawing.add(labx)

    labt = Label()
    labt.setOrigin(210, 205)
    labt.fontName = 'DejaVuSans'
    labt.angle = 0
    labt.dx = 0
    labt.dy = -20
    labt.setText(name)
    drawing.add(labt)
    return drawing


def addSeamTable(seam,styles, storchSpeed, scurrent, svoltage, swireSpeed):
    data = [("Тип соединения", seam.connId.ctype if seam.connId else "Не присвоено"),
            ("Чертёж", seam.detailId.detailName if seam.detailId else "Не присвоено"),
            ("Оборудование", seam.equipmentId.name if seam.equipmentId else "Не присвоено"),
            ("Партия", str(seam.batchNumber)),
            ("Номер в партии", str(seam.detailNumber)),
            ("Авторизованный пользователь", seam.authorizedUser.name if seam.authorizedUser else "Не присвоено"),
            ("Программа сварки", str(seam.weldingProgram)),
            ("Время начала", str(seam.startTime)),
            ("Время окончания", str(seam.endTime)),
            ("Стату окончания", "Успешно" if seam.endStatus == 0 else "Ошибка "+str(seam.endStatus)),
            ("Тип колебаний", str(seam.burnerOscillation.oscName)),
            ("Расч. расход газа", str(seam.connId.shieldingGasConsumption)+" л/мин" if seam.connId else "Нет данных"),
            ("Расч. расход проволки", str(seam.connId.wireConsumption)+" м/мин" if seam.connId else "Нет данных"),
            ("Установленная сила тока", str(round(scurrent[0]))+ " А"),
            ("Установленное напряжение дуги", str(round(svoltage[0]))+ " В"),
            ("Установленная скорость сварки", str(storchSpeed[int(len(storchSpeed)/2)])+ " см/мин"),
            ("Уст. скорость подачи проволоки", str(round(swireSpeed[0],2))+ " м/мин"),
            #("Период снятия", str(seam.period)+" c")
            ]
    table = Table(data, colWidths=200, rowHeights=15)
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.7, colors.black),
                               ("FONTNAME", (0, 0), (-1, -1), 'DejaVuSans')]))
    return table


def addDetTable(det,styles):
    data = [("Номер чертежа", det.blueprinNumber if det else "Не присвоено"),
            ("Название детали", det.detailName if det else "Не присвоено"),
            ("Марка материала", det.materialGrade if det else "Не присвоено"),
            ("Программа сварки", det.weldingProgram if det else "Не присвоено"),
            ("рассчётное время сварки", det.processingTime if det else "Не присвоено")
            ]
    table = Table(data, colWidths=200, rowHeights=15)
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.7, colors.black),
                               ("FONTNAME", (0, 0), (-1, -1), 'DejaVuSans')]))
    return table


def createMultiPage():
    pdfmetrics.registerFont(TTFont('DejaVuSans', "DejaVuSansCondensed.ttf"))
    doc = SimpleDocTemplate("отчёт репортлаб.pdf", pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=54, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='russ', fontName = 'DejaVuSans', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='russMain', fontName='DejaVuSans', alignment=TA_CENTER, fontSize = 16, spaceAfter = 10))

    Story = []

    Story.append(Paragraph("""Отчёт
                        C отсюда и до туда""", styles["russMain"]))
    det = Detail.select()[0]
    Story.append(addDetTable(det, styles))
    Story.append(Spacer(0,5))
    detImg = bi.unzip(det.img)
    stream = BytesIO(detImg[-1])
    im = Image(stream, 300)
    Story.append(im)

    Story.append(PageBreak())
    for seam in Seam.select():

        # Create return address
        storchSpeed = struct.unpack('%sf' % (len(seam.torchSpeed) // 4), seam.torchSpeed)
        scurrent = struct.unpack('%sf' % (len(seam.current) // 4), seam.current)
        svoltage = struct.unpack('%sf' % (len(seam.voltage) // 4), seam.voltage)
        swireSpeed = struct.unpack('%sf' % (len(seam.wireSpeed) // 4), seam.wireSpeed)
        Story.append(addSeamTable(seam, styles))
        Story.append(addChart(storchSpeed, "Скорость сварки", "Скорость сварки [см/мин]"))
        Story.append(addChart(scurrent, "Сила тока", "Сила тока [А]"))
        Story.append(addChart(svoltage, "Напряжение дуги", "Напряжение дуги [В]"))
        Story.append(addChart(swireSpeed, "Скорость подачи проволоки", "Скорость подачи проволоки [м/мин]"))
        Story.append(PageBreak())

    doc.build(Story, canvasmaker=PageNumCanvas)


def add_welding_info_table(seam,rdet):
    data = [("Данные авторизованного пользователя", seam.authorizedUser.name if seam.authorizedUser else "не присвоен"),
            ("Название детали", seam.detailId.detailName if seam.detailId else "не присвоен"),
            ("Вид сварного соединения", seam.connId.ctype if seam.connId else "не присвоен"),
            ("Толщина свариваемых деталей", seam.connId.thicknessOfElement if seam.connId else "нет данных"),
            ("Марка и сечение проволоки", seam.connId.fillerWireMark + seam.connId.fillerWireDiam if seam.connId else "нет данных"),
            ("№ чертежа детали", seam.detailId.blueprinNumber  if seam.detailId else "нет данных"),
            ("Марка материала", seam.detailId.materialGrade  if seam.detailId else "нет данных"),
            ("№ партии (серии)", rdet.batchNumber if rdet else "нет данных"),
            ("№ в партии (серии)", rdet.detailNumber if rdet else "нет данных"),
            ("№ программы сварки", seam.weldingProgram)
            ]
    table = Table(data, colWidths=200, rowHeights=15)
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.7, colors.black),
                               ("FONTNAME", (0, 0), (-1, -1), 'DejaVuSans')]))
    return table

def add_meser_value_table(seam):
    storchSpeed = struct.unpack('%sf' % (len(seam.torchSpeed) // 4), seam.torchSpeed)
    scurrent = struct.unpack('%sf' % (len(seam.current) // 4), seam.current)
    svoltage = struct.unpack('%sf' % (len(seam.voltage) // 4), seam.voltage)
    swireSpeed = struct.unpack('%sf' % (len(seam.wireSpeed) // 4), seam.wireSpeed)
    data = [("Дата и время сварки изделия", str(seam.startTime)[:19]),
            ("Скорость сварки см\мин", round(max(storchSpeed))),
            ("Сила тока А", round(scurrent[-1])),
            ("Напряжение дуги B", round(svoltage[-1])),
            ("Тип колебаний", seam.burnerOscillation.oscName),
            ("Расход защитного газа л\мин", "Датчик не подключен"),
            ("Скорость подачи проволоки м\мин", round(swireSpeed[-1])),
            ("Расход сварочной проволоки гр\м", seam.connId.wireMassConsumption if seam.connId else "не присвоено"),
            ("Начало сварки", str(seam.startTime)[:19]),
            ("Окончание сварки", str(seam.endTime)[:19])
            ]
    table = Table(data, colWidths=200, rowHeights=15)
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.7, colors.black),
                               ("FONTNAME", (0, 0), (-1, -1), 'DejaVuSans')]))
    return table


class HorizontalRule(Flowable):

    def __init__(self, width=2, strokecolor=colors.black):
        self.width = width
        self.strokecolor = strokecolor

    def wrap(self, availWidth, availHeight):
        self.availWidth = availWidth
        return (availWidth, self.width + 2)

    def draw(self):
        canvas = self.canv
        canvas.setLineWidth(self.width)
        canvas.setStrokeColor(self.strokecolor)
        p = canvas.beginPath()
        p.moveTo(0, 1)
        p.lineTo(self.availWidth, 1)
        p.close()
        canvas.drawPath(p)


def create_periodPdf(pdf_path, start, end):
    pdfmetrics.registerFont(TTFont('DejaVuSans', "DejaVuSansCondensed.ttf"))
    if pdf_path: pdf_path+="/"
    doc = SimpleDocTemplate(pdf_path+"Отчёт с " +str(start).replace(':','_')+ " по "+str(end).replace(':','_')+".pdf", pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=54, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='russ', fontName='DejaVuSans', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='russMain', fontName='DejaVuSans', alignment=TA_CENTER, fontSize=16, spaceAfter=10))

    Story = []
    Story.append(Paragraph("ИРС-СМАЗ Робототехнический комплекс", styles["russMain"]))
    Story.append(Paragraph("Паспорт РТК", styles["russMain"]))
    Story.append(Paragraph("с " + str(start) + " по " + str(end), styles["russMain"]))
    Story.append(HorizontalRule())
    seams = Seam.select().where(Seam.startTime.between(start, end))

    for seam in seams:
        Story.append(Paragraph("Информация о сварке", styles["russ"]))
        Story.append(Spacer(0, 5))
        Story.append(add_welding_info_table(seam, seam.realDetId))
        Story.append(Spacer(0, 5))
        Story.append(Paragraph("Измеренные значения", styles["russ"]))
        Story.append(Spacer(0, 5))
        Story.append(add_meser_value_table(seam))
        Story.append(Spacer(0, 5))
        Story.append(Paragraph("Графики измерений", styles["russ"]))
        Story.append(Spacer(0, 5))
        storchSpeed = struct.unpack('%sf' % (len(seam.torchSpeed) // 4), seam.torchSpeed)
        scurrent = struct.unpack('%sf' % (len(seam.current) // 4), seam.current)
        svoltage = struct.unpack('%sf' % (len(seam.voltage) // 4), seam.voltage)
        swireSpeed = struct.unpack('%sf' % (len(seam.wireSpeed) // 4), seam.wireSpeed)
        Story.append(addChart(storchSpeed, "Скорость сварки", "Скорость сварки [см/мин]", seam.period))
        Story.append(addChart(scurrent, "Сила тока", "Сила тока [А]", seam.period))
        Story.append(addChart(svoltage, "Напряжение дуги", "Напряжение дуги [В]", seam.period))
        Story.append(
            addChart(swireSpeed, "Скорость подачи проволоки", "Скорость подачи проволоки [м/мин]", seam.period))
        Story.append(PageBreak())
    doc.build(Story, canvasmaker=PageNumCanvas)


def create_pdf(pdf_path, id):
    #Получение данных из БД
    real_detail = RealDetail.get(RealDetail.id == id)
    detail = Detail.get(Detail.id == real_detail.detailId)
    seams = Seam.select().where(Seam.realDetId == id).order_by(
        Seam.connId)

    pdfmetrics.registerFont(TTFont('DejaVuSans', "DejaVuSansCondensed.ttf"))

    if pdf_path: pdf_path += "/"
    doc = SimpleDocTemplate(pdf_path+"Отчёт по детали " + detail.detailName + " партии " + real_detail.batchNumber
                            + ".pdf", pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=54, bottomMargin=18)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='russ', fontName='DejaVuSans', alignment=TA_CENTER, fontSize=12))#TA_JUSTIFY))
    styles.add(ParagraphStyle(name='russMain', fontName='DejaVuSans', alignment=TA_CENTER, fontSize=16, spaceAfter=10))

    Story = []
    if len(seams) > 0:
        if seams[-1].equipmentId is not None:
            Story.append(Paragraph("ИРС-СМАЗ Робототехнический комплекс " + seams[-1].equipmentId.name, styles["russMain"]))
        else:
            Story.append(Paragraph("ИРС-СМАЗ Робототехнический комплекс ", styles["russMain"]))
    else:
        Story.append(Paragraph("ИРС-СМАЗ Робототехнический комплекс ", styles["russMain"]))
    Story.append(Paragraph("Паспорт РТК", styles["russMain"]))
    Story.append(HorizontalRule())
    Story.append(Spacer(0, 5))
    Story.append(Paragraph("Информация о сварке", styles["russ"]))
    Story.append(Spacer(0, 5))
    if len(seams)>0 and real_detail is not None:
        Story.append(add_welding_info_table(seams[-1], real_detail))
    else:
        Story.append(Paragraph("Нет данных о швах", styles["russ"]))
    Story.append(Spacer(0, 5))
    Story.append(Paragraph("Изображение детали", styles["russ"]))
    Story.append(Spacer(0, 5))
    if detail is not None:
        if detail.img is not None:
            detImg = bi.unzip(detail.img)
    if len(detImg) > 0:
        stream = BytesIO(detImg[-1])
        img = plimg.open(stream)
        im = Image(stream, 300, int(300 * img.size[1] / img.size[0]))
        Story.append(im)
    Story.append(Spacer(0, 5))
    Story.append(PageBreak())
    for seam in seams:
        Story.append(Paragraph("Измеренные значения", styles["russ"]))
        Story.append(Spacer(0, 5))
        Story.append(add_meser_value_table(seam))
        Story.append(Spacer(0, 5))
        Story.append(Paragraph("Графики измерений", styles["russ"]))
        Story.append(Spacer(0, 5))
        storchSpeed = struct.unpack('%sf' % (len(seam.torchSpeed) // 4), seam.torchSpeed)
        scurrent = struct.unpack('%sf' % (len(seam.current) // 4), seam.current)
        svoltage = struct.unpack('%sf' % (len(seam.voltage) // 4), seam.voltage)
        swireSpeed = struct.unpack('%sf' % (len(seam.wireSpeed) // 4), seam.wireSpeed)
        """bkmrk = Bookmark("seam", str(seam))
        Story.append(bkmrk)"""
        Story.append(addChart(storchSpeed, "Скорость сварки", "Скорость сварки [см/мин]", seam.period))
        Story.append(addChart(scurrent, "Сила тока", "Сила тока [А]", seam.period))
        Story.append(addChart(svoltage, "Напряжение дуги", "Напряжение дуги [В]", seam.period))
        Story.append(
            addChart(swireSpeed, "Скорость подачи проволоки", "Скорость подачи проволоки [м/мин]", seam.period))
        Story.append(PageBreak())
    doc.build(Story, canvasmaker=PageNumCanvas)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    #createMultiPage()
    start = datetime.date(1940, 1, 1)
    end = datetime.date(2023, 1, 1)
    create_periodPdf("otch", start, end)
    #create_pdf('D:/irsDB/venv/irsDB/otch', 3)