from fastapi import status, HTTPException

BATCH_OUTSIDE_ORGANIZATION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The batch you are trying to join is outside your organization.",
)
