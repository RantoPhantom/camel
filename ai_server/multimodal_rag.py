import os
import uuid
import json
import pickle
import pymupdf
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel
from pdf_extraction import extract_text
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from models import init_embeddings, init_chat_model, get_text_summary_chain

class Element(BaseModel):
    type: str
    text: Any
    
class DiabetesKnowledgeBase:
    def __init__(self):
    
        # Initialize the knowledge base with the path to PDF files
        self.data_dir = "./data/raw-pdfs/"
        self.image_dir = "./data/extracted_images/"
        Path(self.image_dir).mkdir(parents=True, exist_ok=True)

        # Create a directory to store processed data
        self.processed_dir = os.path.join(self.data_dir, "processed")
        Path(self.processed_dir).mkdir(parents=True, exist_ok=True)

        # Create a file to track processed PDFs and their timestamps
        self.processed_log_path = os.path.join(self.processed_dir, "processed_files.json")
        self.processed_files = self._load_processed_files()

        # Create a path for the persisted vector store
        self.vectorstore_path = os.path.join(self.processed_dir, "chroma_db")
        self.docstore_path = os.path.join(self.processed_dir, "docstore.pkl")

        # Initialize components
        self.embeddings = init_embeddings()
        self.chat_model = init_chat_model()
        self.summary_chain = get_text_summary_chain()
        
        # Initialze the retriever system
        self.vectorstore = Chroma(
            collection_name="diabetes_kb",
            embedding_function=self.embeddings,
            persist_directory=self.vectorstore_path
        )

        # Load docstore if it exists, otherwise create new one
        if os.path.exists(self.docstore_path):
            with open(self.docstore_path, 'rb') as f:
                self.store = pickle.load(f)
            
            # Get document count using the yield_keys method
            try:
                doc_count = sum(1 for _ in self.store.yield_keys())
                print(f"Loaded existing docstore with {doc_count} documents.")
            except Exception as e:
                print(f"Loaded existing docstore. Unable to count documents: {str(e)}")
        else:
            self.store = InMemoryStore()
            print("Created new docstore!")
        
       
        self.id_key = "doc_id"
        
        self.retriever = MultiVectorRetriever(
            vectorstore=self.vectorstore,
            docstore=self.store,
            id_key=self.id_key
        )
        
        # Initialize RAG chain
        template = """<|system|> You are a medical assistant specialized in diabetes. Answer only using the provided context.

        <context>
        {context}
        </context>

        <|user|>
        {question} 

        <|assistant|>
        """ 
        self.prompt = ChatPromptTemplate.from_template(template)
        
        self.init_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()} | self.prompt | self.chat_model | StrOutputParser()
        )

    # Load the log of processed files
    def _load_processed_files(self) -> Dict[str, str]:
        if os.path.exists(self.processed_log_path):
            with open(self.processed_log_path, 'r') as f:
                return json.load(f)
            
        return {}
    
    # Save the log of processed files
    def _save_processed_files(self):
        with open(self.processed_log_path, 'w') as f:
            json.dump(self.processed_files, f)

    # Save the docstore to disk
    def _persist_docstore(self):

        with open(self.docstore_path, 'wb') as f:
            pickle.dump(self.store, f)
        
        # Get document count using the yield_keys method
        try:
            doc_count = sum(1 for _ in self.store.yield_keys())
            print(f"Persisted docstore with {doc_count} documents.")
        except Exception as e:
            print(f"Persisted docstore. Unable to count documents: {str(e)}")

    # Process a PDF file, extract text
    def process_pdf(self, pdf_path: str) -> None:

        # Check if the file has already been processed and hasn't changed
        filename = os.path.basename(pdf_path)
        file_mtime = str(os.path.getmtime(pdf_path))

        if filename in self.processed_files and self.processed_files[filename] == file_mtime:
            print(f"Skipping {filename} - already processed!")
            return 

        print(f"Processing {pdf_path}...")
        doc = pymupdf.open(self.data_dir + filename)
        text_chunks = extract_text(doc, max_length=2000)
        
        # Process text elements
        print(f"Summarizing {len(text_chunks)} text chunks...")
        text_summaries = self.summary_chain.batch(text_chunks, {"max_concurrent": 12})

        # Save the interim results to prevent data loss in case of interruption
        interim_results_dir = os.path.join(self.processed_dir, f"{filename}_interim")
        Path(interim_results_dir).mkdir(parents=True, exist_ok=True)

        with open(os.path.join(interim_results_dir, "text_summaries.pkl"), 'wb') as f:
            pickle.dump(text_summaries, f)
        
        # Add to retriever (only if there are items to add)
        if text_chunks and text_summaries:
            self._add_to_retriever(text_chunks, text_summaries, "text", filename)

        # Mark as processed
        self.processed_files[filename] = file_mtime
        self._save_processed_files()
        
        # Persist the vectorstore
        self._persist_docstore()

        # Clean up interim files
        if os.path.exists(interim_results_dir):
            import shutil
            shutil.rmtree(interim_results_dir)

    # Add contents and their summaries to the retriever
    def _add_to_retriever(self, contents, summaries, content_type, source_file):
        # Skip if there's nothing to add
        if not contents or not summaries:
            print(f"No {content_type} content to add for {source_file} - skipping")
            return
        
        doc_ids = [str(uuid.uuid4()) for _ in contents]
        summary_docs = [
            Document(
                page_content=s, 
                metadata={
                    self.id_key: doc_ids[i], 
                    "type": content_type,
                    "source": source_file,
                    "date_added": datetime.now().isoformat()
                }
            )
            for i, s in enumerate(summaries)
        ]
        self.vectorstore.add_documents(summary_docs, embeddings=self.embeddings)
        self.store.mset(list(zip(doc_ids, contents)))
        print(f"Added {len(summary_docs)} {content_type} documents from {source_file}")
        
    # Process all PDFs in the data directory
    def process_all_pdfs(self):
        pdf_files = [f for f in os.listdir(self.data_dir) if f.lower().endswith('.pdf')]
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.data_dir, pdf_file)
            self.process_pdf(pdf_path)
            
    # Answer a question using the RAG pipeline
    def answer_question(self, question: str) -> str:
        response = self.init_chain.invoke(question)
            # Extract the answer part
        answer_start = response.find("<|assistant|>")
        if answer_start != -1:
            return response[answer_start + len("<|assistant|>"):].strip()
        
        return response.strip()  # If "Answer:" isn't found, return full response
