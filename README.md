
# Agentic Writing Assistant

Currently, we primarily use LLMs in zero-shot mode, where we prompt a model to generate its final output token by token without making revisions. This is similar to asking someone to write an essay from beginning to end without any chance to backtrack, yet expecting a high-quality result. Due to these challenges, LLMs sometimes produce suboptimal outputs.

Another significant issue is that LLMs lack knowledge about recent events. If asked about a current topic, they might generate completely hallucinated responses that are factually inaccurate.  

To tackle these challenges, I propose an agentic workflow using OpenAI's Large Language Models that emulates human writing. In this workflow, the LLM is prompted iteratively multiple times (averaging 15 times per user query), each time refining and enhancing the text. This method is sometimes referred to as few-shot generation. To gauge its effectiveness, consider that GPT-3.5 (in zero-shot mode) was 48.1% correct, while GPT-4 (in zero-shot mode) improved to 67.0%. However, the leap from GPT-3.5 to GPT-4 is overshadowed by the gains achieved through an iterative agent workflow. When wrapped in an agent loop, GPT-3.5 reaches up to 95.1% accuracy.

This workflow consists of five distinct steps:  

1. Generator
2. Reflector
3. Modifier
4. Web search
5. Data Processing
6. Add data from the Internet











## Generator

This step involves the zero-shot generation mode, where a text is composed based on the given topic.
## Reflector

This step serves as a critique of the writing. After composing a text on a given topic, we typically evaluate it ourselves to identify areas for improvement. This step mimics that process, critiquing the text based on articulation, engagement, informativeness, and proper formatting.
## Modifier

The text produced by the Generator (in zero-shot mode), along with the critiques from the Reflector, is sent to the Modifier layer to enhance the writing based on the Reflector's feedback.

This generation-criticism-modification cycle repeats several times (default is 3 times), with each iteration refining and improving the text.
## Web Search

When writing about a topic, we often search the internet for relevant information. This step replicates that process. It involves searching the web for pertinent and recent information (by default, from the last three years) and scraping text from these pages using the Beautiful Soup module in Python.

After processing, this web data is fed to the LLM, addressing the issue of LLMs lacking current information.
## Data Processing

After extracting data from web pages, all the information is combined into a single Python string. This string is then divided into chunks using **Langchain's** default **Recursive Character Text Splitter**. The default chunk size and chunk overlap are set to **1500** and **100**, respectively. These chunks are vectorized using an embedding model from OpenAI, and the resulting vectors are indexed in FAISS. A similarity search is performed, followed by re-ranking. After the similarity search, the **top-k** chunks (default is half of the total chunks) are taken,then these top-k chunks are reanked using **ms-marco-MiniLM-L-6-v2** reranker model. after reranking top 6 (default value) are selected. These chunks are then used to modify the text.
## Add information from the internet

After retrieving the top 6 chunks (default value), each chunk is used to make the previously generated text more informative and up-to-date.
## Implementation and Deployment

The entire workflow is implemented in Python. It is API-fied using FASTAPI, and the frontend is created with Streamlit. The server can be spun up as follows:

```
# FastAPI server
cd C:\Users\itouf\OneDrive\my_proj\projvenv\Scripts
activate
cd C:\Users\itouf\OneDrive\my_proj
uvicorn fast:app --reload

# Streamlit server
cd C:\Users\itouf\OneDrive\my_proj\projvenv\Scripts
activate
cd C:\Users\itouf\OneDrive\my_proj
python -m streamlit run stream.py

```
Below is a screenshot of fronted inerface :  

![App Screenshot](https://github.com/itoufik/Agentic-Writing-Assistant/blob/main/Screenshots/frontend.png)

In this simple UI, most details are abstracted away from the user. Users can enter their OpenAI API key, the topic they want to write about, the target audience, and the desired word count. They can choose the LLM and Embedding model from a dropdown menu. Additionally, they can adjust the number of pages to scrape from the internet, the temperature value, and the maximum new tokens. Each button (or widget, in Streamlit terminology) has an "[i]" button to assist users in selecting the appropriate values based on their needs. Users can also review previous writings by clicking the "Past Writing" button.

To generate a piece of text, users simply click the "Generate" button. Upon completion, both the zero-shot writing and the Agentic writing will be displayed in the UI for comparison. Users can also download the writing in .docx format by clicking the "Download" button beneath the Agentic writing.