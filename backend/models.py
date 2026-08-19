from pydantic import BaseModel


# =========================================
# ENTITY
# =========================================

class Entity(BaseModel):

    name: str
    type: str


# =========================================
# RELATIONSHIP
# =========================================

class Relationship(BaseModel):

    source: str
    type: str
    target: str


# =========================================
# GRAPH DATA
# =========================================

class GraphData(BaseModel):

    entities: list[Entity]
    relationships: list[Relationship]