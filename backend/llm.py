import os
import json

from dotenv import load_dotenv
from groq import Groq

from models import GraphData


load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# raw text leta hai
# GRAPH EXTRACTION

def extract_graph_data(text: str) -> GraphData:

    response = client.chat.completions.create(

        model = "openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",

                "content": """
You are a Knowledge Graph extraction system.

Extract entities and relationships
from the user's text.

Return ONLY valid JSON.

The JSON must follow this exact structure:

{
    "entities": [
        {
            "name": "entity name",
            "type": "entity type"
        }
    ],
    "relationships": [
        {
            "source": "source entity",
            "type": "relationship type",
            "target": "target entity"
        }
    ]
}

Entity types:

User,
Skill,
Company,
Topic,
Technology

Relationship types:

KNOWS,
WORKS_AT,
LEARNING,
USES

Do not add explanations.

Do not use Markdown.

Return JSON only.
"""
            },

            {
                "role": "user",
                "content": text
            }
        ],

        temperature=0,

        response_format={
            "type": "json_object"
        }
    )

    raw_output = response.choices[0].message.content

    print("\nRAW LLM OUTPUT:")
    print(raw_output)

    #json ko python object me convert
    data = json.loads(raw_output)
    #Pydantic validation
    return GraphData(**data)


# GRAPH RAG - ANSWER GENERATION


def generate_answer(
    question: str,
    graph_context: str
):

    prompt = f"""
You are a helpful AI assistant.

Answer the user's question using ONLY
the provided Knowledge Graph context.

Knowledge Graph Context:

{graph_context}


User Question:

{question}


Instructions:

1. Use the graph context to answer.
2. Do not invent information.
3. If the answer is not available in the
   graph context, say:

   "The information is not available
   in the knowledge graph."

4. Give a clear and concise answer.
"""

    response = client.chat.completions.create(

        model = "openai/gpt-oss-20b",

        messages=[

            {
                "role": "system",

                "content": """
You answer questions using
Knowledge Graph context.
"""
            },

            {
                "role": "user",

                "content": prompt
            }
        ],

        temperature=0
    )

    return response.choices[0].message.content