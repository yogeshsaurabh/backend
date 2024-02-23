from fastapi import HTTPException, status


class EmailNotFoundException(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f'record with email "{email}" not found.',
        )


class PhoneNumberNotFoundException(HTTPException):
    def __init__(self, phone_number: str):
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f'record with phone number "{phone_number}" not found.',
        )


class RecordNotFoundException(HTTPException):
    def __init__(self, id_: int):
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"record with id {id_} not found",
        )


class NoSuchRecordException(HTTPException):
    def __init__(self, msg: str = ""):
        super().__init__(status.HTTP_404_NOT_FOUND, msg)


class UniqueConstraintFailedException(HTTPException):
    def __init__(self, msg: str = ""):
        super().__init__(status.HTTP_400_BAD_REQUEST, msg)


class QueryException(HTTPException):
    def __init__(self, error=""):
        super().__init__(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Query Error : {error}"
        )


class DBCreateException(HTTPException):
    def __init__(self, error=""):
        super().__init__(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"DB Create Error : {error}"
        )


class DBUpdateException(HTTPException):
    def __init__(self, error=""):
        super().__init__(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"DB Update Error : {error}"
        )


class DBDeleteException(HTTPException):
    def __init__(self, error=""):
        super().__init__(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"DB Delete Error : {error}"
        )
