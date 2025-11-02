"""
ConversationService - Manages rich conversation contexts for LCA chat

Handles:
- Conversation state with database and method tracking
- Database/method change history
- Manual vs automatic selection modes
- Context preservation across changes
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class ConversationService:
    """Service for managing conversation contexts with rich metadata"""

    def __init__(self):
        """Initialize conversation storage"""
        self.conversations: Dict[str, Dict[str, Any]] = {}

    def create_conversation(
        self,
        database_id: str,
        method_id: Optional[str] = None
    ) -> str:
        """
        Create a new conversation with initial context

        Args:
            database_id: Initial database selection
            method_id: Initial method selection (None = auto)

        Returns:
            Conversation ID
        """
        conv_id = f"conv_{uuid.uuid4().hex[:8]}"

        self.conversations[conv_id] = {
            "id": conv_id,
            "created_at": datetime.utcnow().isoformat(),
            "database_id": database_id,
            "method_id": method_id,
            "method_selection_mode": "manual" if method_id else "auto",
            "messages": [],
            "database_history": [
                {
                    "database_id": database_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "reason": "Initial selection"
                }
            ],
            "method_history": [
                {
                    "method_id": method_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "is_manual": method_id is not None,
                    "reason": "Initial selection"
                }
            ],
            "debug_history": []  # Store debug data for each turn
        }

        return conv_id

    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a conversation by ID

        Args:
            conv_id: Conversation ID

        Returns:
            Conversation object or None if not found
        """
        return self.conversations.get(conv_id)

    def update_database(
        self,
        conv_id: str,
        new_database_id: str,
        reason: str = "User changed database"
    ) -> bool:
        """
        Update database without clearing conversation history

        Args:
            conv_id: Conversation ID
            new_database_id: New database to switch to
            reason: Reason for change (for history tracking)

        Returns:
            True if successful, False if conversation not found
        """
        conv = self.conversations.get(conv_id)
        if not conv:
            return False

        # Only update if actually changing
        if conv["database_id"] == new_database_id:
            return True

        conv["database_id"] = new_database_id
        conv["database_history"].append({
            "database_id": new_database_id,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason
        })

        # When database changes, method may need to reset if it's not available
        # We'll let the calling code handle method validation

        return True

    def update_method(
        self,
        conv_id: str,
        new_method_id: Optional[str],
        is_manual: bool,
        reason: str = "Method selection changed"
    ) -> bool:
        """
        Update LCIA method and track selection mode

        Args:
            conv_id: Conversation ID
            new_method_id: New method (None = auto)
            is_manual: True if user manually selected, False if AI chose
            reason: Reason for change

        Returns:
            True if successful, False if conversation not found
        """
        conv = self.conversations.get(conv_id)
        if not conv:
            return False

        # Only update if actually changing
        if conv["method_id"] == new_method_id:
            return True

        conv["method_id"] = new_method_id
        conv["method_selection_mode"] = "manual" if is_manual else "auto"
        conv["method_history"].append({
            "method_id": new_method_id,
            "timestamp": datetime.utcnow().isoformat(),
            "is_manual": is_manual,
            "reason": reason
        })

        return True

    def add_message(
        self,
        conv_id: str,
        role: str,
        content: str,
        action: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to conversation history

        Args:
            conv_id: Conversation ID
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            action: Action data (for assistant responses)
            metadata: Additional metadata

        Returns:
            True if successful, False if conversation not found
        """
        conv = self.conversations.get(conv_id)
        if not conv:
            return False

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }

        if action:
            message["action"] = action

        if metadata:
            message["metadata"] = metadata

        conv["messages"].append(message)
        return True

    def get_messages(self, conv_id: str) -> List[Dict[str, Any]]:
        """
        Get message history for a conversation

        Args:
            conv_id: Conversation ID

        Returns:
            List of messages or empty list if not found
        """
        conv = self.conversations.get(conv_id)
        if not conv:
            return []

        return conv["messages"]

    def get_context_for_ai(
        self,
        conv_id: str,
        db_name: Optional[str] = None,
        method_name: Optional[str] = None
    ) -> str:
        """
        Build context string for AI system prompt

        Includes information about:
        - Current database and method
        - Selection mode (manual vs auto)
        - Change history

        Args:
            conv_id: Conversation ID
            db_name: Human-readable database name (optional)
            method_name: Human-readable method name (optional)

        Returns:
            Formatted context string for AI
        """
        conv = self.conversations.get(conv_id)
        if not conv:
            return ""

        context_parts = []

        # Current selections
        context_parts.append("# Conversation Context\n")
        context_parts.append(f"**Database**: {db_name or conv['database_id']}")

        if conv["method_id"]:
            mode_indicator = "👤 User-selected" if conv["method_selection_mode"] == "manual" else "🤖 AI-selected"
            context_parts.append(f"**Impact Method**: {method_name or conv['method_id']} ({mode_indicator})")
        else:
            context_parts.append("**Impact Method**: Auto (AI will choose)")

        # Selection mode guidance
        if conv["method_selection_mode"] == "manual":
            context_parts.append("\n⚠️ **Important**: User has manually selected a method. You MUST use this method for all calculations. You may explain why other methods might be relevant, but you cannot change the selection unless the user explicitly asks.")
        else:
            context_parts.append("\n✓ Method is set to Auto. You may recommend and use the most appropriate method for each calculation.")

        # Change history (if any changes occurred)
        if len(conv["database_history"]) > 1:
            context_parts.append("\n## Database Change History")
            for i, change in enumerate(conv["database_history"]):
                if i == 0:
                    continue  # Skip initial selection
                context_parts.append(f"- Changed to {change['database_id']}: {change['reason']}")

        if len(conv["method_history"]) > 1:
            context_parts.append("\n## Method Change History")
            for i, change in enumerate(conv["method_history"]):
                if i == 0:
                    continue  # Skip initial selection
                mode = "Manual" if change["is_manual"] else "Auto"
                method_display = change["method_id"] or "Auto"
                context_parts.append(f"- Changed to {method_display} ({mode}): {change['reason']}")

        return "\n".join(context_parts)

    def get_conversation_summary(self, conv_id: str) -> Dict[str, Any]:
        """
        Get a summary of conversation state

        Args:
            conv_id: Conversation ID

        Returns:
            Summary dict with key information
        """
        conv = self.conversations.get(conv_id)
        if not conv:
            return {}

        return {
            "id": conv["id"],
            "created_at": conv["created_at"],
            "database_id": conv["database_id"],
            "method_id": conv["method_id"],
            "method_selection_mode": conv["method_selection_mode"],
            "message_count": len(conv["messages"]),
            "database_changes": len(conv["database_history"]) - 1,
            "method_changes": len(conv["method_history"]) - 1
        }

    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        List all conversations with summaries

        Returns:
            List of conversation summaries
        """
        return [
            self.get_conversation_summary(conv_id)
            for conv_id in self.conversations.keys()
        ]

    def add_debug_data(self, conv_id: str, debug_data: Dict[str, Any]) -> bool:
        """
        Add debug data for a conversation turn

        Args:
            conv_id: Conversation ID
            debug_data: Debug information to store

        Returns:
            True if successful, False if conversation not found
        """
        conv = self.conversations.get(conv_id)
        if not conv:
            return False

        # Add timestamp to debug data
        debug_data["stored_at"] = datetime.utcnow().isoformat()
        conv["debug_history"].append(debug_data)
        return True

    def get_debug_data(self, conv_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get all debug data for a conversation

        Args:
            conv_id: Conversation ID

        Returns:
            List of debug data entries or None if conversation not found
        """
        conv = self.conversations.get(conv_id)
        if not conv:
            return None

        return conv.get("debug_history", [])
