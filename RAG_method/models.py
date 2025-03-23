import os
import base64
import requests
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings

# Initialize the text-based LLM (llama2)
def init_text_model():
    return Ollama(model="llama2")

# Initialize the chat-based LLM (Llama2)
def init_chat_model():
    return ChatOllama(model="llama2")

# Initialize the embeddings model
def init_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create a chain for summarizing text
def get_text_summary_chain():
    prompt_text = """You are an assistant with diabetes medical expertise tasked with summarizing tables and text. 
    Give a concise summary of the table or text. Table or text chunk: {element}"""
    
    prompt = ChatPromptTemplate.from_template(prompt_text)
    model = init_text_model()
    return {"element": lambda x: x} | prompt | model | StrOutputParser()

# Process an image with LLaVA to get a description
# Process an image with LLaVA using Ollama API
def process_image_with_llava(image_path):
    if not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    
    try:
        # Read the image and encode it as base64
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode("utf-8")
        
        # Prepare the API request
        url = "http://localhost:11434/api/generate"
        prompt = "Describe this image in detail. If it contains graphs, charts, or illustrations related to diabetes, explain what they show regarding diabetes management, treatment, or monitoring."
        
        payload = {
            "model": "llava",
            "prompt": prompt,
            "images": [image_data],
            "stream": False
        }
        
        # Make the API request
        response = requests.post(url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response received")
        else:
            return f"API request failed with status code: {response.status_code}"
        
    except Exception as e:
        return f"Error processing image: {str(e)}"
