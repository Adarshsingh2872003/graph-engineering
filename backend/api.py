from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from llm import extract_graph_data, generate_answer
from graph import (
    store_graph,
    get_user_graph_context,
    driver
)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Adarsh AI - Graph RAG API",
    description="Personal Resume Knowledge Graph + Graph RAG Assistant",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "https://graph-engineering-iota.vercel.app"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# REQUEST MODELS
# =========================================================

class GraphRequest(BaseModel):

    text: str


class QuestionRequest(BaseModel):

    user_name: str

    question: str


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "Adarsh AI Graph RAG API is running",
        "status": "online"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    try:

        with driver.session() as session:

            result = session.run(
                "RETURN 1 AS status"
            )

            record = result.single()

            if record and record["status"] == 1:

                return {
                    "status": "healthy",
                    "neo4j": "connected"
                }

    except Exception as e:

        print("Health check error:", e)

        raise HTTPException(
            status_code=500,
            detail=f"Neo4j connection failed: {str(e)}"
        )


# =========================================================
# CREATE / STORE KNOWLEDGE GRAPH
# =========================================================

@app.post("/graph")
def create_graph(request: GraphRequest):

    print("\n=========================================")
    print("CREATE GRAPH")
    print("=========================================")

    try:

        text = request.text.strip()

        if not text:

            raise HTTPException(
                status_code=400,
                detail="Text cannot be empty."
            )


        print("Extracting graph data...")


        # -------------------------------------------------
        # STEP 1
        # LLM -> ENTITIES + RELATIONSHIPS
        # -------------------------------------------------

        graph_data = extract_graph_data(text)


        print(
            f"Entities extracted: "
            f"{len(graph_data.entities)}"
        )

        print(
            f"Relationships extracted: "
            f"{len(graph_data.relationships)}"
        )


        # -------------------------------------------------
        # STEP 2
        # STORE IN NEO4J
        # -------------------------------------------------

        print("Storing graph in Neo4j...")


        store_graph(graph_data)


        print("Graph stored successfully!")


        # -------------------------------------------------
        # STEP 3
        # RESPONSE
        # -------------------------------------------------

        return {

            "success": True,

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


    except HTTPException:

        raise


    except Exception as e:

        print("\n=========================================")
        print("GRAPH CREATION ERROR")
        print("=========================================")

        print(type(e).__name__)
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# ASK GRAPH RAG
# =========================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    print("\n=========================================")
    print("GRAPH RAG QUESTION")
    print("=========================================")

    print(
        "User:",
        request.user_name
    )

    print(
        "Question:",
        request.question
    )


    try:

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        user_name = request.user_name.strip()

        question = request.question.strip()


        if not user_name:

            raise HTTPException(
                status_code=400,
                detail="User name cannot be empty."
            )


        if not question:

            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty."
            )


        # -------------------------------------------------
        # STEP 1
        # GET GRAPH CONTEXT
        # -------------------------------------------------

        print("\nSTEP 1: Getting graph context...")


        graph_context = get_user_graph_context(
            user_name
        )


        print("\n=========================================")
        print("GRAPH CONTEXT")
        print("=========================================")

        print(graph_context)


        # -------------------------------------------------
        # CHECK GRAPH CONTEXT
        # -------------------------------------------------

        if not graph_context.strip():

            print(
                "\nWARNING: No graph context found."
            )


            return {

                "success": True,

                "user": user_name,

                "question": question,

                "answer": (
                    "I couldn't find relevant "
                    "information about Adarsh "
                    "in the available resume data."
                ),

                "graph_context": ""
            }


        # -------------------------------------------------
        # STEP 2
        # GENERATE ANSWER
        # -------------------------------------------------

        print(
            "\nSTEP 2: Generating AI answer..."
        )


        answer = generate_answer(
            question,
            graph_context
        )


        print("\n=========================================")
        print("FINAL ANSWER")
        print("=========================================")

        print(answer)


        # -------------------------------------------------
        # STEP 3
        # RETURN RESPONSE
        # -------------------------------------------------

        return {

            "success": True,

            "user": user_name,

            "question": question,

            "answer": answer,

            "graph_context": graph_context
        }


    except HTTPException:

        raise


    except Exception as e:

        print("\n=========================================")
        print("ASK API ERROR")
        print("=========================================")

        print(
            "Error type:",
            type(e).__name__
        )

        print(
            "Error:",
            str(e)
        )


        raise HTTPException(

            status_code=500,

            detail=(
                f"AI answer generation failed: "
                f"{str(e)}"
            )
        )


# =========================================================
# TEST GRAPH DIRECTLY
# =========================================================

@app.get("/debug/user/{user_name}")
def debug_user(user_name: str):

    print("\n=========================================")
    print("DEBUG USER")
    print("=========================================")

    print(
        "Searching:",
        user_name
    )


    try:

        context = get_user_graph_context(
            user_name
        )


        return {

            "user": user_name,

            "found": bool(
                context.strip()
            ),

            "graph_context": context
        }


    except Exception as e:

        print(
            "Debug error:",
            str(e)
        )


        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# =========================================================
# SHUTDOWN
# =========================================================

@app.on_event("shutdown")
def shutdown_event():

    try:

        driver.close()

        print(
            "Neo4j driver closed."
        )

    except Exception as e:

        print(
            "Error closing Neo4j driver:",
            e
        )