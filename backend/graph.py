import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


# =========================================
# ENVIRONMENT
# =========================================

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


if not NEO4J_URI:
    raise ValueError("NEO4J_URI missing")

if not NEO4J_USERNAME:
    raise ValueError("NEO4J_USERNAME missing")

if not NEO4J_PASSWORD:
    raise ValueError("NEO4J_PASSWORD missing")


# =========================================
# DRIVER
# =========================================

driver = GraphDatabase.driver(

    NEO4J_URI,

    auth=(
        NEO4J_USERNAME,
        NEO4J_PASSWORD
    )
)


# =========================================
# CONNECTION TEST
# =========================================

def test_connection():

    with driver.session() as session:

        session.run(
            "RETURN 1"
        ).consume()

    print("Neo4j Connected!")


# =========================================
# CLEAR OLD GRAPH
# =========================================

def clear_graph():

    with driver.session() as session:

        session.run(
            """
            MATCH (n)
            DETACH DELETE n
            """
        ).consume()

    print("Old graph deleted.")


# =========================================
# STORE GRAPH
# =========================================

def store_graph(graph_data):

    allowed_relationships = {

        "KNOWS",
        "WORKS_AT",
        "STUDIED_AT",
        "BUILT",
        "HAS_SKILL",
        "USES",
        "WORKED_AS",
        "LEARNING",
        "HAS_EDUCATION",
        "HAS_EXPERIENCE",
        "HAS_CERTIFICATION"
    }

    with driver.session() as session:

        # =====================================
        # ENTITIES
        # =====================================

        for entity in graph_data.entities:

            session.run(

                """
                MERGE (e:Entity {
                    name: $name
                })

                SET e.type = $type
                """,

                name=entity.name.strip(),

                type=entity.type.strip()
            ).consume()

        # =====================================
        # RELATIONSHIPS
        # =====================================

        for relationship in graph_data.relationships:

            relationship_type = (
                relationship.type
                .upper()
                .strip()
            )

            if relationship_type not in allowed_relationships:

                print(
                    "Skipping relationship:",
                    relationship_type
                )

                continue

            query = f"""
            MATCH (source:Entity {{
                name: $source
            }})

            MATCH (target:Entity {{
                name: $target
            }})

            MERGE (
                source
            )-[:{relationship_type}]->
            (
                target
            )
            """

            session.run(

                query,

                source=relationship.source.strip(),

                target=relationship.target.strip()
            ).consume()

    print(
        "Knowledge Graph stored successfully!"
    )


# =========================================
# GET COMPLETE USER CONTEXT
# =========================================

def get_user_graph_context(
    user_name="Adarsh"
):

    user_name = user_name.strip()

    print("\n=========================================")
    print("GRAPH SEARCH")
    print("=========================================")

    print(
        "Searching for:",
        user_name
    )

    with driver.session() as session:

        # =====================================
        # FIND USER
        # =====================================

        result = session.run(

            """
            MATCH (u:Entity)

            WHERE
                u.type = 'User'
                AND (
                    toLower(u.name) = toLower($name)
                    OR
                    toLower(u.name) CONTAINS
                    toLower($name)
                    OR
                    toLower($name) CONTAINS
                    toLower(u.name)
                )

            RETURN
                u.name AS name,
                u.type AS type

            LIMIT 1
            """,

            name=user_name
        )

        user = result.single()

        if not user:

            print(
                "USER NOT FOUND:",
                user_name
            )

            return ""

        actual_name = user["name"]

        print(
            "USER FOUND:",
            actual_name
        )

        # =====================================
        # GET ALL CONNECTIONS
        # =====================================

        result = session.run(

            """
            MATCH (u:Entity {
                name: $name
            })

            OPTIONAL MATCH path =
                (u)-[*1..3]->(target:Entity)

            WHERE target <> u

            RETURN
                nodes(path) AS nodes,
                relationships(path) AS relationships
            """,

            name=actual_name
        )

        # -------------------------------------------------
        # IMPORTANT:
        # Iterate the raw Result directly instead of calling
        # result.data(). .data() converts Neo4j Relationship
        # objects into plain tuples (start, type, end), which
        # do NOT have a .type attribute. Iterating the Result
        # keeps nodes/relationships as native Neo4j graph
        # objects (Node / Relationship) so `.type` and `.get()`
        # work correctly below.
        # -------------------------------------------------

        records = list(result)

        print(
            "Graph paths found:",
            len(records)
        )

        context_lines = []

        # =====================================
        # BUILD CONTEXT
        # =====================================

        for record in records:

            nodes = record["nodes"]
            relationships = record["relationships"]

            if not nodes:
                continue

            for i, relationship in enumerate(
                relationships
            ):

                source = nodes[i]
                target = nodes[i + 1]

                source_name = source.get(
                    "name"
                )

                source_type = source.get(
                    "type"
                )

                target_name = target.get(
                    "name"
                )

                target_type = target.get(
                    "type"
                )

                relationship_type = (
                    relationship.type
                )

                line = (
                    f"{source_name} "
                    f"({source_type}) "
                    f"--{relationship_type}--> "
                    f"{target_name} "
                    f"({target_type})"
                )

                context_lines.append(line)

        # =====================================
        # REMOVE DUPLICATES
        # =====================================

        context_lines = list(
            dict.fromkeys(
                context_lines
            )
        )

        context = "\n".join(
            context_lines
        )

        print(
            "\nCONTEXT RECORDS:",
            len(context_lines)
        )

        print("\nFINAL CONTEXT:")
        print(context)

        print(
            "========================================="
        )

        return context


# =========================================
# CLOSE
# =========================================

def close_driver():

    driver.close()