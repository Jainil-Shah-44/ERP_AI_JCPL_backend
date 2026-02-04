from app.crud.base import CRUDBase

from app.models.department import Department
from app.models.factory import Factory
from app.models.category import ItemCategory
from app.models.group import ItemGroup
from app.models.unit import Unit
from app.models.raw_material import RawMaterial
from app.models.vendor import Vendor
from app.models.warehouse import Warehouse

department = CRUDBase(Department)
factory = CRUDBase(Factory)
category = CRUDBase(ItemCategory)
group = CRUDBase(ItemGroup)
unit = CRUDBase(Unit)
raw_material = CRUDBase(RawMaterial)
vendor = CRUDBase(Vendor)
warehouse = CRUDBase(Warehouse)
