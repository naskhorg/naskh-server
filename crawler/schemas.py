from ninja import Schema


class NameEntitySchema(Schema):
    name: str
    link: str
    category: str
    entity_json: str
