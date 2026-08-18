from pydantic import BaseModel

#defines the schema of my Knowledge Graph & ensures that the LLM output has the expected entity and relationship structure
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