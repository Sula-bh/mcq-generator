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
        

def get_table_data(quiz_dict):
    try:
        logging.info("Converting quiz dictionary to table format")
        quiz_table_data=[]
        
        for key,value in quiz_dict.items():
            mcq=value["mcq"]
            options=" || ".join(
                [
                    f"{option}-> {option_value}" for option, option_value in value["options"].items()
                 
                 ]
            )
            
            correct=value["correct"]
            quiz_table_data.append({"MCQ": mcq,"Choices": options, "Correct": correct})
        
        logging.info("Successfully created table data")
        return quiz_table_data
        
    except Exception as e:
        logging.error("Error while converting quiz to table data", exc_info=True)
        return None

