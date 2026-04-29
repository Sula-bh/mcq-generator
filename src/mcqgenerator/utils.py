import PyPDF2
from mcqgenerator.logger import logging


def read_file(file):
    try:
        logging.info(f"Reading file: {file.name}")

        if file.name.endswith(".pdf"):
            pdf_reader=PyPDF2.PdfReader(file)
            text=""
            for page in pdf_reader.pages:
                text+=page.extract_text()
            logging.info("PDF file read successfully")
            return text
            
        elif file.name.endswith(".txt"):
            content = file.read().decode("utf-8")
            logging.info("TXT file read successfully")
            return content
        
        else:
            logging.error("Unsupported file format")
            raise Exception(
                "unsupported file format only pdf and text file suppoted"
                )
        
    except Exception as e:
            logging.error("Error reading file", exc_info=True)
        

