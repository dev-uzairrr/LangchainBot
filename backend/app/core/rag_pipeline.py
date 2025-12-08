"""
RAG (Retrieval-Augmented Generation) pipeline.
"""
import logging
from typing import Dict

from app.core.config import settings
from app.core.vectorstore import vector_store
from app.core.llm_groq import groq_llm

logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG pipeline for query answering."""
    
    def __init__(self):
        """Initialize RAG pipeline."""
        self.system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from uploaded documents.

Your task is to:
1. Answer questions accurately using ONLY the information from the provided context
2. If the context doesn't contain enough information to answer the question, clearly state that the information is not available in the documents
3. Provide clear, concise, and well-structured answers
4. When possible, cite specific details from the context to support your answer
5. If asked about something not in the context, politely explain that you can only answer based on the uploaded documents

Important guidelines:
- Base your answer strictly on the context provided
- Do not use external knowledge beyond what's in the context
- If the question is unclear or ambiguous, ask for clarification or provide the most relevant answer based on the context
- Structure your answer logically and make it easy to understand
- Be honest when information is not available in the context

Be helpful, accurate, and honest. If you don't know something based on the context, admit it clearly."""
    
    async def rag_query(self, query: str, lang: str = "en") -> Dict:
        """
        Process a RAG query.
        
        Args:
            query: User query
            lang: Language code (for future multilingual support)
            
        Returns:
            Dictionary with answer, sources, and confidence
        """
        try:
            # Step 1: Retrieve relevant documents
            logger.info(f"Searching for query: {query[:100]}...")
            search_results = vector_store.search(
                query=query,
                top_k=settings.RAG_TOP_K,
                min_score=settings.RAG_MIN_SCORE,
            )
            
            logger.info(f"Retrieved {len(search_results)} search results")
            
            if not search_results:
                logger.warning(f"No search results found for query: {query}")
                return {
                    "answer": "I couldn't find relevant information in the uploaded documents to answer your question. Please try rephrasing your question or ensure the relevant documents have been uploaded.",
                    "sources": [],
                    "confidence": 0.0,
                }
            
            # Step 2: Build context from retrieved documents
            context_parts = []
            sources = []
            
            for result in search_results:
                context_parts.append(result["text"])
                doc_id = result["metadata"].get("doc_id", result["id"])
                if doc_id not in sources:
                    sources.append(doc_id)
            
            context = "\n\n".join(context_parts)
            
            # Step 3: Build prompt with context
            prompt = f"""Based on the following context from uploaded documents, please answer the question.

Context from documents:
{context}

Question: {query}

Instructions:
- Answer the question using ONLY the information from the context above
- If the context contains relevant information, provide a clear and detailed answer
- If the context doesn't contain enough information to answer the question, clearly state: "I couldn't find enough information in the uploaded documents to answer this question."
- Be specific and cite relevant details from the context when possible
- Structure your answer in a clear and easy-to-understand format"""
            
            # Step 4: Generate answer using LLM
            try:
                answer = await groq_llm.chat_completion_async(
                    prompt=prompt,
                    system_prompt=self.system_prompt,
                )
            except ValueError as e:
                # Handle API key or authentication errors
                logger.error(f"LLM authentication/configuration error: {str(e)}", exc_info=True)
                return {
                    "answer": "I'm unable to process your query due to a configuration issue. Please check the API settings.",
                    "sources": sources,
                    "confidence": 0.0,
                }
            except RuntimeError as e:
                # Handle API errors
                logger.error(f"LLM API error: {str(e)}", exc_info=True)
                return {
                    "answer": "I'm experiencing issues connecting to the language model service. Please try again later.",
                    "sources": sources,
                    "confidence": 0.0,
                }
            
            # Step 5: Calculate confidence (based on number of sources and scores)
            avg_score = sum(r["score"] for r in search_results) / len(search_results)
            confidence = min(avg_score, 0.95)  # Cap at 0.95
            
            logger.info(f"RAG query processed. Sources: {len(sources)}, Confidence: {confidence:.2f}")
            
            return {
                "answer": answer.strip(),
                "sources": sources,
                "confidence": round(confidence, 2),
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}", exc_info=True)
            raise


# Global instance
rag_pipeline = RAGPipeline()

