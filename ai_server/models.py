import torch 
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, AutoModelForSeq2SeqLM
from langchain_huggingface import HuggingFacePipeline
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings

base_model_path = "./models/"
chat_pipeline = None

def init_chat_model():
    global device, chat_pipeline,base_model_path
    if chat_pipeline is not None:
        return chat_pipeline

    model_path = base_model_path + "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

    model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="cuda"
            )
    tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="left", truncation=True)

    pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            eos_token_id=tokenizer.eos_token_id
            )
    chat_pipeline = HuggingFacePipeline(pipeline=pipe)
    return chat_pipeline

# Initialize the embeddings model
def init_embeddings():
    global base_model_path
    return HuggingFaceEmbeddings(model_name=base_model_path + "sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cuda"})

# Create a chain for summarizing text
def get_text_summary_chain():
    global base_model_path
    model_path = "google-t5/t5-small"

    model = AutoModelForSeq2SeqLM.from_pretrained(
        base_model_path + model_path, 
        torch_dtype=torch.float16, 
        device_map="cuda"
    )

    tokenizer = AutoTokenizer.from_pretrained(model_path)

    pipe = pipeline("summarization", model=model, tokenizer=tokenizer)
    pipe = HuggingFacePipeline(pipeline=pipe)

    prompt_text = """You are an assistant with diabetes medical expertise tasked with summarizing tables and text. 
    Give a concise summary of the table or text. Table or text chunk: {element}"""

    prompt = ChatPromptTemplate.from_template(prompt_text)
    return {"element": lambda x: x} | prompt | pipe | StrOutputParser()
