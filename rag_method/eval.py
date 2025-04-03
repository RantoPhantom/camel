import json
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from rouge import Rouge
from multimodal_rag import DiabetesKnowledgeBase

class RAGEvaluator:
    def __init__(self, knowledge_base: DiabetesKnowledgeBase, eval_dataset_path: str):
        self.kb = knowledge_base
        self.eval_dataset = self._load_evaluation_dataset(eval_dataset_path)
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.rouge = Rouge()
        
    def _load_evaluation_dataset(self, path: str) -> List[Dict[str, Any]]:
        with open(path, 'r') as f:
            return json.load(f)
            
    def evaluate_all(self) -> Dict[str, Any]:
        results = {
            "overall": {},
            "per_question": []
        }
        
        # Using fixed k=5
        k = 5
        
        # Lists to collect metrics across all questions
        recall_at_k = []
        precision_at_k = []
        faithfulness_scores = []
        answer_accuracy_scores = []
        context_relevance_scores = []
        
        # Evaluate each question
        for i, question_data in enumerate(self.eval_dataset):
            print(f"Evaluating question {i+1}/{len(self.eval_dataset)}: {question_data['question'][:80]}...")
            
            # Get results for this question
            question_results = self.evaluate_question(
                question_data["question"], 
                question_data["ground_truth"],
                question_data["expected_contexts"],
                k
            )
            
            # Add to per-question results
            results["per_question"].append({
                "question": question_data["question"],
                "metrics": question_results
            })
            
            # Collect metrics for overall calculations
            recall_at_k.append(question_results[f"recall@{k}"])
            precision_at_k.append(question_results[f"precision@{k}"])
            faithfulness_scores.append(question_results["faithfulness"])
            answer_accuracy_scores.append(question_results["answer_accuracy"])
            context_relevance_scores.append(question_results["context_relevance"])
        
        # Add hallucination comparison
        print("\nStarting hallucination comparison...")
        hallucination_results = self.compare_hallucination_rates()

        # Calculate overall metrics
        results["overall"][f"avg_recall@K"] = np.mean(recall_at_k)
        results["overall"][f"avg_precision@K"] = np.mean(precision_at_k)
        results["overall"]["avg_faithfulness"] = np.mean(faithfulness_scores)
        results["overall"]["avg_answer_accuracy"] = np.mean(answer_accuracy_scores)
        results["overall"]["avg_context_relevance"] = np.mean(context_relevance_scores)
        results["hallucination_comparison"] = hallucination_results
        results["overall"]["hallucination_reduction"] = hallucination_results["avg_hallucination_improvement_pct"]
        results["overall"]["factual_consistency_improvement"] = hallucination_results["avg_factual_consistency_improvement_pct"]
        
        return results

    # Evaluate a single question using multiple RAG metrics.
    def evaluate_question(self, question: str, ground_truth: str, expected_contexts: List[str], k: int) -> Dict[str, float]:
        # Get RAG system response
        generated_answer = self.kb.answer_question(question)
        
        # Get retrieved contexts
        all_contexts = self.kb.get_contexts_for_question(question, k=k)
        
        # Calculate metrics
        metrics = {}
        
        # Calculate Recall and Precision for k=5
        recall, precision = self.calculate_context_metrics(all_contexts, expected_contexts)
        metrics[f"recall@{k}"] = recall
        metrics[f"precision@{k}"] = precision
        
        # Calculate answer accuracy (semantic similarity to ground truth)
        metrics["answer_accuracy"] = self.calculate_answer_accuracy(generated_answer, ground_truth)
        
        # Calculate faithfulness (how well the answer is grounded in retrieved contexts)
        metrics["faithfulness"] = self.calculate_faithfulness(generated_answer, all_contexts)
        
        # Calculate overall context relevance
        metrics["context_relevance"] = self.calculate_context_relevance(all_contexts, question)
        
        # Store the generated answer for reference
        metrics["generated_answer"] = generated_answer
        
        return metrics
        
    # Calculate Recall and Precision of retrieved contexts compared to expected contexts
    def calculate_context_metrics(self, retrieved_contexts: List[str], expected_contexts: List[str]) -> Tuple[float, float]:
    
        # Convert all strings to lowercase for case-insensitive matching
        retrieved_lower = ' '.join(retrieved_contexts).lower()
        
        # Count how many expected contexts are found in the retrieved contexts
        found_contexts = 0
        for context in expected_contexts:
            if context.lower() in retrieved_lower:
                found_contexts += 1
        
        # Calculate recall: what fraction of expected contexts were found
        recall = found_contexts / len(expected_contexts) if expected_contexts else 0
        
        # Calculate precision: what fraction of expected contexts were found relative to total possible
        precision = found_contexts / min(len(expected_contexts), len(retrieved_contexts)) if retrieved_contexts else 0
        
        return recall, precision
    
    # Calculate the semantic similarity between the generated answer and ground truth
    def calculate_answer_accuracy(self, generated_answer: str, ground_truth: str) -> float:

        # Use semantic similarity with sentence embeddings
        try:
            # Get embeddings
            generated_embedding = self.model.encode([generated_answer])[0]
            truth_embedding = self.model.encode([ground_truth])[0]
            
            # Calculate cosine similarity
            similarity = cosine_similarity([generated_embedding], [truth_embedding])[0][0]
            
            # Also use ROUGE scores for lexical comparison
            rouge_scores = self.rouge.get_scores(generated_answer, ground_truth)[0]
            rouge_l_f = rouge_scores['rouge-l']['f']
            
            # Combine semantic and lexical metrics (with more weight on semantic)
            combined_score = 0.7 * similarity + 0.3 * rouge_l_f
            
            return float(combined_score)
        except Exception as e:
            print(f"Error calculating answer accuracy: {str(e)}")
            return 0.0
    
    # Calculate faithfulness - how well the answer is grounded in the contexts.
    def calculate_faithfulness(self, generated_answer: str, retrieved_contexts: List[str]) -> float:

        # Join all contexts into a single text
        all_contexts_text = ' '.join(retrieved_contexts)
        
        # Get embeddings
        try:
            # Split the answer into sentences for more granular analysis
            import re
            answer_sentences = re.split(r'(?<=[.!?])\s+', generated_answer)
            answer_sentences = [s for s in answer_sentences if len(s.strip()) > 10]  # Filter out very short sentences
            
            # For each sentence in the answer, check if it's supported by the contexts
            support_scores = []
            
            for sentence in answer_sentences:
                # Skip very short sentences or common phrases that might not need support
                if len(sentence.split()) < 3 or sentence.lower().startswith(("i don't", "i do not")):
                    continue
                    
                # Get embedding for this sentence
                sentence_embedding = self.model.encode([sentence])[0]
                
                # Split contexts into chunks for more precise similarity
                context_chunks = []
                for context in retrieved_contexts:
                    # Simple chunking by sentences
                    chunks = re.split(r'(?<=[.!?])\s+', context)
                    context_chunks.extend([c for c in chunks if len(c.strip()) > 10])
                
                # Calculate similarity with each context chunk
                max_similarity = 0
                if context_chunks:
                    context_embeddings = self.model.encode(context_chunks)
                    similarities = cosine_similarity([sentence_embedding], context_embeddings)[0]
                    max_similarity = max(similarities)
                
                support_scores.append(max_similarity)
            
            # Overall faithfulness is the average support score across all sentences
            if support_scores:
                return float(np.mean(support_scores))
            else:
                return 0.5  # Default if no evaluable sentences
        except Exception as e:
            print(f"Error calculating faithfulness: {str(e)}")
            return 0.5
    
    # Calculate how relevant the retrieved contexts are to the question
    def calculate_context_relevance(self, retrieved_contexts: List[str], question: str) -> float:
    
        try:
            # Get question embedding
            question_embedding = self.model.encode([question])[0]
            
            # Calculate similarity for each context
            relevance_scores = []
            for context in retrieved_contexts:
                if not context or len(context.strip()) < 10:
                    continue
                    
                context_embedding = self.model.encode([context])[0]
                similarity = cosine_similarity([question_embedding], [context_embedding])[0][0]
                relevance_scores.append(similarity)
            
            # Overall relevance is the average across all contexts
            if relevance_scores:
                return float(np.mean(relevance_scores))
            else:
                return 0.0
        except Exception as e:
            print(f"Error calculating context relevance: {str(e)}")
            return 0.0
        
    # Get an answer directly from the base LLM without RAG
    def get_base_model_answer(self, question):
        
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        # Create a simple prompt for the base model
        template = """You are a question and answering chatbot. Answer the question below:
        
        Question: {question}
        
        Give a detailed and factual answer based on your knowledge.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Use the same chat model as the one used in RAG system
        chain = prompt | self.kb.chat_model | StrOutputParser()
        
        # Get the answer from base model
        try:
            return chain.invoke({"question": question})
        except Exception as e:
            print(f"Error getting base model answer: {str(e)}")
            return "Error generating answer"


    # Helper method to calculate hallucination score for an answer against context
    def _calculate_hallucination_score(self, answer, context):
  
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Split answer into sentences
        import re
        answer_sentences = re.split(r'(?<=[.!?])\s+', answer)
        answer_sentences = [s for s in answer_sentences if len(s.strip()) > 0]
        
        # Check each sentence for support in contexts
        total_sentences = len(answer_sentences)
        unsupported_sentences = 0
        
        for sentence in answer_sentences:
            # Skip very short sentences
            if len(sentence.split()) < 3:
                total_sentences -= 1
                continue
            
            # Check if sentence is supported by context
            try:
                sentence_embedding = self.model.encode([sentence])
                context_embedding = self.model.encode([context])
                similarity = cosine_similarity(sentence_embedding, context_embedding)[0][0]
                
                # If similarity is below threshold, consider it unsupported
                if similarity < 0.5:  # Threshold can be adjusted (can maybe try 0.25)
                    unsupported_sentences += 1
            except Exception as e:
                print(f"Error calculating similarity: {str(e)}")
                # Assume unsupported if calculation fails
                unsupported_sentences += 1
        
        # Calculate hallucination score (percentage of unsupported sentences)
        return unsupported_sentences / total_sentences if total_sentences > 0 else 0

    # Compare hallucination rates between base model and RAG model
    def compare_hallucination_rates(self) -> Dict[str, Any]:
 
        print("\nComparing hallucination rates between base model and RAG...")
        
        results = []
        
        for i, question_data in enumerate(self.eval_dataset):
            question = question_data["question"]
            ground_truth = question_data["ground_truth"]
            
            print(f"Processing question {i+1}/{len(self.eval_dataset)}")
            
            # Get answers from both models
            rag_answer = self.kb.answer_question(question)
            base_answer = self.get_base_model_answer(question)
            
            # Get retrieved contexts for evaluation
            retrieved_contexts = self.kb.get_contexts_for_question(question)
            combined_context = ' '.join(retrieved_contexts)
            
            # Evaluate RAG model hallucination
            rag_hallucination_score = self._calculate_hallucination_score(rag_answer, combined_context)
            
            # Evaluate Base model hallucination (against the same contexts for fair comparison)
            base_hallucination_score = self._calculate_hallucination_score(base_answer, combined_context)
            
            # Calculate factual consistency with ground truth for both models
            ground_truth_embedding = self.model.encode([ground_truth])
            rag_answer_embedding = self.model.encode([rag_answer])
            base_answer_embedding = self.model.encode([base_answer])
            
            rag_factual_consistency = cosine_similarity(ground_truth_embedding, rag_answer_embedding)[0][0]
            base_factual_consistency = cosine_similarity(ground_truth_embedding, base_answer_embedding)[0][0]
            
            # Calculate improvement percentage
            if base_hallucination_score > 0:
                hallucination_improvement = ((base_hallucination_score - rag_hallucination_score) / base_hallucination_score) * 100
            else:
                hallucination_improvement = 0 if rag_hallucination_score == 0 else -100
                
            if base_factual_consistency > 0:

                factual_improvement = ((rag_factual_consistency - base_factual_consistency) / base_factual_consistency) * 100
            else:
                factual_improvement = 100 if rag_factual_consistency > 0 else 0
            
            results.append({
                "question": question,
                "rag_hallucination_score": rag_hallucination_score,
                "base_hallucination_score": base_hallucination_score,
                "hallucination_improvement_pct": hallucination_improvement,
                "rag_factual_consistency": rag_factual_consistency,
                "base_factual_consistency": base_factual_consistency,
                "factual_consistency_improvement_pct": factual_improvement,
                "rag_answer": rag_answer,
                "base_answer": base_answer
            })
        
          # Convert NumPy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif hasattr(obj, 'item'):
                return obj.item()
            else:
                return obj

        # Calculate average metrics
        avg_rag_hallucination = sum(r["rag_hallucination_score"] for r in results) / len(results)
        avg_base_hallucination = sum(r["base_hallucination_score"] for r in results) / len(results)
        avg_hallucination_improvement = sum(r["hallucination_improvement_pct"] for r in results) / len(results)
        
        avg_rag_factual = sum(r["rag_factual_consistency"] for r in results) / len(results)
        avg_base_factual = sum(r["base_factual_consistency"] for r in results) / len(results)
        avg_factual_improvement = sum(r["factual_consistency_improvement_pct"] for r in results) / len(results)
        
        return {
            "detailed_results": results,
            "avg_rag_hallucination": avg_rag_hallucination,
            "avg_base_hallucination": avg_base_hallucination,
            "avg_hallucination_improvement_pct": avg_hallucination_improvement,
            "avg_rag_factual_consistency": avg_rag_factual,
            "avg_base_factual_consistency": avg_base_factual,
            "avg_factual_consistency_improvement_pct": avg_factual_improvement
        }
    

    #  Generate and save a detailed evaluation report    
    def generate_report(self, results: Dict[str, Any], output_path: str = "rag_evaluation_report.json") -> None:
       
        # Add timestamp to the report
        from datetime import datetime
        results["timestamp"] = datetime.now().isoformat()
        
        # Calculate additional statistics
        # Find highest and lowest scoring questions for each metric
        metrics_of_interest = ["answer_accuracy", "faithfulness", "context_relevance"] 
        best_worst = {}
        
        for metric in metrics_of_interest:
            scores = [(q["question"], q["metrics"][metric]) for q in results["per_question"]]
            scores.sort(key=lambda x: x[1])
            
            best_worst[f"lowest_{metric}"] = {
                "question": scores[0][0],
                "score": scores[0][1]
            }
            
            best_worst[f"highest_{metric}"] = {
                "question": scores[-1][0],
                "score": scores[-1][1]
            }
            
        results["analysis"] = best_worst

        # Add hallucination analysis if available
        if "hallucination_comparison" in results:
            hallucination_data = results["hallucination_comparison"]
            
            # Find questions with best and worst hallucination reduction
            detailed_results = hallucination_data["detailed_results"]
            detailed_results.sort(key=lambda x: x["hallucination_improvement_pct"])
            
            best_worst_hallucination = {
                "lowest_hallucination_improvement": {
                    "question": detailed_results[0]["question"],
                    "improvement": detailed_results[0]["hallucination_improvement_pct"]
                },
                "highest_hallucination_improvement": {
                    "question": detailed_results[-1]["question"],
                    "improvement": detailed_results[-1]["hallucination_improvement_pct"]
                }
            }
            
            if "analysis" not in results:
                results["analysis"] = {}
                
            results["analysis"].update(best_worst_hallucination)

        # Convert NumPy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif hasattr(obj, 'item'):
                return obj.item()
            else:
                return obj

        # Convert all NumPy types in the results
        serializable_results = convert_numpy_types(results)

        # Save the report as JSON
        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
            
        print(f"Evaluation report saved to {output_path}")
        
        # Print evaluation summary
        print("\n===== RAG EVALUATION SUMMARY =====")
        for metric, value in results["overall"].items():
            if isinstance(value, (int, float)):
                print(f"{metric}: {value:.4f}")

        # Print summary of hallucination metrics
        if "hallucination_comparison" in results:
            h_data = results["hallucination_comparison"]
            print("\n===== HALLUCINATION COMPARISON =====")
            print(f"Average RAG Hallucination Score: {h_data['avg_rag_hallucination']:.4f}")
            print(f"Average Base Model Hallucination Score: {h_data['avg_base_hallucination']:.4f}")
            print(f"Hallucination Reduction: {h_data['avg_hallucination_improvement_pct']:.2f}%")
            print(f"Factual Consistency Improvement: {h_data['avg_factual_consistency_improvement_pct']:.2f}%")

    # Run the full evaluation process with fixed k=5
    def run_evaluation(data_dir: str, eval_dataset_path: str):
        
        # Initialize the knowledge base
        kb = DiabetesKnowledgeBase(data_dir)
        
        # Make sure all PDFs are processed
        kb.process_all_pdfs()
        
        # Initialize the evaluator
        evaluator = RAGEvaluator(kb, eval_dataset_path)
        
        # Run the evaluation
        results = evaluator.evaluate_all()
        
        # Generate the report
        evaluator.generate_report(results)
        
        return results
    

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate a RAG system for diabetes knowledge")
    parser.add_argument("--data-dir", type=str, required=True, help="Directory containing knowledge base PDFs")
    parser.add_argument("--eval-dataset", type=str, required=True, help="Path to evaluation dataset JSON")
    parser.add_argument("--output", type=str, default="rag_evaluation_report.json", help="Output path for evaluation report")
    
    args = parser.parse_args()
    
    kb = DiabetesKnowledgeBase(args.data_dir)
    
    evaluator = RAGEvaluator(kb, args.eval_dataset)
    results = evaluator.evaluate_all() 
    evaluator.generate_report(results, args.output)