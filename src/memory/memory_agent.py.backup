"""
Memory Agent - Handles long-term storage, retrieval, and context management.
Uses ChromaDB for vector similarity search and JSON for structured metadata.
Manages conversation history, knowledge base, and agent state memory.
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import chromadb
from chromadb.config import Settings
from .base_agent import BaseAgent
from ..models.message import AgentMessage, TaskResult

class MemoryAgent(BaseAgent):
    """Agent specialized for memory management and retrieval"""
    
    def __init__(self, storage_path: str = "memory_storage"):
        """Initialize Memory Agent with vector DB and file storage"""
        super().__init__("memory_agent", ["store", "retrieve", "search", "remember"])
        
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize ChromaDB for vector similarity search
        self.chroma_client = chromadb.PersistentClient(
            path=os.path.join(storage_path, "chroma_db"),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create collections for different memory types
        self.conversation_collection = self._get_or_create_collection("conversations")
        self.knowledge_collection = self._get_or_create_collection("knowledge")
        self.agent_state_collection = self._get_or_create_collection("agent_states")
        
        # File paths for structured metadata
        self.conversation_metadata_file = os.path.join(storage_path, "conversation_metadata.json")
        self.knowledge_metadata_file = os.path.join(storage_path, "knowledge_metadata.json")
        
        # Load existing metadata
        self.conversation_metadata = self._load_metadata(self.conversation_metadata_file)
        self.knowledge_metadata = self._load_metadata(self.knowledge_metadata_file)
        
    def _get_or_create_collection(self, name: str):
        """Get existing collection or create new one"""
        try:
            return self.chroma_client.get_collection(name=name)
        except ValueError:
            return self.chroma_client.create_collection(name=name)
    
    def _load_metadata(self, file_path: str) -> Dict[str, Any]:
        """Load metadata from JSON file"""
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self, data: Dict[str, Any], file_path: str):
        """Save metadata to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    async def process_task(self, message: AgentMessage) -> TaskResult:
        """Process memory-related tasks (store, retrieve, search)"""
        start_time = asyncio.get_event_loop().time()
        self.log_message(message)
        
        try:
            content = message.content.lower()
            
            if "store" in content or "save" in content:
                result = await self._store_memory(message)
            elif "retrieve" in content or "get" in content:
                result = await self._retrieve_memory(message)
            elif "search" in content or "find" in content:
                result = await self._search_memory(message)
            else:
                result = await self._general_memory_query(message)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return TaskResult(
                agent_id=self.agent_id,
                success=True,
                data=result,
                confidence=0.9,
                execution_time=execution_time
            )
            
        except Exception as e:
            return TaskResult(
                agent_id=self.agent_id,
                success=False,
                data={},
                confidence=0.0,
                execution_time=asyncio.get_event_loop().time() - start_time,
                error=str(e)
            )
    
    async def _store_memory(self, message: AgentMessage) -> Dict[str, Any]:
        """Store new information in memory"""
        data = message.metadata.get("data", {})
        memory_type = message.metadata.get("memory_type", "conversation")
        
        # Generate unique ID for this memory
        memory_id = f"{memory_type}_{datetime.now().timestamp()}"
        
        # Prepare content for vector storage
        content_text = f"{message.content} {json.dumps(data)}"
        
        if memory_type == "conversation":
            # Store in conversation collection
            self.conversation_collection.add(
                documents=[content_text],
                metadatas=[{
                    "timestamp": str(datetime.now()),
                    "sender": message.sender,
                    "type": "conversation"
                }],
                ids=[memory_id]
            )
            
            # Update metadata
            self.conversation_metadata[memory_id] = {
                "content": message.content,
                "data": data,
                "timestamp": str(datetime.now()),
                "sender": message.sender
            }
            self._save_metadata(self.conversation_metadata, self.conversation_metadata_file)
            
        elif memory_type == "knowledge":
            # Store in knowledge collection
            self.knowledge_collection.add(
                documents=[content_text],
                metadatas=[{
                    "timestamp": str(datetime.now()),
                    "source": message.metadata.get("source", "unknown"),
                    "confidence": message.metadata.get("confidence", 0.5),
                    "type": "knowledge"
                }],
                ids=[memory_id]
            )
            
            # Update knowledge metadata
            self.knowledge_metadata[memory_id] = {
                "content": message.content,
                "data": data,
                "timestamp": str(datetime.now()),
                "source": message.metadata.get("source", "unknown"),
                "confidence": message.metadata.get("confidence", 0.5)
            }
            self._save_metadata(self.knowledge_metadata, self.knowledge_metadata_file)
        
        return {
            "action": "stored",
            "memory_id": memory_id,
            "memory_type": memory_type,
            "content_length": len(content_text)
        }
    
    async def _retrieve_memory(self, message: AgentMessage) -> Dict[str, Any]:
        """Retrieve specific memory by ID or recent memories"""
        memory_id = message.metadata.get("memory_id")
        memory_type = message.metadata.get("memory_type", "conversation")
        limit = message.metadata.get("limit", 5)
        
        if memory_id:
            # Retrieve specific memory
            if memory_type == "conversation" and memory_id in self.conversation_metadata:
                return {
                    "action": "retrieved",
                    "memory": self.conversation_metadata[memory_id]
                }
            elif memory_type == "knowledge" and memory_id in self.knowledge_metadata:
                return {
                    "action": "retrieved", 
                    "memory": self.knowledge_metadata[memory_id]
                }
        else:
            # Retrieve recent memories
            metadata = self.conversation_metadata if memory_type == "conversation" else self.knowledge_metadata
            recent_memories = sorted(
                metadata.items(),
                key=lambda x: x[1].get("timestamp", ""),
                reverse=True
            )[:limit]
            
            return {
                "action": "retrieved",
                "memories": [{"id": k, **v} for k, v in recent_memories],
                "count": len(recent_memories)
            }
        
        return {"action": "retrieved", "result": "not found"}
    
    async def _search_memory(self, message: AgentMessage) -> Dict[str, Any]:
        """Search memory using vector similarity"""
        query = message.content
        memory_type = message.metadata.get("memory_type", "conversation")
        n_results = message.metadata.get("limit", 3)
        
        # Choose collection based on memory type
        collection = (self.conversation_collection if memory_type == "conversation" 
                     else self.knowledge_collection)
        
        # Perform vector similarity search
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        search_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                result_data = {
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                    "id": results["ids"][0][i]
                }
                search_results.append(result_data)
        
        return {
            "action": "searched",
            "query": query,
            "results": search_results,
            "count": len(search_results)
        }
    
    async def _general_memory_query(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle general memory queries"""
        # Try to understand what user is asking for
        content = message.content.lower()
        
        if "what did" in content or "earlier" in content or "before" in content:
            # Search for relevant past conversations
            return await self._search_memory(message)
        elif "remember" in content:
            # Store the information
            return await self._store_memory(message)
        else:
            # General memory status
            return {
                "action": "status",
                "conversation_memories": len(self.conversation_metadata),
                "knowledge_memories": len(self.knowledge_metadata),
                "available_actions": ["store", "retrieve", "search"]
            }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        return {
            "conversation_count": len(self.conversation_metadata),
            "knowledge_count": len(self.knowledge_metadata),
            "storage_path": self.storage_path,
            "collections": ["conversations", "knowledge", "agent_states"]
        }