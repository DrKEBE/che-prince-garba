# backend\core\exceptions.py
from fastapi import HTTPException, status

class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class NotFoundException(CustomException):
    def __init__(self, resource: str, id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} avec ID {id} non trouvé"
        )

class InsufficientStockException(CustomException):
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuffisant pour {product_name}: {available} disponible, {requested} demandé"
        )

class BusinessLogicException(CustomException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class ValidationException(CustomException):  # Nouvelle classe
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )