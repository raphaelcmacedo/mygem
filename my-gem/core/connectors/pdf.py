import PyPDF2
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfparser import PDFParser, PDFDocument

def convert_pdf_to_txt(file):
    if type(file) == dict:
        infile = open(file["path"], 'rb')
        parser = PDFParser(infile)
    else:
        parser = PDFParser(file)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    lines = []

    for page in doc.get_pages():
        interpreter.process_page(page)
        layout = device.get_result()
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                blocks = lt_obj.get_text().split('\n')
                for block in blocks:
                    lines.append(block)

    return lines

def pdf_to_txt_pypdf(f):
    read_pdf = PyPDF2.PdfFileReader(f)
    page = read_pdf.getPage(0)
    page_content = page.extractText()
    return page_content.split('\n')
