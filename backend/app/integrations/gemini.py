import json

from google import genai
from google.genai import types

from app.core.config import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)


TICKET_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "category": {
            "type": "STRING",
            "enum": [
                "hardware",
                "software",
                "network",
                "access",
                "other",
            ],
        },
        "priority": {
            "type": "STRING",
            "enum": [
                "low",
                "medium",
                "high",
                "critical",
            ],
        },
        "justification": {
            "type": "STRING",
        },
    },
    "required": [
        "category",
        "priority",
        "justification",
    ],
}


def analyze_ticket(title: str, description: str) -> dict:
    prompt = f"""
Você é um especialista em triagem de chamados de suporte técnico.

Analise o chamado abaixo e classifique-o.

Título: {title}

Descrição: {description}

Regras:
- category deve ser hardware, software, network, access ou other.
- priority deve ser low, medium, high ou critical.
- critical deve ser usado somente quando houver impacto muito grave,
  como indisponibilidade generalizada ou risco significativo.
- justification deve explicar brevemente a classificação.
- Não invente informações que não estejam no chamado.
- Responda exclusivamente no formato JSON solicitado.
"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TICKET_SCHEMA,
            temperature=0.2,
        ),
    )

    if not response.text:
        raise ValueError("O Gemini retornou uma resposta vazia.")

    return json.loads(response.text)
