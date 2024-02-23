from fastapi import HTTPException, status

MAX_ORGANIZATION_CAPACITY = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="max organization capacity reached."
)

MAX_JOINING_ATTEMPTS = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="too many attempts to join org."
)
