import os
import sys
import argparse
import subprocess
from pathlib import Path
import gradio as gr

# Add the curret directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multimodal_rag import DiabetesKnowledgeBase

# Check if Ollama and required models are installed
def check_models():
    # Check if Ollama server is running
    try:
        response = subprocess.run(["curl", "-s", "http://localhost:11434/api/version"], 
                                 check=True, capture_output=True, shell=True)
        print("Ollama server is running.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Ollama server is not running.")
        return False
    
    # Check for required models
    try:
        result = subprocess.run(["ollama", "list"], check=True, capture_output=True, shell=True, text=True)
        output = result.stdout
        
        if "llama2" not in output:
            print("ERROR: llama2 model is not installed. Please run: ollama pull llama2")
            return False
            
        if "llava" not in output:
            print("ERROR: llava model is not installed. Please run: ollama pull llava")
            return False
            
        print("All required models are installed.")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: Unable to check installed models. Please verify Ollama is properly installed.")
        return False
    

def main():
    parser = argparse.ArgumentParser(description="Diabetes Medical Chatbot")
    parser.add_argument("--data_dir", type=str, default="./data", help="Directory containing diabetes PDF files")
    parser.add_argument("--skip_processing", action="store_true", help="Skip PDF processing and use existing knowledge base")
    args = parser.parse_args()
    
    # Create data directory if it does not exist
    Path(args.data_dir).mkdir(parents=True, exist_ok=True)
    
    # Check if models are available
    check_models()
    
    # Initialize the knowledge base
    print(f"Initializing the knowledge base from: {args.data_dir} ...")
    kb = DiabetesKnowledgeBase(args.data_dir)
    
    # Process PDF files if not skipped
    if not args.skip_processing:
        kb.process_all_pdfs()
    else:
        print("Skipping PDF processing. Using existing knowledge base.")
        print(kb.get_processed_files_status())
    
    # Process user question and return answer
    def chat_response(message, history):
        try:
            response = kb.answer_question(message)
            print(f"Chatbot response: {response}")  # Debugging
            return response
        except Exception as e:
            print(f"Chatbot error: {str(e)}")  # Debugging
            return f"Sorry, I encountered an error: {str(e)}"
    
    # Create a Gradio interface
    demo = gr.ChatInterface(
        chat_response,
        title="Diabetes Medical Assistant",
        description="Ask me questions about diabetes. "
                    "I'm powered by a knowledge base of medical PDFs specialized in diabetes care.",
        theme="soft",
        examples=[
            """
            What are the four broad categories of diabetes other than Type 1 and Type 2?
            How do the World Health Organization (WHO) and the American Diabetes Association (ADA) define diabetes based on fasting plasma glucose (FPG) levels?
            What minimum criteria are recommended for diagnosing diabetic neuropathy?
            
            """
        ]
    )
    
    demo.launch(share=True)
    
if __name__ == "__main__":
    main()