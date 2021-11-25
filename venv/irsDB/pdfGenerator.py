from fpdf import FPDF
from models import *
import datetime
import byteimgs as bi
from io import BytesIO

class TOC(FPDF):
    def AddPage(this, orientation=''):
        FPDF.AddPage(this, orientation)
        if (this._numbering):
            this._numPageNum += 1

    def TOC_Entry(this, txt, level=0):
        this._toc += [{'t': txt, 'l': level, 'p': this.numPageNo()}]

    def insertTOC(this, location=1, labelSize=20, entrySize=10, tocfont='Times', label='Table of Contents'):
        # make toc at end
        this.stopPageNums()
        this.AddPage()
        tocstart = this.page

        this.SetFont(tocfont, 'B', labelSize)
        this.Cell(0, 5, label, 0, 1, 'C')
        this.Ln(10)

        for t in this._toc:
            # Offset
            level = t['l']
            if (level > 0):
                this.Cell(level * 8)
            weight = ''
            if (level == 0):
                weight = 'B'
            Str = t['t']
            this.SetFont(tocfont, weight, entrySize)
            strsize = this.GetStringWidth(Str)
            this.Cell(strsize + 2, this.FontSize + 2, Str)

            # Filling dots
            this.SetFont(tocfont, '', entrySize)
            PageCellSize = this.GetStringWidth(str(t['p'])) + 2
            w = this.w - this.lMargin - this.rMargin - PageCellSize - (level * 8) - (strsize + 2)
            nb = w / this.GetStringWidth('.')
            dots = str_repeat('.', nb)
            this.Cell(w, this.FontSize + 2, dots, 0, 0, 'R')

            # Page number
            this.Cell(PageCellSize, this.FontSize + 2, str(t['p']), 0, 1, 'R')

        # grab it and move to selected location
        n = this.page
        n_toc = n - tocstart + 1
        last = []

        # store toc pages
        for i in xrange(tocstart, n + 1):
            last += [this.pages[i]]

        # move pages
        for i in xrange(tocstart - 1, location - 1, -1):
            # ~ for(i=tocstart - 1;i>=location-1;i--)
            this.pages[i + n_toc] = this.pages[i]

        # Put toc pages at insert point
        for i in xrange(0, n_toc):
            this.pages[location + i] = last[i]
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



def create_pdf(pdf_path):
    pdf = CustomPDF()
    # Создаем особое значение {nb}
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(200, 10, txt="Отчёт по сварке", ln=1, align="C")
    pdf.set_font('DejaVu', '', 12)
    batchNumber = 1
    detailNumber = 1
    seams = Seam.select().where(Seam.batchNumber == 1 and Seam.detailNumber == 1)
    pdf.cell(200, 5, txt="Номер партии: " + str(batchNumber), ln=1, align="L")
    pdf.cell(200, 10, txt="Номер детали: " + str(detailNumber), ln=1, align="L")
    detail = Detail.get(Detail.id == seams[0].detailId)
    print(detail)
    pdf.cell(200, 5, txt="Номер чертежа: " + str(detail.blueprinNumber), ln=1, align="L")
    pdf.cell(200, 5, txt="Название детали: " + detail.detailName, ln=1, align="L")
    pdf.cell(200, 5, txt="Материал: " + detail.materialGrade, ln=1, align="L")
    pdf.cell(200, 5, txt="Программа сварки: " + detail.weldingProgram, ln=1, align="L")
    pdf.cell(200, 5, txt="Время обработки: " + str(detail.processingTime), ln=1, align="L")
    detImgs = bi.unzip(detail.img)
    stream = BytesIO(detImgs[1])
    pdf.image(stream, x=20, y=120, w=70)
    pdf.add_page()
    for seam in seams:
        pdf.cell(200, 5, txt="Тип соединения: " + str(seam.connId), ln=1, align="L")
        pdf.cell(200, 5, txt="Тип детали: " + str(seam.detailId), ln=1, align="L")
        pdf.cell(200, 5, txt="Авторизованный пользователь: " + seam.authorizedUser, ln=1, align="L")
        pdf.cell(200, 5, txt="Программа сварки: " + seam.weldingProgram, ln=1, align="L")
        pdf.cell(200, 5, txt="Время начала сварки: " + str(seam.startTime), ln=1, align="L")
        pdf.cell(200, 5, txt="Время окнчания сварки: " + str(seam.endTime), ln=1, align="L")
        pdf.cell(200, 10, txt="Завершён: " + ("успешно" if seam.endStatus else "с ошибкой"), ln=1, align="L")
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


if __name__ == '__main__':
    create_pdf('отчёт.pdf')
    """d1940 = datetime.date(1940, 1, 1)
    d1960 = datetime.date(2022, 1, 1)
    print("try")
    seams = Seam.select().where(Seam.batchNumber == 1 and Seam.detailNumber == 1)
    for seam in seams:
        print(seam)
    seams = Seam.select().where(Seam.startTime.between(d1940,d1960))
    for seam in seams:
        print(seam)"""
