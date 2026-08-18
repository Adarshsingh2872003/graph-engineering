from fastapi import FastAPI
from pydantic import BaseModel

from llm import extract_graph_data, generate_answer
from graph import store_graph, get_user_graph_context
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Graph Engineering API",
    description="Knowledge Graph + Graph RAG API",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# REQUEST SCHEMAS
# =========================================

class GraphRequest(BaseModel):
    text: str


class QuestionRequest(BaseModel):
    user_name: str
    question: str


# =========================================
# HOME
# =========================================

@app.get("/")
def home():

    return {
        "message": "Graph Engineering API is running"
    }


# =========================================
# CREATE KNOWLEDGE GRAPH
# =========================================

@app.post("/graph")
def create_graph(request: GraphRequest):

    # STEP 1: Extract entities and relationships
    graph_data = extract_graph_data(request.text)

    # STEP 2: Store in Neo4j
    store_graph(graph_data)

    return {
        "message": "Knowledge Graph stored successfully",
        "entities": [
            {
                "name": entity.name,
                "type": entity.type
            }
            for entity in graph_data.entities
        ],
        "relationships": [
            {
                "source": relationship.source,
                "type": relationship.type,
                "target": relationship.target
            }
            for relationship in graph_data.relationships
        ]
    }


# =========================================
# GRAPH RAG QUESTION
# =========================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    # STEP 1: Retrieve graph context
    graph_context = get_user_graph_context(
        request.user_name
    )

    # STEP 2: Generate answer using Graph RAG
    answer = generate_answer(
        request.question,
        graph_context
    )

    return {
        "user": request.user_name,
        "question": request.question,
        "graph_context": graph_context,
        "answer": answer
    }