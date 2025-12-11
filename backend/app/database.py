"""Supabase database connection module"""

from supabase import create_client, Client
from typing import Optional
from app.config import settings


class SupabaseConnection:
    """Singleton class for managing Supabase client connection"""
    
    _instance: Optional['SupabaseConnection'] = None
    _client: Optional[Client] = None
    
    def __new__(cls) -> 'SupabaseConnection':
        """Ensure only one instance of SupabaseConnection exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the Supabase connection if not already initialized"""
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Supabase client with credentials from environment"""
        try:
            self._client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_key
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Supabase client: {str(e)}")
    
    @property
    def client(self) -> Client:
        """Get the Supabase client instance"""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def get_client(self) -> Client:
        """Get the Supabase client instance (alternative method)"""
        return self.client
    
    def test_connection(self) -> bool:
        """Test the connection to Supabase"""
        try:
            # Try a simple query to test connection
            result = self.client.table('gold_queries').select('id').limit(1).execute()
            return True
        except Exception:
            return False


# Global instance
_supabase_connection = SupabaseConnection()


def get_supabase_client() -> Client:
    """Get the global Supabase client instance"""
    return _supabase_connection.client


def test_supabase_connection() -> bool:
    """Test the Supabase connection"""
    return _supabase_connection.test_connection()