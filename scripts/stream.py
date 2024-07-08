import streamlit as st
import json
import requests
import logging
from docx import Document
import io

logging.basicConfig(filename = "writing_assitance_log.txt" ,
                    filemode = "a" ,
                    format = "%(name)s - %(levelname)s - %(message)s" ,
                    datefmt="%d-%b-%y %H:%M:%S",
                    level = logging.DEBUG
                    )


# i button functionality
def info_button_with_text(widget_name, info_text):
    info_button = st.sidebar.button(f"ℹ️ {widget_name}")
    if info_button:
        st.sidebar.markdown(info_text)

# Save the doc
def save_to_word(text):
    doc = Document()
    doc.add_paragraph(text)
    doc_bytes = io.BytesIO()
    doc.save(doc_bytes)
    doc_bytes.seek(0)
    return doc_bytes

api_key = st.sidebar.text_input("Enter the OpenAI API key" , value = "")
topic = st.sidebar.text_input("Enter the  topic you want to write about")
words = st.sidebar.number_input("Words" , value = 1000 , step =100)
info_button_with_text("Words", "Enter how many words you want in your writing. LLMs do not under the concept of 'word' properly, so the number of words in the writing can be different than the number you have mentioned.")
target_audience = st.sidebar.text_input("What is the target audidence ?")
llm_model = st.sidebar.selectbox("LLM Model" , ("gpt-3.5-turbo-0125" ,  "gpt-3.5-turbo-16k"))
info_button_with_text("LLM Model", "Enter which LLM model you want to use. Different LLM models can have different capibilities and pricing. Check OpenAI page for more details.")
emb_model = st.sidebar.selectbox("Embedding Model" , ("text-embedding-3-small" , "text-embedding-3-large" , "text-embedding-ada-002"))
info_button_with_text("Embedding Model", "Enter which Embedding model you want to use. Different Embeding models can have different capibilities and pricing. Check OpenAI page for more details.")
num_pages_to_scrape = st.sidebar.number_input("No of web pages" , value =3 , step = 1)
info_button_with_text("No of web pages", "This Agent underneath the hood will go different Google pages to look for information , just like a human being. Higher value will make the process slower. Reccommended value in 3-5.")
temperature = st.sidebar.slider("Feel Adventerous" , 0.0 , 2.0 , 0.1)
info_button_with_text("Feel Adventerous", "Higher value will make the writing mode creative but may result in providing wrong information.")
max_tokens = st.sidebar.number_input("Max Tokens" , value = 2000 , step = 100)
info_button_with_text("Max Tokens", "OpenAI models charge on the basis of tokens. This parameter will determine how many tokens to print in output. If you feel like the answer in stopped in between abruptly, try increasing max token value.")

if "memory" not in st.session_state:
     st.session_state.memory = []

inputs = {"api_key" : api_key , "topic":topic , "words":words , "target_audience" : target_audience , "llm_model" : llm_model, "emb_model" : emb_model , "num_pages_to_scrape" : num_pages_to_scrape , "temperature" : temperature , "max_tokens" : max_tokens}
st.write("## Zero shot writing vs Agentic flow writing")
if st.button("Generate"):
    try:
        res = requests.post(url = "http://127.0.0.1:8000/api_call" , data = json.dumps(inputs))
        output = res.text # will return a json formatted str
        output_dict = json.loads(output) # convert it to a json for conviniance
        zero_shot_writing = output_dict["zero_shot_writing"]
        final_writing = output_dict["final writing"]
        memory_dict = {"topic" : topic , "words" : words , "target_audience" : target_audience , "llm_model" : llm_model , "emb_model" : emb_model , "num_pages_to_scraoe" : num_pages_to_scrape , "temperature" : temperature , "max_tokens" : max_tokens , "zero shot writing" : zero_shot_writing , "final writing" : final_writing }
        st.session_state.memory.append(memory_dict)
        st.text_area(label = "Zero shot learning" , value = zero_shot_writing , height= 1000)
        st.text_area(label = "Agent learning" , value = final_writing , height= 1000)
        doc_bytes = save_to_word(final_writing)
        st.download_button(label="Download", data=doc_bytes, file_name="output.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        # st.write(output_dict["score"])

    except Exception as e:
            logging.debug(f"An error occurured in streamlit {e}" , exc_info= True)
            logging.error(f"An error occurured in streamlit {e}" , exc_info= True)

#memory button
if st.sidebar.button("Past Writings"):
     for item in st.session_state.memory:
          st.write(item)
        
#clear memory
if st.sidebar.button("Clear memory"):
     st.session_state.memory.clear()


# st.sidebar.help("How many words Should this writing have ? LLMs do not understand the concept of 'words' properly so it will not match Exactly")

#memory call back
# def memory (topic , words , target_audience , llm_model , emb_model , num_pages_to_scrape , temperature , max_tokens , zero_shot_writing , final_writing):
     
#     return {"topic" : topic , "words" : words , "target_audience" : target_audience , "llm_model" : llm_model , "emb_model" : emb_model , "num_pages_to_scraoe" : num_pages_to_scrape , "temperature" : temperature , "max_tokens" : max_tokens , "zero shot writing" : zero_shot_writing , "final writing" : final_writing }

# def info_button_with_text(widget_name, info_text):
#     info_button = st.button("ℹ️")
#     if info_button:
#         st.markdown(f"ℹ️ *Info about {widget_name}:* {info_text}")

# # Example usage
# selected_value = st.slider("Select a value", 0, 100)
# info_button_with_text("Slider", "This widget allows you to select a value between 0 and 100.")

# import streamlit as st

# def info_button_with_text(widget_name, info_text):
#     info_button = st.button("ℹ️")
#     if info_button:
#         st.markdown(f"ℹ️ *Info about {widget_name}:* {info_text}")

# # Example usage for multiple sliders
# selected_value1 = st.slider("Slider 1", 0, 100)
# info_button_with_text("Slider 1", "This widget allows you to select a value between 0 and 100.")

# selected_value2 = st.slider("Slider 2", 0, 100)
# info_button_with_text("Slider 2", "This widget allows you to select a value between 0 and 100.")
