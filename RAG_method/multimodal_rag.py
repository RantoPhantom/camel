import os
import uuid
import json
import pickle
from typing import List
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel
from unstructured.partition.pdf import partition_pdf

from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from models import init_embeddings, init_chat_model, get_text_summary_chain, process_image_with_llava

class Element(BaseModel):
    type: str
    text: Any
    
class DiabetesKnowledgeBase:
    def __init__(self, data_dir: str):
    
        # Initialize the knowledge base with the path to PDF files
        self.data_dir = data_dir
        self.image_dir = "./figures/"
        Path(self.image_dir).mkdir(parents=True, exist_ok=True)

        # Create a directory to store processed data
        self.processed_dir = os.path.join(data_dir, "processed")
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
        template =  """You are a medical assistant specialized in diabetes. 
            Answer the question based only on the following context, which includes text, tables, and image descriptions:
            
            CONTEXT:
            {context}
            
            Question: {question}
            
           INSTRUCTIONS:
            1. Provide a factual answer using ONLY the information in the context above
            2. If the context doesn't contain the information needed, state "I don't have enough information" - DO NOT make up an answer
            3. Cite the specific part of the context that supports your answer
            4. Structure your answer with clear paragraphs and bullet points when appropriate
            5. Be concise yet thorough

            ANSWER:
            """
                            
        self.prompt = ChatPromptTemplate.from_template(template)
        
        self.chain = (
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


    # Process a PDF file, extract text, tables, and images  
    def process_pdf(self, pdf_path: str) -> None:
        # Check if the file has already been processed and hasn't changed
        filename = os.path.basename(pdf_path)
        file_mtime = str(os.path.getmtime(pdf_path))

        if filename in self.processed_files and self.processed_files[filename] == file_mtime:
            print(f"Skipping {filename} - already processed!")
            return 

        print(f"Processing {pdf_path}...")
        
        # Get elements from the PDF
        raw_pdf_elements = partition_pdf(
            filename=pdf_path,
            extract_images_in_pdf=True,
            infer_table_structure=True,
            chunking_strategy="by_title",
            max_characters=4000,
            new_after_n_chars=3800,
            combine_text_under_n_chars=2000,
            image_output_dir_path=self.image_dir,
        )
        
        # Categorize elements
        categorized_elements = []
        for element in raw_pdf_elements:
            if "unstructured.documents.elements.Table" in str(type(element)):
                categorized_elements.append(Element(type="table", text=str(element)))
            elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
                categorized_elements.append(Element(type="text", text=str(element)))
                
        # Process text elements
        text_elements = [e for e in categorized_elements if e.type == "text" and e.text != ""]
        texts = [i.text for i in text_elements]
        print(f"Summarizing {len(texts)} text chunks...")
        text_summaries = self.summary_chain.batch(texts, {"max_concurrent": 1})

        # Save the interim results to prevent data loss in case of interruption
        interim_results_dir = os.path.join(self.processed_dir, f"{filename}_interim")
        Path(interim_results_dir).mkdir(parents=True, exist_ok=True)

        with open(os.path.join(interim_results_dir, "text_summaries.pkl"), 'wb') as f:
            pickle.dump(text_summaries, f)
        
        # Process table elements
        table_elements = [e for e in categorized_elements if e.type == "table"]
        tables = [i.text for i in table_elements]
        print(f"Summarizing {len(tables)} tables...")
        table_summaries = self.summary_chain.batch(tables, {"max_concurrent": 5})

        with open(os.path.join(interim_results_dir, "table_summaries.pkl"), 'wb') as f:
            pickle.dump(table_summaries, f)
        
        # Create a file to track processed images
        processed_images_path = os.path.join(self.processed_dir, "processed_images.json")
        if os.path.exists(processed_images_path):
            with open(processed_images_path, 'r') as f:
                processed_images = json.load(f)
        else:
            processed_images = {}

        # Process image elements
        print("Processing extracted images ...")
        
        # Find images recently extracted from this PDF (within the last 5 minutes of PDF modification time)
        recent_images = [f for f in os.listdir(self.image_dir) 
                        if f.lower().endswith((".png", ".jpg", ".jpeg")) and
                        os.path.getmtime(os.path.join(self.image_dir, f)) > os.path.getmtime(pdf_path) - 300]
        
        # Filter out already processed images
        new_images = [img for img in recent_images if img not in processed_images]
        
        # Print debugging information
        print(f"Found {len(recent_images)} recently extracted images")
        print(f"Processing {len(new_images)} new images")

        # Load existing image descriptions if available
        image_descriptions_path = os.path.join(self.processed_dir, "image_descriptions.json")
        if os.path.exists(image_descriptions_path):
            with open(image_descriptions_path, 'r') as f:
                image_descriptions = json.load(f)
        else:
            image_descriptions = {}

        # Process only new images
        for i, img_file in enumerate(new_images):
            img_path = os.path.join(self.image_dir, img_file)
            print(f"Processing image {i+1}/{len(new_images)}: {img_file}")
            description = process_image_with_llava(img_path)

            # Print the description to help debug
            print(f"Image description: {description[:100]}..." if len(description) > 100 else description)
            
            # Store the description
            image_descriptions[img_file] = description
            
            # Mark this image as processed
            processed_images[img_file] = {
                "source_pdf": filename,
                "processed_time": datetime.now().isoformat(),
                "size_bytes": os.path.getsize(img_path)
            }
            
            # Save descriptions and processed images record incrementally
            with open(image_descriptions_path, 'w') as f:
                json.dump(image_descriptions, f)
                
            with open(processed_images_path, 'w') as f:
                json.dump(processed_images, f)
            
        # Save interim image descriptions
        with open(os.path.join(interim_results_dir, "image_descriptions.json"), 'w') as f:
            json.dump({img: image_descriptions[img] for img in new_images if img in image_descriptions}, f)
            
        # Add to retriever (only if there are items to add)
        if texts and text_summaries:
            self._add_to_retriever(texts, text_summaries, "text", filename)
            
        if tables and table_summaries:
            self._add_to_retriever(tables, table_summaries, "table", filename)
            
        # Add new image descriptions to retriever
        if new_images:
            new_image_descriptions = [image_descriptions[img] for img in new_images if img in image_descriptions]
            if new_image_descriptions:
                self._add_to_retriever(new_image_descriptions, new_image_descriptions, "image", filename)
                
        # Mark as processed
        self.processed_files[filename] = file_mtime
        self._save_processed_files()
        
        # Persist the vectorstore
        self.vectorstore.persist()
        self._persist_docstore()

        print(f"Finished processing {filename}. Added {len(texts)} text chunks, {len(tables)} tables, and {len(new_images)} new images to knowledge base.")
        
        # Clean up interim files
        if os.path.exists(interim_results_dir):
            try:
                import shutil
                shutil.rmtree(interim_results_dir)
            except PermissionError:
                print(f"Warning: Could not remove interim directory {interim_results_dir}. This won't affect functionality.")

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
        self.vectorstore.add_documents(summary_docs)
        self.store.mset(list(zip(doc_ids, contents)))
        print(f"Added {len(summary_docs)} {content_type} documents from {source_file}")
        
        
    # Process all PDFs in the data directory
    def process_all_pdfs(self):
        pdf_files = [f for f in os.listdir(self.data_dir) if f.lower().endswith('.pdf')]
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.data_dir, pdf_file)
            self.process_pdf(pdf_path)
            
            
    # Answer a  question using the RAG pipeline
    def answer_question(self, question: str) -> str:
        return self.chain.invoke(question)
        
    # Get a report of processed files
    def get_processed_files_status(self) -> str:
        if not self.processed_files:
            return "No files have been processed yet."
        
        report = "Processed files:\n"
        for filename, timestamp in self.processed_files.items():
            dt = datetime.fromtimestamp(float(timestamp))
            report += f"- {filename} (processed on {dt.strftime('%Y-%m-%d %H:%M:%S')})\n"
        
        return report

    # Retrieve the most relevant contexts for a given question with improved filtering and processing
    def get_contexts_for_question(self, question: str, k=10, similarity_threshold=0.5):
        
        # Use the retriever to get relevant documents
        docs = self.retriever.invoke(question, k=k*2)
        
        # Handle empty results
        if not docs:
            print("No relevant documents found for the question.")
            return []
        
        contexts = []
        
        # Extract embedding model from retriever if available
        embedding_model = self.embeddings
        
        # Create embedding for the question
        try:
            question_embedding = embedding_model.embed_query(question)
        except:
            # If embedding fails, proceed without filtering by similarity
            question_embedding = None
            print("Warning: Could not create embedding for question.")
        
        # Process each document
        for doc in docs:
            # Extract the content based on document type
            if hasattr(doc, 'page_content'):
                content = doc.page_content
            elif isinstance(doc, str):
                content = doc
            elif hasattr(doc, 'text'):
                content = doc.text
            elif hasattr(doc, 'content'):
                content = doc.content
            else:
                try:
                    content = str(doc)
                except:
                    print(f"Could not convert document to string: {type(doc)}")
                    continue
            
            # Skip empty content
            if not content or not content.strip():
                continue
            
            # Apply similarity filtering if embedding is available
            if question_embedding is not None:
                try:
                    # Get embedding for the content
                    content_embedding = embedding_model.embed_documents([content])[0]
                    
                    # Calculate similarity 
                    similarity = self._cosine_similarity(question_embedding, content_embedding)
                    
                    # Only keep contexts with similarity above threshold
                    if similarity < similarity_threshold:
                        continue
                    
                    # Add a score to the context for potential ranking
                    doc_metadata = getattr(doc, 'metadata', {}) if hasattr(doc, 'metadata') else {}
                    doc_metadata['similarity_score'] = float(similarity)
                    
                    # Create a formatted context with metadata
                    context_with_metadata = {
                        'content': content,
                        'metadata': doc_metadata,
                        'similarity': float(similarity)
                    }
                    contexts.append(context_with_metadata)
                    
                except Exception as e:
                    print(f"Error calculating similarity: {str(e)}")
                    # Fall back to adding content without similarity filtering
                    contexts.append({'content': content, 'metadata': getattr(doc, 'metadata', {})})
            else:
                # Without embedding, just add the content
                contexts.append({'content': content, 'metadata': getattr(doc, 'metadata', {})})
        
        # Sort contexts by similarity score if available
        if contexts and all('similarity' in ctx for ctx in contexts):
            contexts.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Limit to top k results
        contexts = contexts[:k]
        
        # Extract just the content for compatibility with existing code
        return [ctx['content'] for ctx in contexts]

    # Calculate cosine similarity between two vectors
    def _cosine_similarity(self, vector_a, vector_b):
    
        import numpy as np
        
        # Ensure vectors are numpy arrays
        if not isinstance(vector_a, np.ndarray):
            vector_a = np.array(vector_a)
        if not isinstance(vector_b, np.ndarray):
            vector_b = np.array(vector_b)
        
        # Calculate cosine similarity
        dot_product = np.dot(vector_a, vector_b)
        norm_a = np.linalg.norm(vector_a)
        norm_b = np.linalg.norm(vector_b)
        
        # Handle zero division
        if norm_a == 0 or norm_b == 0:
            return 0
            
        return dot_product / (norm_a * norm_b)
        
