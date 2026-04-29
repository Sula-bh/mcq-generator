import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

import json
import streamlit as st

from mcqgenerator.utils import read_file
from mcqgenerator.mcq_generator import generate_evaluate_chain_with_text, generate_evaluate_chain_with_subject
from mcqgenerator.logger import logging

logging.info("MCQ Generator App started")

try:
    with open(r'.\response.json', 'r') as file:
        RESPONSE_JSON = json.load(file)
    logging.info("Loaded response.json successfully")
except Exception as e:
    logging.error("Failed to load response.json", exc_info=True)
    st.error("Error loading response template")
    st.stop()

st.title("MCQs Generator Application")

if "mode" not in st.session_state:
    st.session_state.mode = "Generate with file"

selection = st.segmented_control(
    "Initial selection",
    label_visibility="hidden",
    options=["Generate with file", "Generate with subject"],
    selection_mode="single",
    default="Generate with file",
    required=True,
    width="stretch"
)

if selection != st.session_state.mode:
    st.session_state.mode=selection
    st.session_state.quiz=None
    st.session_state.clicked=False

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

if 'quiz' not in st.session_state:
    st.session_state.quiz= None

@st.cache_data(show_spinner=False)
def run_chain(inputs, mode):
    if mode=="text":
        return generate_evaluate_chain_with_text.invoke(inputs)
    else:
        return generate_evaluate_chain_with_subject.invoke(inputs)
    
def handle_response(response):
    logging.info("Chain executed successfully")
    usage = response["raw"].usage_metadata
    logging.info(f"Token usage: {usage}")

    print("Prompt Tokens:", usage.get("input_tokens"))
    print("Completion Tokens:", usage.get("output_tokens"))
    print("Total Tokens:", usage.get("total_tokens"))
    
    if isinstance(response, dict):
        quiz=response.get("parsed", None)
        st.session_state.quiz = quiz
        if quiz is None:
            logging.error("Parsed response is None")
            st.error("Error in the data")
    else:
        logging.warning("Response is not a dict")
        st.write(response)

with st.form("user_inputs"):
    if st.session_state.mode=="Generate with file":
        uploaded_file=st.file_uploader("Uplaod a PDF or txt file")

    if st.session_state.mode=="Generate with subject":
        subject=st.text_input("Enter Subject",max_chars=50)

    mcq_count=st.number_input("No. of MCQs", min_value=3, max_value=50)

    tone=st.selectbox("Complexity Level Of Questions", ("Easy", "Medium", "Hard"))

    button=st.form_submit_button("Generate MCQs")

    if button:
        if st.session_state.mode=="Generate with file":
            if uploaded_file is not None:
                with st.spinner("Generating MCQs..."):
                    try:
                        logging.info(f"File uploaded: {uploaded_file.name}")
                        logging.info(f"MCQ count: {mcq_count}, Tone: {tone}")

                        text=read_file(uploaded_file)
                        logging.info("File read successfully")

                        logging.info("Invoking generate_evaluate_chain_with_text")
                        response = run_chain({
                            "text": text,
                            "number": mcq_count,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }, "text")

                    except Exception as e:
                        logging.error("Error during MCQ generation", exc_info=True)
                        st.error("Error occurred while generating MCQs")

                    else:
                        handle_response(response)
                        
            else:
                st.error("Please, provide all the inputs!")
        else:
            if subject:
                with st.spinner("Generating MCQs..."):
                    try:
                        logging.info(f"MCQ count: {mcq_count}, Subject: {subject}, Tone: {tone}")

                        logging.info("Invoking generate_evaluate_chain_with_subject")
                        response = run_chain({
                            "number": mcq_count,
                            "subject": subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }, "subject")

                    except Exception as e:
                        logging.error("Error during MCQ generation", exc_info=True)
                        st.error("Error occurred while generating MCQs")

                    else:
                        handle_response(response)
            else:
                st.error("Please, provide all the inputs!")


def click_button():
    st.session_state.clicked = True

if st.session_state.quiz is not None:
    st.divider()
    st.subheader("Generated Questions")

    quiz=st.session_state.quiz

    with st.form("mcqs"):
        score=0
        for key, value in quiz.items():
            options=list(value["options"].values())
            ans = st.radio(f"{key}. {value.get('mcq')}",options,index=None)
            correct_ans = value["options"][value["correct"]]

            if st.session_state.clicked:
                if ans==correct_ans:
                    st.success("Correct Answer!")
                    score+=1
                else:
                    st.error("Wrong Answer!")

        submit=st.form_submit_button("Submit Answer",on_click=click_button)
        if st.session_state.clicked:
            st.markdown(
                f"""
                <div style="
                    display: inline-block;
                    padding: 12px 25px;
                    font-size: 28px;
                    font-weight: 600;
                    border-radius: 15px;
                    background: grey;
                    color: white;
                    margin-bottom: 10px;
                ">
                    Score: {score}
                </div>
                """,
                unsafe_allow_html=True
            )

    logging.info("Displayed MCQs successfully")