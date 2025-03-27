from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import re
import os
from dotenv import load_dotenv
import json

def clean_json_output(response):
    # Remove code block markers and extract JSON
    cleaned = re.sub(r"```json|```", "", response).strip()
    return json.loads(cleaned)

def analyzer(html_template):
    # Load environment variables
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)

    analysis_prompt = PromptTemplate(
                input_variables=["html_template"],
                template="""
                You are provided with the content of an HTML file. 
                Your task is to analyze the HTML and identify all data points that are likely candidates for dynamic updates. 
                For example, if the HTML contains a company name, you should include a key called company_name. 
                Your output must be a valid JSON where each key represents a piece of data that might need updating and each value is set to None.

                Instructions:
                    1. Analyze the provided HTML content thoroughly.
                    2. Identify any elements or data that could be updated, such as company names, addresses, phone numbers, dates, or any other placeholders.
                    3. For each identified data point, create a corresponding key in a dictionary. The key should be descriptive (e.g., company_name, address, etc.).
                    4. Set the value for each key to None.
                    5. Return ONLY the JSON dictionary without any additional text.
                
                HTML Template:
                {html_template}
                """
            )


    analysis_chain = LLMChain(llm=llm, prompt=analysis_prompt)

    llm_result = analysis_chain.run(html_template=html_template)
    
    fields_dict = clean_json_output(llm_result)
    
    return fields_dict