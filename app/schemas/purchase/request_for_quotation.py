from uuid import UUID
from pydantic import BaseModel
from typing import List


class RFQItemFromPR(BaseModel):
    pr_item_id: UUID


class RFQCreate(BaseModel):
    pr_id: UUID
    pr_item_ids: List[UUID]
    remarks: str | None = None
