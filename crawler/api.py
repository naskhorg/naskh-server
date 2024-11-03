from ninja import Router
from typing import List

from crawler.models import NameEntity
from crawler.schemas import NameEntitySchema

router = Router()


@router.get("/all", response=List[NameEntitySchema])
def get_all_names(request):
    names = NameEntity.objects.all()
    return [name for name in names]


@router.get("/search", response=List[NameEntitySchema])
def search_name_by_title(request, title=None):
    try:
        query = NameEntity.objects.filter(name__icontains=title)[:15]
        return [name for name in query]
    except Exception as e:
        print(f"Error while searching: {e}")
