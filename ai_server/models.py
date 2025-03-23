import os
from PIL import Image
import torch 
from transformers import AutoProcessor, LlavaForConditionalGeneration, AutoModelForCausalLM, AutoTokenizer, pipeline, AutoProcessor, AutoModelForSeq2SeqLM, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline
from langchain_community.llms import HuggingFaceHub
#from langchain_community.llms import HuggingFaceHub, HuggingFacePipeline
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
#from peft import PeftModel

chat_pipeline = None

# Initialize the text-based LLM (llama2)
def init_text_model():
    # mental illness #2 Electric Boogaloo
    return init_chat_model()
    return HuggingFaceHub(
            repo_id="meta-llama/Llama-2-7b-hf",
            model_kwargs={"temperature": 0.8},
            huggingfacehub_api_token=os.getenv("HF_API_TOKEN")
            )
# Initialize the chat-based LLM (Llama2)
def init_chat_model():
    global device, chat_pipeline
    if chat_pipeline != None:
        return chat_pipeline

    #model_path = "/ai_server/models/NousResearch/Llama-2-7b-chat-hf"
    model_path = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    adapter_path = "./model_params"

    model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            #quantization_config=bnb_config,
            device_map="cuda"
            )
    tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="left", truncation=True)

    #model = PeftModel.from_pretrained(model, adapter_path)
    #model = model.merge_and_unload()
    #model_path = "google/flan-t5-base"

    #model = AutoModelForSeq2SeqLM.from_pretrained(
    #    model_path, 
    #    torch_dtype=torch.float16, 
    #    device_map="cuda",
    #)
    #tokenizer = AutoTokenizer.from_pretrained(model_path)

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
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device": "cuda"})

# Create a chain for summarizing text
def get_text_summary_chain():
    model_path = "google-t5/t5-small"

    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_path, 
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

# Process an image with LLaVA to get a description
llava_model = None
llava_processor = None
def process_image_with_llava(image_path):
    global device
    if not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    global llava_model
    global llava_processor
    if llava_model == None or llava_processor == None:
        #model_name = "llava-hf/llava-1.5-7b-hf"
        model_name = "Salesforce/blip2-opt-2.7b"
        llava_model = LlavaForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch.float16)
        llava_processor = AutoProcessor.from_pretrained(model_name)

    image = Image.open(image_path).convert("RGB")
    conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},  # Pass the image object directly
                    {"type": "text", "text": '''
                     Describe this image in detail. If it contains graphs, charts, or illustrations related to diabetes, explain what they show regarding diabetes management, treatment, or monitoring.
                     '''}
                    ],
                },
            ]
    inputs = llava_processor.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            ).to(llava_model.device, torch.float16)
    with torch.no_grad():
        generate_ids = llava_model.generate(**inputs, max_new_tokens=200)

    return llava_processor.batch_decode(generate_ids, skip_special_tokens=True)[0]

