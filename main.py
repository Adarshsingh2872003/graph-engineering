from llm import extract_graph_data

from graph import (
    store_graph,
    get_user_graph_context,
    driver
)


text = """
My name is Adarsh.
I know Python and JavaScript.
I am learning Graph Engineering.
I work at ABC Technologies.
"""


# =========================================
# STEP 1: Extract graph data using LLM
# =========================================

graph_data = extract_graph_data(text)


print("\nENTITIES:")

for entity in graph_data.entities:

    print(entity)


print("\nRELATIONSHIPS:")

for relationship in graph_data.relationships:

    print(relationship)


# =========================================
# STEP 2: Store graph in Neo4j
# =========================================

store_graph(graph_data)

print("\nKnowledge Graph stored successfully!")


# =========================================
# STEP 3: Retrieve graph context
# =========================================

user_name = "Adarsh"

graph_context = get_user_graph_context(
    user_name
)


print("\nGRAPH CONTEXT:")

print(graph_context)


# =========================================
# STEP 4: Close Neo4j
# =========================================

driver.close()