from pydantic import BaseModel


class Entity(BaseModel):
    name: str
    type: str


class Relationship(BaseModel):
    source: str
    type: str
    target: str


class GraphData(BaseModel):
    entities: list[Entity]
    relationships: list[Relationship]