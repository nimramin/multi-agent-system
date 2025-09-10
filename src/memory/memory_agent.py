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
from agents.base_agent import BaseAgent
from models.message import AgentMessage, TaskResult
from loguru import logger

class MemoryAgent(BaseAgent):
    """Agent specialized for memory management and retrieval"""
    def __init__(self, storage_path: str = "memory_storage"):
        """Initialize Memory Agent with vector DB and file storage"""
        super().__init__("memory_agent", ["store", "retrieve", "search", "remember"])
        
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize ChromaDB with default settings - no custom embeddings
        self.chroma_client = chromadb.PersistentClient(
            path=os.path.join(storage_path, "chroma_db"),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create collections with default embeddings
        self.conversation_collection = self._get_or_create_collection("conversations")
        self.knowledge_collection = self._get_or_create_collection("knowledge")
        self.agent_state_collection = self._get_or_create_collection("agent_states")
        
        # File paths for structured metadata
        self.conversation_metadata_file = os.path.join(storage_path, "conversation_metadata.json")
        self.knowledge_metadata_file = os.path.join(storage_path, "knowledge_metadata.json")
        
        # Load existing metadata
        self.conversation_metadata = self._load_metadata(self.conversation_metadata_file)
        self.knowledge_metadata = self._load_metadata(self.knowledge_metadata_file)
        self.embedding_function = None  # Force default ChromaDB embeddings
    
    def _get_or_create_collection(self, name: str):
        """Get existing collection or create new one"""
        try:
            return self.chroma_client.get_or_create_collection(name=name)
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
            
            def _has_word(text: str, word: str) -> bool:
                import re
                return re.search(rf"\b{re.escape(word)}\b", text) is not None
            
            if _has_word(content, "store") or _has_word(content, "save"):
                result = await self._store_memory(message)
            elif _has_word(content, "retrieve") or _has_word(content, "get"):
                result = await self._retrieve_memory(message)
            elif _has_word(content, "search") or _has_word(content, "find"):
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
        topic = message.metadata.get("topic")
        keywords: List[str] = message.metadata.get("keywords", [])
        source = message.metadata.get("source", "unknown")
        confidence = message.metadata.get("confidence", 0.5)
        agent_name = message.metadata.get("agent", message.sender)
        
        # Generate unique ID for this memory
        memory_id = f"{memory_type}_{datetime.now().timestamp()}"
        
        # Prepare content for vector storage
        content_text = f"{message.content} {json.dumps(data)}"
        # Basic keyword extraction fallback if none provided
        if not keywords:
            words = [w.strip('.,:;!?#()[]{}"\'') for w in message.content.lower().split()]
            keywords = [w for w in words if w.isalpha() and len(w) > 3][:10]
        # Try to infer topic from data if not provided
        if topic is None and isinstance(data, dict):
            topic = data.get("topic")
        # Chroma metadatas must be primitives and non-None
        keywords_csv = ",".join(keywords) if keywords else ""
        topic_str = str(topic) if topic is not None else ""
        source_str = str(source) if source is not None else ""
        agent_str = str(agent_name) if agent_name is not None else ""
        
        if memory_type == "conversation":
            # Store in conversation collection
            self.conversation_collection.add(
                documents=[content_text],
                metadatas=[{
                    "timestamp": str(datetime.now()),
                    "sender": message.sender,
                    "type": "conversation",
                    "topic": topic_str,
                    "keywords_csv": keywords_csv,
                    "source": source_str,
                    "agent": agent_str,
                    "confidence": confidence
                }],
                ids=[memory_id],
                # embeddings=None if self.embedding_function else [self._cheap_embed(content_text, self._fallback_embedding_dim)]
            )
            
            # Update metadata
            self.conversation_metadata[memory_id] = {
                "content": message.content,
                "data": data,
                "timestamp": str(datetime.now()),
                "sender": message.sender,
                "topic": topic,
                "keywords": keywords,
                "source": source,
                "agent": agent_name,
                "confidence": confidence
            }
            self._save_metadata(self.conversation_metadata, self.conversation_metadata_file)
            
        elif memory_type == "knowledge":
            # Store in knowledge collection
            self.knowledge_collection.add(
                documents=[content_text],
                metadatas=[{
                    "timestamp": str(datetime.now()),
                    "source": source,
                    "confidence": confidence,
                    "type": "knowledge",
                    "topic": topic_str,
                    "keywords_csv": keywords_csv,
                    "agent": agent_str
                }],
                ids=[memory_id],
                embeddings=None if self.embedding_function else [self._cheap_embed(content_text, self._fallback_embedding_dim)]
            )
            
            # Update knowledge metadata
            self.knowledge_metadata[memory_id] = {
                "content": message.content,
                "data": data,
                "timestamp": str(datetime.now()),
                "source": source,
                "confidence": confidence,
                "topic": topic,
                "keywords": keywords,
                "agent": agent_name
            }
            self._save_metadata(self.knowledge_metadata, self.knowledge_metadata_file)
        elif memory_type == "agent_state":
            # Track what each agent learned/accomplished per task
            self.agent_state_collection.add(
                documents=[content_text],
                metadatas=[{
                    "timestamp": str(datetime.now()),
                    "agent": agent_str,
                    "type": "agent_state",
                    "topic": topic_str,
                    "keywords_csv": keywords_csv,
                    "source": source_str,
                    "confidence": confidence
                }],
                ids=[memory_id],
                embeddings=None if self.embedding_function else [self._cheap_embed(content_text, self._fallback_embedding_dim)]
            )
            # Persist agent state to conversation metadata file under a dedicated key
            # (kept simple to avoid new file introduction)
            state_key = "__agent_state__"
            if state_key not in self.conversation_metadata:
                self.conversation_metadata[state_key] = []
            self.conversation_metadata[state_key].append({
                "id": memory_id,
                "agent": agent_name,
                "topic": topic,
                "keywords": keywords,
                "data": data,
                "timestamp": str(datetime.now()),
                "confidence": confidence
            })
            self._save_metadata(self.conversation_metadata, self.conversation_metadata_file)
        
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
        """Search memory using keyword/topic filters plus vector similarity"""
        query = message.content
        memory_type = message.metadata.get("memory_type", "conversation")
        n_results = message.metadata.get("limit", 3)
        topic_filter = message.metadata.get("topic")
        keywords_filter: List[str] = message.metadata.get("keywords", [])
        
        # Choose collection based on memory type
        collection = (self.conversation_collection if memory_type == "conversation" 
                     else self.knowledge_collection)
        search_results = []
        try:
            # Perform vector similarity search when embeddings are available
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            if results.get("documents") and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    meta = results["metadatas"][0][i]
                    match_topic = (topic_filter is None) or (meta.get("topic") == topic_filter)
                    match_keywords = True
                    if keywords_filter:
                        stored_csv = meta.get("keywords_csv") or ""
                        match_keywords = any(k in stored_csv for k in keywords_filter)
                    if match_topic and match_keywords:
                        result_data = {
                            "content": doc,
                            "metadata": meta,
                            "distance": results.get("distances", [[None]])[0][i],
                            "id": results.get("ids", [[None]])[0][i]
                        }
                        search_results.append(result_data)
        except Exception:
            # Fallback: no embeddings available. Do a simple substring search over stored documents.
            all_items = collection.get(limit=100)
            docs = all_items.get("documents", []) or []
            metas = all_items.get("metadatas", []) or []
            ids = all_items.get("ids", []) or []
            # Build simple query tokens
            stop_words = {"the","a","an","and","or","but","in","on","at","to","for","of","with","by","about","is","are","what","find","search"}
            q_tokens = [w for w in query.lower().split() if w not in stop_words and len(w) > 2]
            for i, doc in enumerate(docs):
                meta = metas[i] if i < len(metas) else {}
                # Basic match: any token contained
                doc_lower = (doc or "").lower()
                match_text = any(t in doc_lower for t in q_tokens) if q_tokens else False
                match_topic = (topic_filter is None) or (meta.get("topic") == topic_filter)
                match_keywords = True
                if keywords_filter:
                    stored_csv = meta.get("keywords_csv") or ""
                    match_keywords = any(k in stored_csv for k in keywords_filter)
                if match_text and match_topic and match_keywords:
                    search_results.append({
                        "content": doc,
                        "metadata": meta,
                        "distance": None,
                        "id": ids[i] if i < len(ids) else None
                    })
            # Truncate to requested number
            search_results = search_results[:n_results]

        # If vector search returned nothing, attempt textual fallback too
        if not search_results:
            all_items = collection.get(limit=500)
            docs = all_items.get("documents", []) or []
            metas = all_items.get("metadatas", []) or []
            ids = all_items.get("ids", []) or []
            q_lower = query.lower().strip()
            for i, doc in enumerate(docs):
                if q_lower == (doc or "").lower().strip() or q_lower in (doc or "").lower():
                    search_results.append({
                        "content": doc,
                        "metadata": metas[i] if i < len(metas) else {},
                        "distance": None,
                        "id": ids[i] if i < len(ids) else None
                    })
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