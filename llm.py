
import os
import json

from dotenv import load_dotenv
from groq import Groq

from models import GraphData


load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def extract_graph_data(text: str) -> GraphData:

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": """
You are a Knowledge Graph extraction system.

Extract entities and relationships from the user's text.

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
User, Skill, Company, Topic, Technology

Relationship types:
KNOWS, WORKS_AT, LEARNING, USES

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


    data = json.loads(raw_output)

    return GraphData(**data)