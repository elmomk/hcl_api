"""Example Pydantic model used for testing and demonstration purposes."""
from pydantic import BaseModel


class Item(BaseModel):
    """Simple item model with optional description and tax."""
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
