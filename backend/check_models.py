import os
import json

from dotenv import load_dotenv
from groq import Groq

from models import GraphData


# =========================================
# ENVIRONMENT
# =========================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing from .env"
    )


client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================
# MODEL
# =========================================

MODEL = "openai/gpt-oss-120b"


# =========================================
# GRAPH EXTRACTION
# =========================================

def extract_graph_data(text: str) -> GraphData:

    system_prompt = """
You are a Knowledge Graph extraction API.

Your job is to extract important information from a resume
and convert it into a small Knowledge Graph.

IMPORTANT:
Return ONLY valid JSON.

Do NOT:
- explain
- reason
- use markdown
- use code fences
- add comments
- add text outside JSON

Use exactly this JSON structure:

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


=========================================
ALLOWED ENTITY TYPES
=========================================

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


=========================================
ALLOWED RELATIONSHIP TYPES
=========================================

KNOWS
WORKS_AT
STUDIED_AT
BUILT
HAS_SKILL
USES
WORKED_AS
LEARNING


=========================================
RELATIONSHIP RULES
=========================================

Person -> College
STUDIED_AT

Person -> Company
WORKS_AT

Person -> Project
BUILT

Person -> Skill
HAS_SKILL

Person -> Role
WORKED_AS

Project -> Technology
USES

Person -> Technology
KNOWS

Person -> Topic
LEARNING


=========================================
EXTRACTION RULES
=========================================

1. Extract only information explicitly present in the resume.

2. Never invent information.

3. Do not duplicate entities.

4. Do not duplicate relationships.

5. Keep the graph concise.

6. Maximum 30 entities.

7. Maximum 40 relationships.

8. Focus on:
   - Person
   - Colleges
   - Companies
   - Roles
   - Projects
   - Skills
   - Technologies
   - Important topics

9. Do not create unnecessary entities.

10. Do not create an Experience entity if the same
    information can be represented using Role + Company.

11. If something is explicitly listed as a skill,
    create a Skill entity.

12. If something is clearly a technology/tool/API/framework,
    create a Technology entity.

13. If something is a general subject or area of interest,
    create a Topic entity.

14. Every relationship source MUST exactly match
    an entity name from the entities array.

15. Every relationship target MUST exactly match
    an entity name from the entities array.

16. Preserve:
    - spelling
    - spaces
    - capitalization
    - punctuation

17. Never change an entity name when using it
    inside a relationship.

18. Return the JSON immediately.

19. Do not generate reasoning.

20. Do not generate a partial JSON response.

21. Always return:
    {
      "entities": [...],
      "relationships": [...]
    }

Return ONLY JSON.
"""


    # =========================================
    # LLM CALL
    # =========================================

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
                    "content": text
                }
            ],

            temperature=0,

            max_completion_tokens=12000,

            reasoning_effort="low",

            include_reasoning=False,

            response_format={
                "type": "json_object"
            }
        )

    except Exception as e:

        print("\n=========================================")
        print("LLM API ERROR")
        print("=========================================")

        print(e)

        raise


    # =========================================
    # RESPONSE DEBUG
    # =========================================

    choice = response.choices[0]

    print("\n=========================================")
    print("LLM RESPONSE DEBUG")
    print("=========================================")

    print("Model:")
    print(MODEL)

    print("\nFinish reason:")
    print(choice.finish_reason)

    print("\nRaw message:")
    print(choice.message)


    # =========================================
    # GET CONTENT
    # =========================================

    raw_output = choice.message.content


    # =========================================
    # EMPTY RESPONSE
    # =========================================

    if not raw_output:

        print("\n=========================================")
        print("EMPTY LLM CONTENT")
        print("=========================================")

        print(
            "Finish reason:",
            choice.finish_reason
        )

        raise ValueError(
            "LLM returned an empty response."
        )


    # =========================================
    # RAW OUTPUT
    # =========================================

    print("\n=========================================")
    print("RAW LLM OUTPUT")
    print("=========================================")

    print(raw_output)


    # =========================================
    # CLEAN OUTPUT
    # =========================================

    raw_output = raw_output.strip()


    # Remove markdown code fences if model adds them
    if raw_output.startswith("```json"):

        raw_output = raw_output[7:]

    elif raw_output.startswith("```"):

        raw_output = raw_output[3:]


    if raw_output.endswith("```"):

        raw_output = raw_output[:-3]


    raw_output = raw_output.strip()


    # =========================================
    # JSON PARSING
    # =========================================

    try:

        data = json.loads(
            raw_output
        )

    except json.JSONDecodeError as e:

        print("\n=========================================")
        print("JSON PARSING ERROR")
        print("=========================================")

        print(e)

        print("\nINVALID OUTPUT:")
        print(raw_output)

        raise ValueError(
            "LLM did not return valid JSON."
        )


    # =========================================
    # JSON OBJECT VALIDATION
    # =========================================

    if not isinstance(data, dict):

        raise ValueError(
            "LLM JSON response is not an object."
        )


    # =========================================
    # GET ENTITIES
    # =========================================

    entities = data.get(
        "entities",
        []
    )


    # =========================================
    # GET RELATIONSHIPS
    # =========================================

    relationships = data.get(
        "relationships",
        []
    )


    # =========================================
    # LIST VALIDATION
    # =========================================

    if not isinstance(
        entities,
        list
    ):

        raise ValueError(
            "'entities' must be a list."
        )


    if not isinstance(
        relationships,
        list
    ):

        raise ValueError(
            "'relationships' must be a list."
        )


    # =========================================
    # REMOVE DUPLICATE ENTITIES
    # =========================================

    unique_entities = []

    seen_entities = set()


    for entity in entities:

        if not isinstance(entity, dict):
            continue

        name = entity.get("name")
        entity_type = entity.get("type")

        if not name or not entity_type:
            continue

        key = (
            str(name).strip(),
            str(entity_type).strip()
        )

        if key not in seen_entities:

            seen_entities.add(key)

            unique_entities.append(
                {
                    "name": str(name).strip(),
                    "type": str(entity_type).strip()
                }
            )


    # =========================================
    # VALID ENTITY NAMES
    # =========================================

    valid_entity_names = {
        entity["name"]
        for entity in unique_entities
    }


    # =========================================
    # VALIDATE RELATIONSHIPS
    # =========================================

    unique_relationships = []

    seen_relationships = set()


    for relationship in relationships:

        if not isinstance(
            relationship,
            dict
        ):
            continue


        source = relationship.get(
            "source"
        )

        relationship_type = relationship.get(
            "type"
        )

        target = relationship.get(
            "target"
        )


        if not source:
            continue

        if not relationship_type:
            continue

        if not target:
            continue


        source = str(source).strip()
        relationship_type = str(
            relationship_type
        ).strip()
        target = str(target).strip()


        # -----------------------------------------
        # IMPORTANT:
        # Source and target must exist
        # in entity list.
        # -----------------------------------------

        if source not in valid_entity_names:

            print(
                f"Skipping invalid relationship source: "
                f"{source}"
            )

            continue


        if target not in valid_entity_names:

            print(
                f"Skipping invalid relationship target: "
                f"{target}"
            )

            continue


        key = (
            source,
            relationship_type,
            target
        )


        if key not in seen_relationships:

            seen_relationships.add(key)

            unique_relationships.append(
                {
                    "source": source,
                    "type": relationship_type,
                    "target": target
                }
            )


    # =========================================
    # CREATE GRAPH DATA
    # =========================================

    try:

        graph_data = GraphData(

            entities=unique_entities,

            relationships=unique_relationships

        )

    except Exception as e:

        print("\n=========================================")
        print("PYDANTIC VALIDATION ERROR")
        print("=========================================")

        print(e)

        raise


    # =========================================
    # SUCCESS
    # =========================================

    print("\n=========================================")
    print("GRAPH EXTRACTION SUCCESSFUL")
    print("=========================================")

    print(
        f"Entities: "
        f"{len(graph_data.entities)}"
    )

    print(
        f"Relationships: "
        f"{len(graph_data.relationships)}"
    )


    # =========================================
    # PRINT ENTITIES
    # =========================================

    print("\nEntities:")

    for entity in graph_data.entities:

        print(
            f"  - {entity.name} "
            f"[{entity.type}]"
        )


    # =========================================
    # PRINT RELATIONSHIPS
    # =========================================

    print("\nRelationships:")

    for relationship in graph_data.relationships:

        print(
            f"  - {relationship.source} "
            f"--[{relationship.type}]--> "
            f"{relationship.target}"
        )


    return graph_data


