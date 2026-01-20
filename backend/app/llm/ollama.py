"""
Ollama LLM provider with streaming support.
Wraps Ollama API for local model inference.
"""

from typing import AsyncIterator, List, Optional

from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage

from app.config import get_settings
from app.utils import logger


class OllamaProvider:
    """Ollama LLM provider with streaming support for local models."""
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize Ollama provider.
        
        Args:
            model: Model name (defaults to config)
        """
        settings = get_settings()
        self.model = model or settings.default_ollama_model
        self.base_url = settings.ollama_base_url
        
        self._llm = ChatOllama(
            model=self.model,
            base_url=self.base_url,
            temperature=0.7
        )
        
        logger.info(f"Initialized Ollama provider with model: {self.model}")
    
    def _build_messages(
        self,
        query: str,
        context: str,
        conversation_history: List[dict],
        system_prompt: Optional[str] = None
    ) -> List[BaseMessage]:
        """
        Build message list for chat completion.
        
        Args:
            query: User query
            context: Retrieved document context
            conversation_history: Previous conversation turns
            system_prompt: Custom system prompt
            
        Returns:
            List of LangChain message objects
        """
        messages = []
        
        # System message with RAG instructions
        default_system = """You are a helpful AI assistant that answers questions based ONLY on the provided context.

IMPORTANT RULES:
1. Answer ONLY based on the provided context
2. If the context does not contain relevant information, respond with: "I do not have knowledge of this based on the uploaded documents."
3. Be precise and cite information from the context
4. Do not make up or hallucinate information
5. If asked a follow-up question, use the conversation history to understand the context

You must provide accurate, well-structured answers based solely on the retrieved documents."""
        
        system_content = system_prompt or default_system
        
        if context:
            system_content += f"\n\n--- RETRIEVED CONTEXT ---\n{context}\n--- END CONTEXT ---"
        
        messages.append(SystemMessage(content=system_content))
        
        # Add conversation history
        for turn in conversation_history:
            if turn.get("role") == "user":
                messages.append(HumanMessage(content=turn["content"]))
            elif turn.get("role") == "assistant":
                messages.append(AIMessage(content=turn["content"]))
        
        # Add current query
        messages.append(HumanMessage(content=query))
        
        return messages
    
    async def generate_stream(
        self,
        query: str,
        context: str,
        conversation_history: List[dict],
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Generate streaming response.
        
        Args:
            query: User query
            context: Retrieved document context
            conversation_history: Previous conversation turns
            system_prompt: Custom system prompt
            
        Yields:
            Token strings as they are generated
        """
        messages = self._build_messages(query, context, conversation_history, system_prompt)
        
        logger.info(f"Generating streaming response for query: {query[:50]}...")
        
        async for chunk in self._llm.astream(messages):
            if chunk.content:
                yield chunk.content
    
    async def generate(
        self,
        query: str,
        context: str,
        conversation_history: List[dict],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate non-streaming response.
        
        Args:
            query: User query
            context: Retrieved document context
            conversation_history: Previous conversation turns
            system_prompt: Custom system prompt
            
        Returns:
            Complete response string
        """
        messages = self._build_messages(query, context, conversation_history, system_prompt)
        response = await self._llm.ainvoke(messages)
        return response.content
