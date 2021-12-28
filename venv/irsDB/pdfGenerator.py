from fpdf import FPDF
from models import *
import datetime
import byteimgs as bi
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

class CustomPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-10)

        #self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        self.set_font('DejaVu', '', 8)

        # Добавляем номер страницы

        page = 'Страница ' + str(self.page_no()) + ' из {nb}'
        self.cell(0, 10, "www.irobs.ru  +7 (800) 777-02-01", 0, 0, 'L')
        self.cell(0, 10, page, 0, 0, 'R')


def addSeam(pdf, seam):
    pdf.cell(200, 5, txt="Тип соединения: " + (str(seam.connId) if seam.connId is not None else "не присвоено"), ln=1, align="L")
    pdf.cell(200, 5, txt="Программа сварки: " + seam.weldingProgram, ln=1, align="L")
    pdf.cell(200, 5, txt="Время начала сварки: " + str(seam.startTime)[:19], ln=1, align="L")
    pdf.cell(200, 5, txt="Время окнчания сварки: " + str(seam.endTime)[:19], ln=1, align="L")
    pdf.cell(200, 5, txt="Период снятия данных: " + str(seam.period) + " c", ln=1, align="L")
    pdf.cell(200, 5, txt="Колебания: " + (str(seam.burnerOscillation) if seam.burnerOscillation is not None else "не присвоено"), ln=1, align="L")

    plt.title("Линейная скорость движения горелки по стыку")
    plt.xlabel("Время (с)")
    plt.ylabel("Скорость (см/с)")
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
    plt.savefig('plot.png')
    pdf.image('plot.png', x=None, y=None, w=200, h=100, type='', link='')

    plt.title("Ток")
    plt.xlabel("Время (с)")
    plt.ylabel("Ток (А)")
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
    plt.savefig('plot1.png')
    pdf.image('plot1.png', x=None, y=None, w=200, h=100, type='', link='')

    plt.title("Напряжение")
    plt.xlabel("Время (с)")
    plt.ylabel("Напряжение (В)")
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
    plt.savefig('plot2.png')
    pdf.image('plot2.png', x=None, y=None, w=200, h=100, type='', link='')

    plt.title("Значение коррекции напряжения")
    plt.xlabel("Время (с)")
    plt.ylabel("Напряжение (В)")
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
    plt.savefig('plot3.png')
    pdf.image('plot3.png', x=None, y=None, w=200, h=100, type='', link='')

    plt.title("Скорость подачи проволоки")
    plt.xlabel("Время (с)")
    plt.ylabel("Расход (см/мин)")
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
    plt.savefig('plot4.png')
    pdf.image('plot4.png', x=None, y=None, w=200, h=100, type='', link='')

    plt.title("Расход защитного газа")
    plt.xlabel("Время (с)")
    plt.ylabel("Расход (л/мин)")
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
    plt.savefig('plot5.png')
    pdf.image('plot5.png', x=None, y=None, w=200, h=100, type='', link='')

    pdf.cell(200, 10, txt="Завершён: " + ("успешно" if seam.endStatus else "с ошибкой"), ln=1, align="L")



