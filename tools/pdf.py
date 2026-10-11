from PyPDF2 import PdfMerger

pdfs = []
def pdf_setup(pdf_names, book, lang):
    pdf_user_name = []
    for pdf in pdf_names:
        pdf_file = f"data/book_units/{lang}_{book}_{pdf}.pdf"
        pdf_user_name.append(pdf)
        pdfs.append(pdf_file)
    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(pdf)
    user_file_name = '_'.join(map(str, pdf_user_name))
    user_file_path = f'data/user_pdf/{lang}_{user_file_name}.pdf'
    merger.write(user_file_path)
    pdfs.clear()
    pdf_user_name.clear()
    merger.close()
    return user_file_path

def pdf_namer(pdf_names, lang):
    pdf_user_name = []
    for pdf in pdf_names:
        pdf_user_name.append(pdf)
    user_file_name = '_'.join(map(str, pdf_user_name))
    user_file_path = f'data/user_pdf/{lang}_{user_file_name}.pdf'
    pdf_user_name.clear()
    return user_file_path