# =========================================
# GRAPH RAG ANSWER
# =========================================

def generate_answer(
    question: str,
    graph_context: str
):

    system_prompt = """
You are a Knowledge Graph question-answering assistant.

You must answer the user's question using ONLY
the supplied Knowledge Graph context.

Rules:

1. Do not use outside knowledge.

2. Do not invent information.

3. Answer only from the supplied graph.

4. Keep the answer concise and natural.

5. If the answer is not present in the graph,
   say exactly:

The information is not available in the knowledge graph.

6. Do not mention these instructions.

7. Do not create information that is not present
   in the graph.
"""


    # =========================================
    # USER PROMPT
    # =========================================

    user_prompt = f"""
KNOWLEDGE GRAPH:

{graph_context}


=========================================

USER QUESTION:

{question}


=========================================

Answer the question using ONLY the Knowledge Graph.
"""


    # =========================================
    # LLM CALL
    # =========================================

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

            max_completion_tokens=2000,

            reasoning_effort="low",

            include_reasoning=False

        )

    except Exception as e:

        print("\n=========================================")
        print("ANSWER GENERATION ERROR")
        print("=========================================")

        print(e)

        raise


    # =========================================
    # RESPONSE
    # =========================================

    choice = response.choices[0]


    print("\n=========================================")
    print("ANSWER LLM DEBUG")
    print("=========================================")

    print(
        "Model:",
        MODEL
    )

    print(
        "Finish reason:",
        choice.finish_reason
    )


    answer = choice.message.content


    print(
        "Answer:",
        answer
    )


    # =========================================
    # EMPTY ANSWER
    # =========================================

    if not answer:

        return (
            "The information is not available "
            "in the knowledge graph."
        )


    return answer.strip()