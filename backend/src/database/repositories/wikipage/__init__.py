"""
Wiki Page Repository Package
"""

def get_wikipage_repository():
    """Factory function to get the appropriate WikiPage repository implementation"""
    from src.config import settings
    
    if settings.SKIP_DATABASE:
        from .wikipage_in_memory import InMemoryWikiPageRepository
        return InMemoryWikiPageRepository()
    else:
        from .wikipage_supabase import SupabaseWikiPageRepository
        return SupabaseWikiPageRepository()