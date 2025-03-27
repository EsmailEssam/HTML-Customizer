from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import re
from dotenv import load_dotenv

def clean_html_output(response):
    if '```html' in response:
        # Remove html block markers
        cleaned = re.sub(r"```html|```", "", response).strip()
        return cleaned

def updater(html_template_body, fields_dict):
    # Load environment variables
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)

    generated_html_body = ""
    continue_generation = True
    max_iterations = 10  # Safety limit
    iteration_count = 0

    while continue_generation and iteration_count < max_iterations:
        prompt_template = PromptTemplate(
            input_variables=["html_template", "fields_dict", "generated_html"],
            template="""
            You are tasked with generating the updated body content of an HTML template in a step-by-step manner. Your goal is to produce a complete and well-structured HTML body, intelligently integrating any relevant data provided in the dictionary. The HTML body should be generated in multiple chunks, with each chunk aiming to be under 200 lines.

            **Instructions for Step-by-Step HTML Body Generation (Chunked):**

            **Step 1: Analyze the HTML Body Template:** Carefully examine the structure and content of the provided HTML template body. Understand the overall layout and the types of information it seems to contain.

            **Step 2: Check Previously Generated Content:** Review the `generated_html` from previous steps.

            **Step 3: Determine Generation Start Point:**
            * **If no HTML body has been generated yet (`{{generated_html}}` is empty):** Begin generating the HTML body content from the beginning, aiming to create a complete and coherent structure.
            * **If some HTML body content has already been generated:** Compare the `{{generated_html}}` with the HTML template body. Identify the point where the generated content appears to have stopped in terms of completing the overall HTML body structure or integrating the necessary information.

            **Step 4: Continue Generation:** From the identified stopping point, generate the next logical chunk of the HTML body (not exceeding approximately 200 lines). Ensure this chunk seamlessly follows the previously generated content and contributes towards completing the entire HTML body.

            **Step 5: Intelligent Data Integration (If Applicable):** If the provided data dictionary contains information that logically fits within the current chunk of HTML being generated, integrate it intelligently.

            **Step 6: Heuristic-Based Placement:** Employ reasonable heuristics for data placement in each chunk.

            **Step 7: Output Generation (Chunked):** Generate the next logical chunk of the HTML body.

            **Step 8: Ensure Coherence:** Maintain the overall structure and coherence of the generated HTML body with the provided template (if it has initial content).

            **Step 9: Completion Signal:** Only include the clear closing marker 'END_GENERATION' in your output **when you have finished generating the entire HTML body content in a logical and complete manner.** Do not add any additional text outside the HTML body content.

            Given the following HTML template body:
            {html_template}

            And the following dictionary of data:
            {{
            {fields_dict}
            }}

            So far, the generated HTML body is:
            {generated_html}

            Generate the next chunk of the HTML body:
            """
        )

        updater_chain = LLMChain(llm=llm, prompt=prompt_template)

        llm_result = updater_chain.run(
            html_template=html_template_body,
            fields_dict=fields_dict,
            generated_html=generated_html_body
        )

        cleaned_chunk = clean_html_output(llm_result)
        generated_html_body += str(cleaned_chunk).strip() + "\n"

        if "END_GENERATION" in str(cleaned_chunk):
            continue_generation = False
            generated_html_body = generated_html_body.replace("END_GENERATION", "").strip()
            break

        iteration_count += 1

    return generated_html_body.strip()