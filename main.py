from llm import (
    extract_graph_data,
    generate_answer
)

from graph import (
    store_graph,
    get_user_graph_context,
    driver
)



# USER DATA


text = """
My name is Adarsh.
I know Python and JavaScript.
I am learning Graph Engineering.
I work at ABC Technologies.
"""



# STEP 1: EXTRACT GRAPH DATA


print("\n==============================")
print("STEP 1: GRAPH EXTRACTION")
print("==============================")


graph_data = extract_graph_data(text)


print("\nENTITIES:")

for entity in graph_data.entities:

    print(entity)


print("\nRELATIONSHIPS:")

for relationship in graph_data.relationships:

    print(relationship)



# STEP 2: STORE GRAPH IN NEO4J


print("\n==============================")
print("STEP 2: STORE GRAPH")
print("==============================")


store_graph(graph_data)


print("\nKnowledge Graph stored successfully!")



# STEP 3: RETRIEVE GRAPH CONTEXT


print("\n==============================")
print("STEP 3: GRAPH RETRIEVAL")
print("==============================")


user_name = "Adarsh"


graph_context = get_user_graph_context(
    user_name
)


print("\nGRAPH CONTEXT:")

print(graph_context)



# STEP 4: USER QUESTION


print("\n==============================")
print("STEP 4: USER QUESTION")
print("==============================")


question = input(
    "\nAsk something about Adarsh: "
)



# STEP 5: GRAPH RAG


print("\n==============================")
print("STEP 5: GRAPH RAG")
print("==============================")


answer = generate_answer(
    question,
    graph_context
)



# STEP 6: FINAL ANSWER


print("\nFINAL ANSWER:")

print(answer)


# STEP 7: CLOSE NEO4J


driver.close()