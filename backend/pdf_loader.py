import PyPDF2
import docx2txt
import os
import tempfile

def load_pdf_text(uploaded_file):
    """
    Load text from a Streamlit UploadedFile or file-like object.
    Supports PDF, DOCX, and TXT.
    """
    # Determine filename and extension
    name = getattr(uploaded_file, 'name', '')
    ext = name.lower().split('.')[-1]

    if ext == 'pdf':
        # PDFReader accepts a file-like, so pass the UploadedFile directly
        reader = PyPDF2.PdfReader(uploaded_file)
        return ''.join([page.extract_text() or '' for page in reader.pages])

    elif ext == 'docx':
        # docx2txt requires a filesystem path, so save to temp
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        tmp.write(uploaded_file.read())
        tmp.close()
        text = docx2txt.process(tmp.name)
        os.unlink(tmp.name)
        return text

    elif ext == 'txt':
        return uploaded_file.read().decode('utf-8')

    else:
        return ""