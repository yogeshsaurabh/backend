from fastapi import status, HTTPException

BATCH_NOT_ALLOWED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="You don't have access to this batch.",
)