def create_pdf(pdf_path, batchNumber, detailNumber):
    pdf = CustomPDF()
    # Создаем особое значение {nb}
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(200, 10, txt="Отчёт по детали", ln=1, align="C")
    pdf.set_font('DejaVu', '', 12)
    seams = Seam.select().where(Seam.batchNumber == batchNumber and Seam.detailNumber == detailNumber).order_by(Seam.connId)#detid
    pdf.cell(200, 5, txt="Номер партии: " + str(batchNumber), ln=1, align="L")
    pdf.cell(200, 10, txt="Номер детали: " + str(detailNumber), ln=1, align="L")
    detail = Detail.get(Detail.id == seams[0].detailId)
    pdf.cell(200, 5, txt="Номер чертежа: " + str(detail.blueprinNumber), ln=1, align="L")
    pdf.cell(200, 5, txt="Название детали: " + detail.detailName, ln=1, align="L")
    pdf.cell(200, 5, txt="Материал: " + detail.materialGrade, ln=1, align="L")
    pdf.cell(200, 5, txt="Программа сварки: " + detail.weldingProgram, ln=1, align="L")
    pdf.cell(200, 5, txt="Время обработки: " + str(detail.processingTime), ln=1, align="L")
    detImgs = bi.unzip(detail.img)
    stream = BytesIO(detImgs[1])
    pdf.image(stream, x=20, y=100, w=70)
    pdf.add_page()
    curConnType = 0
    for seam in seams:
        if curConnType != seam.connId:
            pdf.add_page()
            pdf.start_section(str(seam.connId), level=0)
            if seam.connId is not None:
                connInfo = Connection.get(Connection.id == seam.connId)
                pdf.cell(200, 5, txt="Тип соединения: " + connInfo.ctype, ln=1, align="L")
                pdf.cell(200, 5, txt="Толщина элементов: " + connInfo.thicknessOfElement, ln=1, align="L")
                pdf.cell(200, 5, txt="Разделка кромок: " + connInfo.jointBevelling, ln=1, align="L")
                pdf.cell(200, 5, txt="Размеры сварного шва: " + connInfo.seamDimensions, ln=1, align="L")
                pdf.cell(200, 5, txt="Марка присадочной проволоки: " + connInfo.fillerWireMark, ln=1, align="L")
                pdf.cell(200, 5, txt="Сечение присадочной проволоки: " + connInfo.fillerWireDiam , ln=1, align="L")
                pdf.cell(200, 5, txt="Рассчётный расход сварочной проволоки [см/мин]: " + str(connInfo.wireConsumption), ln=1, align="L")
                pdf.cell(200, 5, txt="Тип защитного газа: " + connInfo.shieldingGasType, ln=1, align="L")
                pdf.cell(200, 5, txt="Рассчётный расход защитного газа на соединение [л/мин]: " + str(connInfo.shieldingGasConsumption), ln=1, align="L")
                pdf.cell(200, 5, txt="Наименование программы сварки соединения: " + connInfo.programmName, ln=1, align="L")
                pdf.cell(200, 5, txt="Рассчётное время сварки соединения: " + str(connInfo.weldingTime), ln=1, align="L")
                pdf.cell(200, 5, txt="Предпочтительное частота сбора данных [с]: " + str(connInfo.preferredPeriod), ln=1, align="L")
            """ctype = CharField()
            thicknessOfElement = CharField()
            jointBevelling = CharField()
            jointBevellingImg = BlobField(default=b'\x00\x00\x00\x00')
            seamDimensions = CharField()
            fillerWireMark = CharField()
            fillerWireDiam = CharField()
            wireConsumption  = DoubleField()
            shieldingGasType = CharField()
            shieldingGasConsumption = DoubleField()
            programmName = CharField()
            weldingTime = DateTimeField()
            preferredPeriod = DoubleField(default=0.1)"""
            curConnType = seam.connId
        pdf.start_section(str(seam.connId), level=1)
        addSeam(pdf, seam)
    pdf.output(pdf_path)
    """connId = ForeignKeyField(Connection)
    detailId = ForeignKeyField(Detail)
    batchNumber = IntegerField()
    detailNumber = IntegerField()
    authorizedUser = CharField()
    weldingProgram = CharField()
    startTime = DateTimeField()
    endTime = DateTimeField()
    endStatus = BooleanField(default=False)"""

def create_periodPdf(pdf_path, start, end):
    pdf = CustomPDF()
    # Создаем особое значение {nb}
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(200, 5, txt="Отчёт за период", ln=1, align="C")
    pdf.cell(200, 5, txt="с " + str(start) + " по " + str(end), ln=1, align="C")
    pdf.set_font('DejaVu', '', 12)
    seams = Seam.select().where(Seam.startTime.between(start, end))
    for seam in seams:
        pdf.start_section(str(seam.batchNumber)+str(seam.detailNumber)+str(seam.connId), level = 0)
        pdf.cell(200, 5, txt="Партия №: " + str(seam.batchNumber), ln=1, align="L")
        pdf.cell(200, 5, txt="№ детали в партии: " + str(seam.detailNumber), ln=1, align="L")
        pdf.cell(200, 5, txt="Тип детали: " + (str(seam.detailId) if seam.detailId is not None else "не присвоено"), ln=1, align="L")
        pdf.cell(200, 5, txt="Произведено на: " + (str(seam.equipmentId) if seam.equipmentId is not None else "не присвоено"), ln=1, align="L")
        pdf.cell(200, 5, txt="Авторизованный пользователь: " + (str(seam.authorizedUser) if seam.authorizedUser is not None else "не присвоено"), ln=1, align="L")
        addSeam(pdf, seam)
        pdf.add_page()
    pdf.output(pdf_path + '/Отчёт за период ' + str(start).replace(':','_') +' '+ str(end).replace(':','_') + '.pdf')



if __name__ == '__main__':
    start = datetime.date(1940, 1, 1)
    end = datetime.date(2023, 1, 1)
    #create_periodPdf('', start, end)
    create_pdf('отчёт по детали.pdf', 1, 2)
    """d1940 = datetime.date(1940, 1, 1)
    d1960 = datetime.date(2023, 1, 1)
    print("try")
    seams = Seam.select().where(Seam.batchNumber == 1 and Seam.detailNumber == 1)
    for seam in seams:
        print(seam)
    seams = Seam.select().where(Seam.startTime.between(d1940,d1960))
    for seam in seams:
        print(seam)"""
