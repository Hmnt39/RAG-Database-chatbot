"""Question-answering chain for RAG-based chatbot."""

from typing import List, Dict, Any, Optional, Tuple
import logging
from openai import OpenAI
from app.core.retriever import RAGRetriever

logger = logging.getLogger(__name__)


class QAChain:
    """Question-answering chain combining retrieval and generation."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        retriever: Optional[RAGRetriever] = None,
    ):
        """
        Initialize QA chain.

        Args:
            api_key: OpenAI API key
            model: Model name to use
            retriever: RAGRetriever instance
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.retriever = retriever

    def generate_answer(
        self,
        question: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate answer using LLM with context.

        Args:
            question: User question
            context: Retrieved context documents
            conversation_history: Previous conversation messages
            system_prompt: Custom system prompt

        Returns:
            Generated answer
        """
        try:
            messages = self._build_messages(
                question, context, conversation_history, system_prompt
            )

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=1000
            )

            answer = response.choices[0].message.content
            logger.info(f"Generated answer for question: {question}")
            return answer
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise

    def answer_question(
        self,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 5,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Answer question using RAG pipeline.

        Args:
            question: User question
            conversation_history: Previous messages
            top_k: Number of documents to retrieve

        Returns:
            Tuple of (answer, retrieved_documents)
        """
        try:
            # Retrieve relevant documents
            retrieved_docs = []
            context = ""

            if self.retriever:
                retrieved_docs = self.retriever.retrieve_documents(question, top_k=top_k)
                context = self.retriever.build_context(retrieved_docs)

            # Generate answer
            answer = self.generate_answer(question, context, conversation_history)

            return answer, retrieved_docs
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            raise

    def _build_messages(
        self,
        question: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]],
        system_prompt: Optional[str],
    ) -> List[Dict[str, str]]:
        """
        Build message list for LLM.

        Args:
            question: User question
            context: Retrieved context
            conversation_history: Previous messages
            system_prompt: Custom system prompt

        Returns:
            List of message dictionaries
        """
        messages = []

        # Add system prompt
        if not system_prompt:
            system_prompt = (
                "You are a helpful assistant. Use the provided context to answer questions "
                "accurately. If the context doesn't contain relevant information, say so."
            )

        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-4:])  # Keep last 4 messages for context

        # Add context and question
        user_message = f"Context:\n{context}\n\nQuestion: {question}"
        messages.append({"role": "user", "content": user_message})

        return messages
