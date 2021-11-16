from fpdf import FPDF

class CustomPDF(FPDF):

    def header(self):
        pass

    def footer(self):
        self.set_y(-10)

        self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        self.set_font('DejaVu', '', 8)

        # Добавляем номер страницы

        page = 'Страница ' + str(self.page_no()) + ' из {nb}'
        self.cell(0, 10, "Разработано www.irobs.ru  +7 (800) 777-02-01", 0, 0, 'L')
        self.cell(0, 10, page, 0, 0, 'R')



def create_pdf(pdf_path):
    pdf = CustomPDF()
    # Создаем особое значение {nb}
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(200, 10, txt="Отчёт по сварке", ln=1, align="C")
    pdf.output(pdf_path)


if __name__ == '__main__':
    create_pdf('отчёт.pdf')
