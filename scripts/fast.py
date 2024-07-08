from fastapi import FastAPI
from pydantic import BaseModel

# importing the main function
from writing_assistant import main

#logging
import logging
logging.basicConfig(filename = "writing_assitance_log.txt" ,
                    filemode = "a" ,
                    format = "%(name)s - %(levelname)s - %(message)s" ,
                    datefmt="%d-%b-%y %H:%M:%S",
                    level = logging.DEBUG
                    )

app = FastAPI()

class Main_Input(BaseModel):
    api_key: str
    topic: str
    words: int
    target_audience : str
    llm_model : str
    emb_model : str
    num_pages_to_scrape : int
    temperature : float
    max_tokens : int

@app.post("/api_call")
def main_call(input_data : Main_Input):
    try:
        out = main(api_key = input_data.api_key , topic= input_data.topic , words = input_data.words , target_audience= input_data.target_audience , llm_model= input_data.llm_model , emb_model= input_data.emb_model , num_pages_to_scrape= input_data.num_pages_to_scrape , temperature= input_data.temperature , max_tokens= input_data.max_tokens)
        logging.info("FASTAPI response is genarated")

        return out

    except Exception as e:
        logging.debug(f"An error occurured while using FASTAPI {e}" , exc_info= True)
        logging.error(f"An error occurured while using FASTAPI {e}" , exc_info= True)