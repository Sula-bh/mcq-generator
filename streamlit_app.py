import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

import json
import streamlit as st

from mcqgenerator.utils import read_file
from mcqgenerator.mcq_generator import generate_evaluate_chain
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

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

if 'quiz' not in st.session_state:
    st.session_state.quiz= None

@st.cache_data(show_spinner=False)
def run_chain(inputs):
    return generate_evaluate_chain.invoke(inputs)

with st.form("user_inputs"):
    uploaded_file=st.file_uploader("Uplaod a PDF or txt file")

    mcq_count=st.number_input("No. of MCQs", min_value=3, max_value=50)

    subject=st.text_input("Insert Subject",max_chars=50)

    tone=st.selectbox("Complexity Level Of Questions", ("Easy", "Medium", "Hard"))

    button=st.form_submit_button("Generate MCQs")

    if button:
        if uploaded_file is not None and mcq_count and subject and tone:
            with st.spinner("Generating MCQs..."):
                try:
                    logging.info(f"File uploaded: {uploaded_file.name}")
                    logging.info(f"MCQ count: {mcq_count}, Subject: {subject}, Tone: {tone}")

                    text=read_file(uploaded_file)
                    logging.info("File read successfully")

                    logging.info("Invoking generate_evaluate_chain")
                    response = run_chain({
                        "text": text,
                        "number": mcq_count,
                        "subject":subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    })
                    logging.info("Chain executed successfully")

                except Exception as e:
                    logging.error("Error during MCQ generation", exc_info=True)
                    st.error("Error occurred while generating MCQs")

                else:
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