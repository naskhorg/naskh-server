from django.db import models

QURANIC_NATURE = {
    "Directly Mentioned": "direct",
    "Indirectly Mentioned": "indirect",
}


class NameEntity(models.Model):
    name = models.CharField(max_length=255)
    link = models.URLField(unique=True)
    category = models.CharField(max_length=255)
    description = models.TextField(default="")
    short_meaning = models.CharField(max_length=255, default="")
    arabic_name = models.CharField(max_length=255, default="")
    quranic_nature = models.CharField(
        max_length=255, choices=QURANIC_NATURE, default="indirect"
    )
    alternative_spellings = models.ManyToManyField("self")
    similar_root_names = models.ManyToManyField("self")
    details = models.TextField(default="")

    def __str__(self):
        return self.name
