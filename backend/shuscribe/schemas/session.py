# shuscribe/schemas/session.py

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import time

from shuscribe.services.llm.providers.provider import LLMProvider
from shuscribe.services.llm.streaming import StreamSession, StreamStatus

from shuscribe.schemas.provider import ProviderName

class ProviderInstance(BaseModel):
    """Model for tracking a provider instance"""
    provider: LLMProvider
    last_used: float = Field(default_factory=time.time)
    provider_name: ProviderName
    api_key_id: str  # Using key_id (masked or "default") instead of actual API key
    
    class Config:
        arbitrary_types_allowed = True  # To allow LLMProvider instances

class UserProviders(BaseModel):
    """Model for tracking all provider instances for a user"""
    user_id: str
    providers: Dict[ProviderName, Dict[str, ProviderInstance]] = Field(default_factory=dict)
    
    def add_provider(self, provider_name: ProviderName, api_key_id: str, provider: LLMProvider) -> ProviderInstance:
        """Add a provider instance for this user"""
        if provider_name not in self.providers:
            self.providers[provider_name] = {}
            
        instance = ProviderInstance(
            provider=provider,
            provider_name=provider_name,
            api_key_id=api_key_id,
            last_used=time.time()
        )
        
        self.providers[provider_name][api_key_id] = instance
        return instance
        
    def get_provider(self, provider_name: ProviderName, api_key_id: str) -> Optional[ProviderInstance]:
        """Get a provider instance if it exists"""
        return self.providers.get(provider_name, {}).get(api_key_id)
        
    def update_last_used(self, provider_name: ProviderName, api_key_id: str) -> None:
        """Update the last used timestamp for a provider"""
        instance = self.get_provider(provider_name, api_key_id)
        if instance:
            instance.last_used = time.time()
            
    def get_idle_providers(self, max_idle_time: float) -> List[ProviderInstance]:
        """Get all provider instances that have been idle for longer than max_idle_time"""
        current_time = time.time()
        idle_providers = []
        
        for provider_dict in self.providers.values():
            for instance in provider_dict.values():
                if current_time - instance.last_used > max_idle_time:
                    idle_providers.append(instance)
                    
        return idle_providers

class StreamSessionInfo(BaseModel):
    """Model for tracking stream session information"""
    session_id: str
    user_id: str
    provider_name: Optional[ProviderName] = None
    model: Optional[str] = None
    status: StreamStatus = StreamStatus.INITIALIZING
    accumulated_text_length: int = 0
    created_at: float = Field(default_factory=time.time)
    last_active: float = Field(default_factory=time.time)
    
    class Config:
        arbitrary_types_allowed = True  # For StreamStatus enum

class SessionRegistry:
    """Model for tracking all stream sessions across users"""
    def __init__(self):
        self.sessions: Dict[str, StreamSession] = {}  # session_id -> StreamSession
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> [session_id]
    
    def add_session(self, session: StreamSession, user_id: str) -> None:
        """Add a session to the registry"""
        self.sessions[session.session_id] = session
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
            
        self.user_sessions[user_id].append(session.session_id)
        
    def get_session(self, session_id: str) -> Optional[StreamSession]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
        
    def get_user_sessions(self, user_id: str) -> List[StreamSession]:
        """Get all sessions for a user"""
        session_ids = self.user_sessions.get(user_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]
        
    def remove_session(self, session_id: str) -> bool:
        """Remove a session from the registry"""
        session = self.sessions.get(session_id)
        if not session:
            return False
            
        # Get the user_id from the session
        user_id = getattr(session, 'user_id', None)
        
        # Remove from sessions dict
        del self.sessions[session_id]
        
        # Remove from user_sessions dict if user_id is known
        if user_id and user_id in self.user_sessions and session_id in self.user_sessions[user_id]:
            self.user_sessions[user_id].remove(session_id)
            
        return True
        
    def get_idle_sessions(self, max_idle_time: float) -> List[str]:
        """Get all session IDs that have been idle for longer than max_idle_time"""
        current_time = time.time()
        idle_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.is_complete or session.has_error or (current_time - session.last_active > max_idle_time):
                idle_sessions.append(session_id)
                
        return idle_sessions