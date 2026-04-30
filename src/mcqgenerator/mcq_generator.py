import os
from dotenv import load_dotenv
import streamlit as st
from mcqgenerator.logger import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.globals import set_verbose

load_dotenv()
KEY=st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not KEY:
    logging.error("GOOGLE_API_KEY not found")
else:
    logging.info("GOOGLE_API_KEY loaded successfully")

logging.info("Initializing Gemini model")
llm = ChatGoogleGenerativeAI(google_api_key=KEY, model="gemini-3.1-flash-lite-preview", temperature=0.3, max_output_tokens=2048)

GENERATE_TEMPLATE_WITH_TEXT = """
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions with difficulty level: {tone}. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Do NOT use markdown (no ```).
Do NOT use escape characters (like \\')
### RESPONSE_JSON
{response_json}

"""

quiz_generation_prompt_with_text=PromptTemplate(
    input_variables=["text", "number", "tone", "response_json"],
    template=GENERATE_TEMPLATE_WITH_TEXT
)

quiz_chain_with_text = quiz_generation_prompt_with_text | llm

GENERATE_TEMPLATE_WITH_SUBJECT = """
You are an expert MCQ maker. Your job is to \
create a quiz of {number} multiple choice questions for {subject} students with difficulty level: {tone}. 
Cover different subtopics of {subject}.
Include a mix of conceptual and factual questions.
Ensure questions are clear and unambiguous.
Make sure the questions are not repeated and make sure the questions are relevant to the subject.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Do NOT use markdown (no ```).
Do NOT use escape characters (like \\')
### RESPONSE_JSON
{response_json}

"""

quiz_generation_prompt_with_subject=PromptTemplate(
    input_variables=["number", "subject", "tone", "response_json"],
    template=GENERATE_TEMPLATE_WITH_SUBJECT
)

quiz_chain_with_subject = quiz_generation_prompt_with_subject | llm

EVALUATE_TEMPLATE="""
You are an expert teacher reviewing MCQs for accuracy and clarity.

Here is a quiz:
{quiz}

Your task:
- Review each question
- Fix any incorrect questions or answers
- Improve clarity
- Ensure correctness

Return ONLY the corrected MCQs in the same format.
Return ONLY valid JSON.
Do NOT add explanation.
"""

quiz_evaluation_prompt=PromptTemplate(input_variables=["quiz"], template=EVALUATE_TEMPLATE)

generate_evaluate_chain_with_text=(
    quiz_chain_with_text
    | (lambda x: {"quiz": x.content})
    | quiz_evaluation_prompt
    | llm
    | {
        "raw": RunnablePassthrough(),   
        "parsed": JsonOutputParser()
    }
)

generate_evaluate_chain_with_subject=(
    quiz_chain_with_subject
    | (lambda x: {"quiz": x.content})
    | quiz_evaluation_prompt
    | llm
    | {
        "raw": RunnablePassthrough(),   
        "parsed": JsonOutputParser()
    }
)

logging.info("MCQ generation and evaluation chain created successfully")

set_verbose(True)