import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")


print("URI:", URI)
print("USERNAME:", USERNAME)
print("PASSWORD loaded:", bool(PASSWORD))


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def test_connection():

    with driver.session() as session:

        result = session.run(
            "RETURN 'Neo4j Connected!' AS message"
        )

        record = result.single()

        print(record["message"])


# =====================================================
# ENTITY
# =====================================================

def create_entity(name, entity_type):

    allowed_types = {
        "User",
        "Skill",
        "Company",
        "Topic",
        "Technology"
    }

    if entity_type not in allowed_types:
        raise ValueError(
            f"Invalid entity type: {entity_type}"
        )

    query = f"""
    MERGE (e:Entity {{name: $name}})
    SET e:{entity_type}
    """

    with driver.session() as session:

        session.run(
            query,
            name=name
        )


# =====================================================
# RELATIONSHIP
# =====================================================

def create_relationship(source, relationship_type, target):

    allowed_relationships = {
        "KNOWS",
        "WORKS_AT",
        "LEARNING",
        "USES"
    }

    if relationship_type not in allowed_relationships:
        raise ValueError(
            f"Invalid relationship type: {relationship_type}"
        )

    relationship_queries = {

        "KNOWS": """
        MATCH (source:Entity {name: $source})
        MATCH (target:Entity {name: $target})
        MERGE (source)-[:KNOWS]->(target)
        """,

        "WORKS_AT": """
        MATCH (source:Entity {name: $source})
        MATCH (target:Entity {name: $target})
        MERGE (source)-[:WORKS_AT]->(target)
        """,

        "LEARNING": """
        MATCH (source:Entity {name: $source})
        MATCH (target:Entity {name: $target})
        MERGE (source)-[:LEARNING]->(target)
        """,

        "USES": """
        MATCH (source:Entity {name: $source})
        MATCH (target:Entity {name: $target})
        MERGE (source)-[:USES]->(target)
        """
    }

    query = relationship_queries[relationship_type]

    with driver.session() as session:

        session.run(
            query,
            source=source,
            target=target
        )


# =====================================================
# STORE GRAPH
# =====================================================

def store_graph(graph_data):

    for entity in graph_data.entities:

        create_entity(
            entity.name,
            entity.type
        )

    for relationship in graph_data.relationships:

        create_relationship(
            relationship.source,
            relationship.type,
            relationship.target
        )

def get_user_graph_context(user_name):

    query = """
    MATCH (u:User {name: $user_name})-[r]->(n)
    RETURN
        u.name AS user,
        type(r) AS relationship,
        labels(n) AS labels,
        n.name AS entity
    """

    with driver.session() as session:

        result = session.run(
            query,
            user_name=user_name
        )

        records = list(result)

    context = []

    for record in records:

        context.append(
            f"{record['user']} "
            f"--{record['relationship']}--> "
            f"{record['entity']} "
            f"({', '.join(record['labels'])})"
        )

    return "\n".join(context)


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    test_connection()

    driver.close()