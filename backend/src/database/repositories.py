# backend/src/database/repositories.py
"""
DEPRECATED: Repository implementations have been moved to improve dependency injection.

This file is kept for backward compatibility but will be removed in a future cleanup.

New structure:
- Database implementations: src/database/sqlalchemy/repositories/
- Memory implementations: src/database/memory/repositories/
- Use factory.py to create repository instances with proper dependency injection.
"""

import warnings

# Deprecation warning for any code that might import from here
warnings.warn(
    "src/database/repositories.py is deprecated. "
    "Use src/database/factory.py to create repository instances. "
    "Database implementations are in src/database/sqlalchemy/repositories/ "
    "and memory implementations are in src/database/memory/repositories/",
    DeprecationWarning,
    stacklevel=2
)

# Note: All repository implementations have been moved to their respective directories
# to follow proper dependency injection principles where:
# - Interfaces define contracts (src/database/interfaces/)
# - Domain models are persistence-agnostic (src/database/interfaces/models/)
# - SQLAlchemy implementations use mappers (src/database/sqlalchemy/)
# - Memory implementations work directly with domain models (src/database/memory/)