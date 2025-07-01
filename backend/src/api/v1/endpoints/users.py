# backend/src/api/v1/endpoints/users.py
"""
User management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from src.api.dependencies import (
    get_user_repository_dependency,
    get_current_user_id_dependency
)
from src.database.interfaces.user import IUserRepository
from src.services.llm.llm_service import LLMService
from src.schemas.requests.user import APIKeyRequest, APIKeyResponse

router = APIRouter()


@router.post("/api-keys/{provider}", response_model=APIKeyResponse)
async def store_api_key(
    provider: str,
    request: APIKeyRequest,
    current_user_id: UUID = Depends(get_current_user_id_dependency),
    user_repo: IUserRepository = Depends(get_user_repository_dependency)
):
    """Store and validate user's API key for a provider"""
    try:
        # Create API key data from request
        from src.schemas.db.user import UserAPIKeyCreate
        api_key_data = UserAPIKeyCreate(
            provider=provider,
            api_key=request.api_key,
            provider_metadata=request.provider_metadata or {}
        )

        # Store the API key (this will encrypt it automatically)
        stored_key = await user_repo.store_api_key(
            current_user_id, api_key_data
        )

        # Validate the API key based on request preference
        if request.validate_key:
            try:
                test_model = (
                    LLMService.get_default_test_model_name_for_provider(
                        provider
                    )
                )

                # Simple validation by getting model details
                model_details = LLMService.get_hosted_model_details(
                    provider, test_model
                )
                if model_details:
                    await user_repo.validate_api_key(current_user_id, provider)
                    validation_status = "valid"
                else:
                    validation_status = "invalid"
            except Exception:
                # If validation fails, still store the key but mark as pending
                validation_status = "pending"
        else:
            # Skip validation if requested
            validation_status = "pending"

        # Return response
        return APIKeyResponse(
            provider=provider,
            validation_status=validation_status,
            last_validated_at=stored_key.last_validated_at,
            provider_metadata=stored_key.provider_metadata,
            message="API key stored successfully"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store API key: {str(e)}"
        )
