"""
Conversation memory management.
Provides session-based memory for multi-turn conversations.
"""

from threading import Lock
from typing import Dict, List


class ConversationMemoryManager:
    """Manager for session-based conversation memories."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Singleton pattern for memory manager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize memory manager."""
        if not self._initialized:
            self._histories: Dict[str, List[dict]] = {}
            self._initialized = True
    
    def get_history(self, session_id: str) -> List[dict]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of message dicts with 'role' and 'content'
        """
        if session_id not in self._histories:
            self._histories[session_id] = []
        return self._histories[session_id]
    
    def get_recent_context(self, session_id: str, n_turns: int = 3) -> str:
        """
        Get recent conversation context as a string.
        
        Args:
            session_id: Unique session identifier
            n_turns: Number of recent turns to include
            
        Returns:
            Formatted string of recent conversation
        """
        history = self.get_history(session_id)
        if not history:
            return ""
        
        recent = history[-(n_turns * 2):]  # Each turn has 2 messages
        
        context_parts = []
        for msg in recent:
            role = "Human" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def add_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str
    ) -> None:
        """
        Add a conversation turn to memory.
        
        Args:
            session_id: Unique session identifier
            user_message: User's message
            assistant_message: Assistant's response
        """
        if session_id not in self._histories:
            self._histories[session_id] = []
        
        self._histories[session_id].append({
            "role": "user",
            "content": user_message
        })
        self._histories[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Keep only last 20 messages (10 turns)
        if len(self._histories[session_id]) > 20:
            self._histories[session_id] = self._histories[session_id][-20:]
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear memory for a specific session.
        
        Args:
            session_id: Session to clear
            
        Returns:
            True if session existed and was cleared
        """
        existed = session_id in self._histories
        
        if existed:
            del self._histories[session_id]
        
        return existed
    
    def clear_all(self) -> int:
        """
        Clear all session memories.
        
        Returns:
            Number of sessions cleared
        """
        count = len(self._histories)
        self._histories.clear()
        return count
    
    def list_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return list(self._histories.keys())


def get_memory_manager() -> ConversationMemoryManager:
    """Get the singleton memory manager instance."""
    return ConversationMemoryManager()
