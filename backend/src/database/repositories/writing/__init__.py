"""
Writing Repository Package (STUB)
For future author tools: drafts, worldbuilding documents, etc.
"""

def get_writing_repository():
    """Factory function to get the appropriate Writing repository implementation"""
    from src.config import settings
    
    if settings.SKIP_DATABASE:
        from .writing_in_memory import InMemoryWritingRepository
        return InMemoryWritingRepository()
    else:
        from .writing_supabase import SupabaseWritingRepository
        return SupabaseWritingRepository() 