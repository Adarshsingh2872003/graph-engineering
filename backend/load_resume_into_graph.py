from resume_loader import load_resume_text
from llm import extract_graph_data
from graph import store_graph


def main():

    print("\n=========================================")
    print("RESUME → KNOWLEDGE GRAPH")
    print("=========================================")

    # 1. Load PDF
    resume_text = load_resume_text()

    # 2. Extract entities + relationships using LLM
    print("\nExtracting graph data from resume...")

    graph_data = extract_graph_data(resume_text)

    print("\n=========================================")
    print("GRAPH DATA EXTRACTED")
    print("=========================================")

    print(
        f"Entities: {len(graph_data.entities)}"
    )

    print(
        f"Relationships: {len(graph_data.relationships)}"
    )

    # 3. Store in Neo4j
    print("\nStoring data in Neo4j...")

    store_graph(graph_data)

    print("\n=========================================")
    print("RESUME GRAPH CREATED SUCCESSFULLY")
    print("=========================================")


if __name__ == "__main__":
    main()