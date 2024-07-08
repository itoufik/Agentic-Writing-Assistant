from assistant_class import assistance

#logging
import logging
logging.basicConfig(filename = "writing_assitance_log.txt" ,
                    filemode = "a" ,
                    format = "%(name)s - %(levelname)s - %(message)s" ,
                    datefmt="%d-%b-%y %H:%M:%S",
                    level = logging.DEBUG
                    )

#Loading the config file
import json
with open("config.json") as file:
    config_data = json.load(file)

def main(api_key , topic , words , target_audience , llm_model , emb_model, num_pages_to_scrape , temperature , max_tokens):
    try: 
        assistance_instance = assistance(
        api_key= api_key,
        topic = topic,
        words = words,
        target_audience = target_audience ,
        llm_model= llm_model,
        emb_model= emb_model,
        num_pages_to_scrape= num_pages_to_scrape,
        temperature=temperature,
        max_tokens=max_tokens
        )
        logging.info("Instance creation is successful.")
        formulated_topic = assistance_instance.formulate_topic()
        zero_shot_writing = assistance_instance.generator(formulated_topic)
        logging.info(f"The Zero Shot writing is {zero_shot_writing}")
        generator1 = zero_shot_writing # keeping zero shot writing as it is
        num_loop = config_data.get("num_loop" , 3)
        for _ in range(num_loop):
            improvements = assistance_instance.reflector(generator1)
            improved_wri = assistance_instance.modifier(writing=generator1 , improvements= improvements)
            generator1 = improved_wri
        logging.info(f"After improving the the writing from GPT for {num_loop} times the writing is {improved_wri}")
        urls = assistance_instance.google_search_links()
        all_text = assistance_instance.scrap_text_from_url(urls)
        chunks = assistance_instance.split_string(all_text=all_text)
        all_embs = assistance_instance.get_embedding(all_chunks=chunks)
        index = assistance_instance.index_vectors(all_vecs=all_embs)
        matched_chunks = assistance_instance.retrive_chunks(index ,chunks)
        orders= assistance_instance.rerank(matched_chunks=matched_chunks)
        context = assistance_instance.get_context_list(orders , matched_chunks)
        logging.info(f"The context from the web is {context}")
        len_context = len(context)
        for contex_index in range(len_context):
            final_writing = assistance_instance.modification_from_web(formatted_topic=formulated_topic  , writing=improved_wri , web_search_docs=context[contex_index])
            improved_wri = final_writing
        logging.info(f"Final Agentic writing is {final_writing}")
        # scores = assistance_instance.compare_outputs(formulated_topic = formulated_topic , zero_shot_writing = zero_shot_writing , agentic_workflow_writing = final_writing)

        return { "topic" : assistance_instance.topic , "target audience" : assistance_instance.target_audience,"words" : assistance_instance.words , "zero_shot_writing" : zero_shot_writing , "final writing" : final_writing}
    
    except Exception as e:
        logging.debug(f"An error occurured while formulating the topic from the inputs {e}" , exc_info= True)
        logging.error(f"An error occurured while formulating the topic from the inputs {e}" , exc_info= True)
        return { "topic" : assistance_instance.topic , "target audience" : assistance_instance.target_audience,"words" : assistance_instance.words , "zero_shot_writing" : "" , "final writing" : "An error occured while generating the Agentic answer please check the logs for more information."}