import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

import json
import traceback
import pandas as pd
from mcqgenerator.utils import read_file, get_table_data
import streamlit as st
from mcqgenerator.mcq_generator import generate_evaluate_chain
from mcqgenerator.logger import logging

with open(r'.\response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

st.title("MCQs Generator Application with LangChain 🦜⛓️")

with st.form("user_inputs"):
    uploaded_file=st.file_uploader("Uplaod a PDF or txt file")

    mcq_count=st.number_input("No. of MCQs", min_value=3, max_value=50)

    subject=st.text_input("Insert Subject",max_chars=20)

    tone=st.text_input("Complexity Level Of Questions", max_chars=20, placeholder="Simple")

    button=st.form_submit_button("Generate MCQs")

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("Loading..."):
            try:
                text=read_file(uploaded_file)
                response = generate_evaluate_chain.invoke({
                    "text": text,
                    "number": mcq_count,
                    "subject":subject,
                    "tone": tone,
                    "response_json": json.dumps(RESPONSE_JSON)
                })

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")

            else:
                usage = response["raw"].usage_metadata
                print("Prompt Tokens:", usage.get("input_tokens"))
                print("Completion Tokens:", usage.get("output_tokens"))
                print("Total Tokens:", usage.get("total_tokens"))
                
                if isinstance(response, dict):
                    quiz=response.get("parsed", None)
                    if quiz is not None:
                        table_data=get_table_data(quiz)
                        if table_data is not None:
                            df=pd.DataFrame(table_data)
                            df.index+=1
                            st.dataframe(df)
                        else:
                            st.error("Error in the table data")
                else:
                    st.write(response)