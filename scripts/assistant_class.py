import openai
from openai import OpenAI
import json
import numpy as np
import math
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import faiss
from sentence_transformers import CrossEncoder

# Langchain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter

#Loading the config file
with open("config.json") as file:
    config_data = json.load(file)

# logging
logging.basicConfig(filename = "writing_assitance_log.txt" ,
                    filemode = "a" ,
                    format = "%(name)s - %(levelname)s - %(message)s" ,
                    datefmt="%d-%b-%y %H:%M:%S",
                    level = logging.DEBUG
                    )

class assistance():

    def __init__(self , api_key : str , topic : str, words : int , target_audience : str , llm_model : str , emb_model : str, num_pages_to_scrape : int , temperature : int, max_tokens : int):
        self.api_key = api_key
        self.client = OpenAI(api_key = self.api_key)
        self.topic = topic
        self.words = words
        self.target_audience = target_audience
        self.llm_model = llm_model
        self.emb_model = emb_model
        self.num_pages_to_scrape = num_pages_to_scrape
        self.temperature = temperature
        self.max_tokens = max_tokens

    def formulate_topic(self):
        try:
            out = f"Write about {self.topic}"
            if self.target_audience:
                out = out + f" The target audience for this topic are {self.target_audience}."
            if self.words:
                out = out + f" Complete the writing within '{self.words}' words"
            logging.info(f"Formulated topic is: {out}")

            return out
        
        except Exception as e:
            logging.debug(f"An error occurured while formulating the topic from the inputs {e}" , exc_info= True)
            logging.error(f"An error occurured while formulating the topic from the inputs {e}" , exc_info= True)

    def get_gpt_response(self , messages):
        try:
            stream = self.client.chat.completions.create(   
                model= self.llm_model,
                messages = messages,
                stream=False,
                temperature = self.temperature, # varies from 0 to 2
                top_p = config_data.get("top_p" , 1), # varies from 0 to 2
                max_tokens = self.max_tokens
                )
            logging.info(f"Loaded gpt with llm model {self.llm_model}, temperature {self.temperature} , max_tokens {self.max_tokens}")
            
            return stream.choices[0].message.content   

        except Exception as e:
            logging.debug(f"An error occurured while loading the GPT {e}" , exc_info= True)
            logging.error(f"An error occurured while loading the GPT {e}" , exc_info= True)
    
    def generator(self , formulated_topic):
        try:
            system_message = """
            You are a writing assistance
            """
            user_message = formulated_topic
            messages =  [
            {'role':'system',
            'content': system_message},
            {'role':'user',
            'content': user_message},
            ]

            response = self.get_gpt_response(messages)
            logging.info("Succesfully ran Generator function")

            return response
        
        except Exception as e:
            logging.debug(f"An error occurured while using the Generator function {e}" , exc_info= True)
            logging.error(f"An error occurured while loading the Generator Function {e}" , exc_info= True)

    
    
    def reflector(self , writing):
        try:
            delimiter = "####"
            system_message = f"""
            You are an writing assistant who is an expert in improving a piece of writing by constructively critising it.
            """
            user_message = f"""
            You will be given a piece of writing which will be delimited with four hashtags i,e, {delimiter} you need to constructively cricise the piece of writing.

            Criticise on the basis of the following grounds:

            1. Is it well articulated? How to make it more articulated?
            2. Is this writing engaging? How to make it more engaging?
            3. Is it informative? How to make it more informative?
            4. Is the writing properly formatted? How to improve the formatting?

            writing: {delimiter}{writing}{delimiter}

            """
            messages =  [
            {'role':'system',
            'content': system_message},
            {'role':'user',
            'content': user_message},
            ]
            out = self.get_gpt_response(messages)
            logging.info("Sucessfully ran Reflector function")

            return out.strip(delimiter)
        
        except Exception as e:
            logging.debug(f"An error occurured while using the Reflector function {e}" , exc_info= True)
            logging.error(f"An error occurured while loading the Reflector Function {e}" , exc_info= True)

    
    def modifier(self , writing , improvements):
        try:               
            delimiter_writing = "####"
            delimiter_improvements = "$$$$"
            system_message = f"""
            You are a writing assistant.
            """
            user_message = f"""
            You will be given a piece of writing which will be delimited with four hashtags i,e, {delimiter_writing}. You will also be given some points to improve the piece of writing which will be deliomited with {delimiter_improvements} characters. You need to improve the writing based on the points of improvements. Only output the improved writing and nothing else. Complete the writing within '{self.words}' words strictly.

            writing: {delimiter_writing}{writing}{delimiter_writing}
            points to improve: {delimiter_improvements}{improvements}{delimiter_improvements}
            """

            messages =  [
            {'role':'system',
            'content': system_message},
            {'role':'user',
            'content': user_message},
            ]
            out = self.get_gpt_response(messages)
            out = out.strip(delimiter_writing)
            out = out.strip(delimiter_improvements)
            logging.info("Successfully ran Modifier function")

            return out
        
        except Exception as e:
            logging.debug(f"An error occurured while using the Modifier function {e}" , exc_info= True)
            logging.error(f"An error occurured while loading the Modifier Function {e}" , exc_info= True)

    
    def google_search_links(self):
        try:
            current_datetime = datetime.now()
            previous_datetime = current_datetime - timedelta(days=365 * 2) # taking information from the last 2 years
            formatted_date_current = current_datetime.strftime("%Y-%m-%d")
            formatted_date_previous = previous_datetime.strftime("%Y-%m-%d")
            time_range = formatted_date_previous + ":" + formatted_date_current
            api_key = config_data.get("google_api_key")
            search_engine_id = config_data.get("google_search_engine_id")

            url = "https://www.googleapis.com/customsearch/v1"
            params = {
            "q" : self.topic,
            "key" : api_key,
            "cx" : search_engine_id,
            "dateRestrict" : time_range,
            "lr": "lang_en",
            "num": self.num_pages_to_scrape
            }

            response = requests.get(url , params = params)
            results = response.json()["items"]
            urls = [item["link"] for item in results]
            logging.info(f"The links that are retrived from the web are {urls}")

            return urls
        
        except Exception as e:
            logging.debug(f"An error occurured while retriving the urls {e}" , exc_info= True)
            logging.error(f"An error occurured while retriving the urls {e}" , exc_info= True)
    
    @staticmethod
    def scrap_text_from_url(urls):
        try:
            all_text = ""
            for url in urls:
                try:
                    html_text = requests.get(url).text
                    soup = BeautifulSoup(html_text , "lxml")
                    all_text = all_text + soup.text.strip()
                    logging.info(f"Succesfully scraped texts from the {url} url")

                except Exception as e:
                    logging.debug(f"Could not scrape this url {url}")
                    continue
                
            return all_text
        
        except Exception as e:
            logging.debug(f"An error occurured while scraping text from the links {e}" , exc_info= True)
            logging.error(f"An error occurured while scraping text from the links {e}" , exc_info= True)


    @staticmethod
    def split_string(all_text):
        try:
            chunk_size = config_data.get("chunk_size" , 350)
            overlap = config_data.get("chunk_overlap" , 50)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=overlap)
            all_splits = text_splitter.split_text(all_text)
            logging.info(f"Chunking is successful. No of Chunks are {len(all_splits)}")

            return all_splits
        
        except Exception as e:
            logging.debug(f"An error occurured while chunking the text {e}" , exc_info= True)
            logging.error(f"An error occurured while chunking the text {e}" , exc_info= True)

    
    def get_embedding(self , all_chunks):
        try:
            all_vecs = []
            for chunk in all_chunks:
                chunk = chunk.replace("\n", " ")
                vec = self.client.embeddings.create(input = [chunk], model=self.emb_model).data[0].embedding
                all_vecs.append(vec)
            logging.info(f"Succesfully embedded the chunks using {self.emb_model} and no of vectors are {len(all_vecs)}")

            return np.array(all_vecs)
        
        except Exception as e:
            logging.debug(f"An error occurured while embedding {e}" , exc_info= True)
            logging.error(f"An error occurured while embedding {e}" , exc_info= True)

    @staticmethod
    def index_vectors(all_vecs):
        try:
            d=all_vecs.shape[1]# Dimention of each vector
            index=faiss.IndexFlatL2(d)
            assert index.is_trained
            index.add(all_vecs)
            logging.info(f"Indexing is Done. Total No of vectors in the index are {index.ntotal}")

            return index
        
        except Exception as e:
            logging.debug(f"An error occurured while indexing {e}" , exc_info= True)
            logging.error(f"An error occurured while indexing {e}" , exc_info= True)
    
    def retrive_chunks(self , index , all_chunks):
        try:
            n = len(all_chunks)
            k = math.floor(n/2)
            query = self.topic
            xq=self.get_embedding([query])
            D,I=index.search(xq , k)
            matched_chunks = [all_chunks[i] for i in I[0]]
            logging.info(f"Successfully completed similarity search and retrived {len(matched_chunks)} similar chunks")

            return matched_chunks
        
        except Exception as e:
            logging.debug(f"An error occurured while doing the similarity search {e}" , exc_info= True)
            logging.error(f"An error occurured while doing the similarity search {e}" , exc_info= True)

    def rerank(self , matched_chunks):
        try:
            model_path = config_data.get("reranker_model_path" , None)
            cross_encoder = CrossEncoder(model_path)
            pairs = [[self.topic, matched_chunk] for matched_chunk in matched_chunks]
            scores = cross_encoder.predict(pairs)
            order = []
            for o in np.argsort(scores)[::-1]:
                order.append(o)
            logging.info(f"Reranking is done")

            return order
        
        except Exception as e:
            logging.debug(f"An error occurured while using the Reranker {e}" , exc_info= True)
            logging.error(f"An error occurured while loading the Reranker {e}" , exc_info= True)

    @staticmethod
    def get_context_list(order , matched_chunks):
        try:
            k = config_data.get("no_rel_docs" , 6)
            order = order[:k]
            reordered_chunks = [matched_chunks[o] for o in order]
            logging.info(f"After reranking the {len(reordered_chunks)} are retrived and those chunks are: {reordered_chunks}")

            return reordered_chunks
        
        except Exception as e:
            logging.debug(f"An error occurured while getting context after Reranking {e}" , exc_info= True)
            logging.error(f"An error occurured while getting context after Reranking {e}" , exc_info= True)
    
    def modification_from_web(self , formatted_topic , writing , web_search_docs):
        try:
            delimiter_writing = "####"
            delimiter_context= "$$$$"
            delimiter_formatted_topic = ">>>>"
            system_message = f"""
            You are a writing assistant.
            """
            user_message = f"""
            You will be given a writing which will be delimited with four hashtags i,e, {delimiter_writing} on a topic which will be delimited with {delimiter_formatted_topic}. You will also be given a piece of text which is scraped from the internet, delimited with {delimiter_context}. This piece of text is scraped from internet and it has the potential to improve the quality of the writing. Your job is to understand given the topic and piece of text scraped from the internet, whether piece of text scraped from the internet can improve the quality of the writing. If it can then, then based on the piece of text from the internet improve the writing on the basis of articulation, engagement , information and formatting. Output the modified text only and nothing else. Complete the writing within '{self.words}' words strictly. 
            
            Even if you are using piece of text from the internet to modify the writing , you do no need to mention this explicitly anywhere. Just the Output the modfied without mentioning the source ever. Give the output in such a format that it can easily be used without any post processing.

            writing : {delimiter_writing}{writing}{delimiter_writing}
            topic : {delimiter_formatted_topic}{formatted_topic}{delimiter_formatted_topic}
            piece of text from the internet : {delimiter_context}{web_search_docs}{delimiter_context}

            """
            messages =  [
            {'role':'system',
            'content': system_message},
            {'role':'user',
            'content': user_message},
            ]

            response = self.get_gpt_response(messages)
            response = response.strip(delimiter_writing)
            response = response.strip(delimiter_context)
            response = response.strip(delimiter_formatted_topic)
            logging.info("Successfully used modification from web function")

            return response
        
        except Exception as e:
            logging.debug(f"An error occurured while using the modification using web function {e}" , exc_info= True)
            logging.error(f"An error occurured while using modification using the web function {e}" , exc_info= True)

        

