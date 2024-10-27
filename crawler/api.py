from ninja import Router
from typing import List

from crawler.models import NameEntity
from crawler.schemas import NameEntitySchema

router = Router()


@router.get("/all", response=List[NameEntitySchema])
def get_all_names(request):
    names = NameEntity.objects.all()
    return [name for name in names]
