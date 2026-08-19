import os
import json

from dotenv import load_dotenv
from groq import Groq

from models import GraphData


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from .env")


client = Groq(api_key=GROQ_API_KEY)


# =========================================================
# MODEL
# =========================================================

MODEL = "openai/gpt-oss-120b"


# =========================================================
# HELPER
# =========================================================

def get_value(obj, key, index=None, default=None):
    """
    Safely read value from:
    - Pydantic object
    - dict
    - tuple/list
    """

    # Pydantic / normal object
    if hasattr(obj, key):
        return getattr(obj, key)

    # Dictionary
    if isinstance(obj, dict):
        return obj.get(key, default)

    # Tuple / list
    if isinstance(obj, (tuple, list)) and index is not None:
        if len(obj) > index:
            return obj[index]

    return default


# =========================================================
# GRAPH EXTRACTION
# =========================================================

def extract_graph_data(text: str) -> GraphData:

    print("\n=========================================")
    print("EXTRACTING GRAPH DATA")
    print("=========================================")

    if not text or not text.strip():
        raise ValueError("Resume text is empty.")

    # Keep request safely below Groq TPM limit
    # Your previous request was 9098 tokens against 8000 TPM.
    MAX_CHARS = 18000

    if len(text) > MAX_CHARS:
        print(
            f"Resume text is {len(text)} characters. "
            f"Truncating to {MAX_CHARS} characters."
        )

        text = text[:MAX_CHARS]

    system_prompt = """
You are a Knowledge Graph extraction API.

Extract structured information from the user's resume.

RETURN ONLY VALID JSON.

Do not explain.
Do not use markdown.
Do not add text outside JSON.

Use exactly this structure:

{
  "entities": [
    {
      "name": "string",
      "type": "string"
    }
  ],
  "relationships": [
    {
      "source": "string",
      "type": "string",
      "target": "string"
    }
  ]
}

Allowed entity types:

User
Education
College
Company
Experience
Project
Skill
Technology
Topic
Role

Allowed relationship types:

KNOWS
WORKS_AT
STUDIED_AT
BUILT
HAS_SKILL
USES
WORKED_AS
LEARNING

Rules:

1. Extract only information explicitly present in the resume.
2. Never invent information.
3. Do not duplicate entities.
4. Keep names clean and concise.
5. Always return entities and relationships.
6. The main person must be an entity of type User.
7. Do not create multiple User entities for the same person.
8. Technologies such as React, Node.js, MongoDB, FastAPI,
   Neo4j, Groq, LangChain etc. should normally be Technology.
9. Job titles should normally be Role.
10. Projects should be Project.
11. Colleges/universities should be College.
12. Companies should be Company.
13. Skills explicitly mentioned should be Skill.
14. Learning areas should be Topic.

Relationship rules:

Person -> college = STUDIED_AT
Person -> company = WORKS_AT
Person -> project = BUILT
Person -> skill = HAS_SKILL
Person -> role = WORKED_AS
Project -> technology = USES
Person -> technology = KNOWS
Person -> learning topic = LEARNING

IMPORTANT:

The graph will later be used by another AI assistant
to answer questions about the person.

Therefore extract useful resume information including:

- name
- education
- college
- degree
- CGPA
- companies
- internship
- job roles
- projects
- programming languages
- frameworks
- databases
- APIs
- AI/ML technologies
- tools
- relevant skills
- certifications
- achievements
- learning topics

Return ONLY JSON.
"""

    user_prompt = f"""
Extract the knowledge graph from this resume:

---------------- RESUME ----------------

{text}

-------------- END RESUME --------------

Return only JSON.
"""

    # =====================================================
    # GROQ CALL
    # =====================================================

    try:

        response = client.chat.completions.create(
            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=0,

            max_tokens=3500,

            response_format={
                "type": "json_object"
            }
        )

    except Exception as e:

        print("\n=========================================")
        print("GROQ EXTRACTION ERROR")
        print("=========================================")

        print(type(e).__name__)
        print(str(e))

        raise


    # =====================================================
    # RESPONSE
    # =====================================================

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Groq returned empty response.")


    print("\n=========================================")
    print("RAW GRAPH JSON")
    print("=========================================")

    print(content)


    # =====================================================
    # PARSE JSON
    # =====================================================

    try:

        data = json.loads(content)

    except json.JSONDecodeError as e:

        print("\nJSON ERROR:")
        print(e)

        print("\nRAW OUTPUT:")
        print(content)

        raise ValueError(
            "Groq did not return valid JSON."
        )


    if not isinstance(data, dict):

        raise ValueError(
            "Groq response must be a JSON object."
        )


    entities = data.get("entities", [])
    relationships = data.get("relationships", [])


    if not isinstance(entities, list):
        entities = []

    if not isinstance(relationships, list):
        relationships = []


    # =====================================================
    # CLEAN ENTITIES
    # =====================================================

    cleaned_entities = []

    seen_entities = set()

    for entity in entities:

        name = get_value(
            entity,
            "name",
            index=0
        )

        entity_type = get_value(
            entity,
            "type",
            index=1
        )

        if not name or not entity_type:
            continue

        name = str(name).strip()
        entity_type = str(entity_type).strip()

        key = name.lower()

        if key in seen_entities:
            continue

        seen_entities.add(key)

        cleaned_entities.append(
            {
                "name": name,
                "type": entity_type
            }
        )


    # =====================================================
    # CLEAN RELATIONSHIPS
    # =====================================================

    cleaned_relationships = []

    seen_relationships = set()

    for relationship in relationships:

        source = get_value(
            relationship,
            "source",
            index=0
        )

        relationship_type = get_value(
            relationship,
            "type",
            index=1
        )

        target = get_value(
            relationship,
            "target",
            index=2
        )

        if not source or not relationship_type or not target:
            continue

        source = str(source).strip()
        relationship_type = str(
            relationship_type
        ).strip().upper()

        target = str(target).strip()

        key = (
            source.lower(),
            relationship_type,
            target.lower()
        )

        if key in seen_relationships:
            continue

        seen_relationships.add(key)

        cleaned_relationships.append(
            {
                "source": source,
                "type": relationship_type,
                "target": target
            }
        )


    # =====================================================
    # CREATE PYDANTIC GRAPH DATA
    # =====================================================

    try:

        graph_data = GraphData(
            entities=cleaned_entities,
            relationships=cleaned_relationships
        )

    except Exception as e:

        print("\n=========================================")
        print("GRAPH DATA VALIDATION ERROR")
        print("=========================================")

        print(e)

        print("\nEntities:")
        print(cleaned_entities)

        print("\nRelationships:")
        print(cleaned_relationships)

        raise


    # =====================================================
    # DEBUG
    # =====================================================

    print("\n=========================================")
    print("GRAPH EXTRACTION SUCCESSFUL")
    print("=========================================")

    print(
        "Entities:",
        len(graph_data.entities)
    )

    print(
        "Relationships:",
        len(graph_data.relationships)
    )


    for entity in graph_data.entities:

        name = get_value(
            entity,
            "name",
            index=0
        )

        entity_type = get_value(
            entity,
            "type",
            index=1
        )

        print(
            f"ENTITY: {name} [{entity_type}]"
        )


    for relationship in graph_data.relationships:

        source = get_value(
            relationship,
            "source",
            index=0
        )

        relation = get_value(
            relationship,
            "type",
            index=1
        )

        target = get_value(
            relationship,
            "target",
            index=2
        )

        print(
            f"RELATIONSHIP: "
            f"{source} --{relation}--> {target}"
        )


    return graph_data


