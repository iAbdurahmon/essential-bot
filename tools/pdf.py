import os

from pypdf import PdfWriter

USER_PDF_DIR = 'data/user_pdf'
BOOK_UNITS_DIR = 'data/book_units'


def pdf_namer(pdf_names, lang, user_id):
    # the user id keeps two people picking the same units from sharing one file
    units = '_'.join(map(str, pdf_names))
    return os.path.join(USER_PDF_DIR, f"{lang}_{units}_{user_id}.pdf")


def pdf_setup(pdf_names, book, lang, user_id):
    os.makedirs(USER_PDF_DIR, exist_ok=True)
    merger = PdfWriter()
    for unit in pdf_names:
        merger.append(os.path.join(BOOK_UNITS_DIR, f"{lang}_{book}_{unit}.pdf"))
    user_file_path = pdf_namer(pdf_names, lang, user_id)
    merger.write(user_file_path)
    merger.close()
    return user_file_path
