from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class PRExcelRow(BaseModel):
    pr_date: Optional[date] = None
    material_name: str
    qty: float
    factory_name: str
    department: str
    required_by_date: Optional[date] = None
    remarks: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    
class PRExcelImportRequest(BaseModel):
    rows: List[PRExcelRow]