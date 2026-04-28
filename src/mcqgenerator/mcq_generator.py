import os
import json
import pandas as pd
from dotenv import load_dotenv
from mcqgenerator.logger import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.globals import set_verbose

load_dotenv()
KEY=os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(google_api_key=KEY, model="gemini-2.5-flash", temperature=0.3, max_output_tokens=2048)

TEMPLATE = """
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz  of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}

"""

quiz_generation_prompt=PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=TEMPLATE
)

quiz_chain = quiz_generation_prompt | llm

TEMPLATE2="""
You are an expert {subject} teacher.

Here is a quiz:
{quiz}

Your task:
- Review each question
- Fix any incorrect questions or answers
- Improve clarity
- Ensure correctness

Return ONLY the corrected MCQs in the same format.
"""

quiz_evaluation_prompt=PromptTemplate(input_variables=["subject", "quiz"], template=TEMPLATE2)

generate_evaluate_chain=(
    {
        "quiz": quiz_chain,                     
        "subject": RunnablePassthrough()  
    }
    | quiz_evaluation_prompt
    | llm
    | {
        "raw": RunnablePassthrough(),   
        "parsed": JsonOutputParser()
    }
)

set_verbose(True)