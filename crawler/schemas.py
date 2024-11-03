from ninja import Schema


class NameEntitySchema(Schema):
    name: str
    category: str
    description: str
    short_meaning: str
