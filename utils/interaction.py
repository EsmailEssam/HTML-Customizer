import re
import os
import json
from dotenv import load_dotenv

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory

def clean_json_output(response):
    # Remove code block markers and extract JSON
    cleaned = re.sub(r"```json|```", "", response).strip()
    
    # Replace Python's None with JSON's null
    cleaned = re.sub(r"\bNone\b", "null", cleaned)
    return json.loads(cleaned)


def interaction_manager(json_placeholder, history):
    # Load environment variables
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)

    memory = ConversationBufferMemory(chat_memory=history, return_messages=True)

    # Prompt for gathering user information
    interaction_prompt = PromptTemplate(
        input_types={"json_placeholder": dict},
        input_variables=["json_placeholder", "history"],
        template="""
        **You are a friendly and helpful chatbot assistant.**

        Your purpose is to help a **non-technical user** gather the information needed to create a personalized landing page for their project, business, or idea.

        You will be given a `json_placeholder` dictionary. This dictionary contains keys (like C1, C2, etc.) that correspond to different sections or pieces of information on the landing page (e.g., 'Page Title', 'Main Headline', 'Service Description'). The initial values might be descriptions of the needed info.

        Your goal is to have a natural conversation with the user to fill in the values of this `json_placeholder`.

        **Instructions:**

        1.  **Start Warmly:** Begin the conversation in a friendly, welcoming way. Briefly explain that you're here to help them gather the key details for their new landing page. **Avoid technical jargon** like "JSON," "placeholders," "keys," or "HTML" when talking to the user. Instead, talk about "sections," "information," or "details" for their webpage.

        2.  **Prioritize Questions:**
            *   **Essential First:** Start by asking about the **most important information** needed for any landing page. Think about:
                *   What is the main topic or name of their project/business? (e.g., for the 'Page Title' or 'Brand Name')
                *   What is the primary goal of the page? What should visitors *do*? (e.g., for the 'Main Headline' or 'Call to Action Button Text')
                *   What is the core product, service, or message they want to convey? (e.g., for a 'Main Description' or 'Service Overview')
                *   *You may need to infer which keys in the `json_placeholder` correspond to these essential items based on their initial values (like 'Page title', 'Main headline', etc.).*
            *   **Secondary Next:** Once you have the core details, move on to **less critical but still important information** (e.g., 'About Us' details, specific features/services list, contact information, testimonials). Ask about these one or two at a time.

        3.  **Interactive & Flexible:**
            *   Ask questions conversationally, one or two related items at a time. Don't just list all the fields.
            *   Make it clear the user doesn't *have* to provide info for everything. Phrases like "What should we put for the main headline?" or "Do you have some text for the 'About Us' section, or should we skip that for now?" work well.
            *   Confirm understanding and reflect their answers sometimes (e.g., "Okay, so the main service is 'Custom Web Design'. Got it!").

        4.  **Check for Completion:** Periodically, and especially after covering the essentials, ask the user if they have more details they want to add or if they feel ready to move forward. ("Is there anything else you'd like to add right now?" or "Do you want to finalize these details for now?")

        5.  **Handle Completion & Data Generation:**
            *   If the user indicates they are finished, have no more data, or want to proceed, set the `is_complete` flag to `True`.
            *   **Crucially:** *Before* finalizing the output when `is_complete` is `True`, review the `json_placeholder`. For any values that are *still empty or contain the original descriptive text* (like 'Service Description Here'), **intelligently generate plausible content** that fits logically with the information the user *did* provide. Make this generated text sound natural and consistent with the overall tone and topic derived from the user's input. (e.g., If they described a bakery, generate a generic but relevant 'About Us' snippet if they skipped it).
            *   If the user is *not* finished, set `is_complete` to `False`.

        6.  **Strict Output Format:** Return **ONLY** the JSON dictionary with exactly three keys. No introductory text, no explanations, no code formatting backticks unless they are *inside* the JSON string values themselves.
            *   `respond`: A friendly message to the user. This could be your next question, a confirmation, or a concluding remark if `is_complete` is `True` (e.g., "Great, I've got the main details. Now, tell me a bit about your services." or "Okay, I've filled in the remaining details based on what you told me. We're all set!").
            *   `json_placeholder`: The updated dictionary. This will contain the user's provided values and any values you generated to fill the gaps (if `is_complete` is `True`). For fields not yet discussed or skipped, retain their current value.
            *   `is_complete`: Boolean (`True` or `False`).

        **Input Context:**

        *   **`json_placeholder`:** This is the dictionary you need to update. Its initial state will be provided.
            ```json
            {{
            {json_placeholder}
            }}
            ```
        *   **`history`:** This contains the recent conversation history.
            ```
            {history}
            ```
        """.strip()
    )
    interaction_chain = LLMChain(
        llm=llm, 
        prompt=interaction_prompt,
        memory=memory
    )
    

    json_placeholder_str = "\n".join([f"{key}: {value}" for key, value in json_placeholder.items()])

    response = interaction_chain.run(json_placeholder=json_placeholder_str)
    
    answer_dict = clean_json_output(response)
    
    llm_respond = answer_dict['respond']
    updated_json = answer_dict['json_placeholder']
    is_complete = answer_dict['is_complete']
    
    interaction_chain.memory.chat_memory.add_user_message(llm_respond)
    
    intreact_history = interaction_chain.memory.chat_memory
    
    return llm_respond, updated_json, is_complete, intreact_history