# =========================================================
# GRAPH RAG ANSWER
# =========================================================

def generate_answer(
    question: str,
    graph_context: str
):

    print("\n=========================================")
    print("GENERATING GRAPH RAG ANSWER")
    print("=========================================")

    print("Question:", question)

    print("\nGraph Context:")
    print(graph_context)


    # =====================================================
    # NO CONTEXT
    # =====================================================

    if not graph_context or not graph_context.strip():

        return (
            "I couldn't find this information in "
            "Adarsh's profile."
        )


    system_prompt = """
You are Adarsh Singh's personal AI assistant.

Your job is to answer questions about Adarsh.

Use ONLY the information provided in the profile context.

Rules:

1. Never invent information.
2. Never use outside knowledge.
3. Answer naturally like a chatbot.
4. Be concise but useful.
5. If the answer is present, answer directly.
6. If the answer is not present, say:
   "I couldn't find this information in Adarsh's profile."
7. Do not mention database, Neo4j, graph, retrieval,
   context or internal system details unless the user
   specifically asks about the technology.
8. If the question asks about skills, list the relevant skills.
9. If the question asks about projects, mention projects
   and technologies available in the context.
10. If the question asks about education, provide the
    available education details.
11. If the question asks about experience, provide the
    available company, role and internship details.
"""


    user_prompt = f"""
PROFILE INFORMATION:

{graph_context}


USER QUESTION:

{question}


Answer the user's question about Adarsh.
"""


    # =====================================================
    # GROQ ANSWER CALL
    # =====================================================

    try:

        response = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=0.2,

            max_tokens=800
        )

    except Exception as e:

        print("\n=========================================")
        print("GROQ ANSWER ERROR")
        print("=========================================")

        print(type(e).__name__)
        print(str(e))

        raise


    # =====================================================
    # GET ANSWER
    # =====================================================

    answer = response.choices[0].message.content


    if not answer:

        return (
            "I couldn't generate an answer right now."
        )


    answer = answer.strip()


    print("\n=========================================")
    print("FINAL ANSWER")
    print("=========================================")

    print(answer)


    return answer


# =========================================================
# STREAMING ANSWER
# =========================================================

def generate_answer_stream(
    question: str,
    graph_context: str
):

    if not graph_context or not graph_context.strip():

        yield (
            "I couldn't find this information "
            "in Adarsh's profile."
        )

        return


    system_prompt = """
You are Adarsh Singh's personal AI assistant.

Answer questions about Adarsh using ONLY
the supplied profile information.

Do not invent information.

Do not mention internal database or graph details.

Give a natural concise answer.

If information is unavailable, say:

I couldn't find this information in Adarsh's profile.
"""


    user_prompt = f"""
PROFILE:

{graph_context}


QUESTION:

{question}
"""


    try:

        stream = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=0.2,

            max_tokens=800,

            stream=True
        )


        for chunk in stream:

            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                yield content


    except Exception as e:

        print("\n=========================================")
        print("STREAM ERROR")
        print("=========================================")

        print(type(e).__name__)
        print(str(e))

        yield (
            "Sorry, I couldn't generate the answer "
            "right now."
        )