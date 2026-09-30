import json

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .config import get_settings
from .models import ComicPanel, PromptRequest


class OutlineResponse(BaseModel):
    panels: list[ComicPanel] = Field(
        min_length=5,
        max_length=5,
    )


def _client() -> genai.Client:
    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it to your .env file."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_outline(
    request: PromptRequest,
) -> list[dict]:

    settings = get_settings()

    prompt = f"""
Create a coherent five-panel comic outline.

Story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:

- Exactly 5 panels.
- Number panels from 1 through 5.
- Give every panel a short title.
- Give every panel a clear scene description.
- Give every panel a detailed image-generation prompt.
- Keep the same main character visually consistent.
- Create a beginning, development, climax and ending.
- Do not put dialogue inside image_prompt.
- Describe visual elements clearly.
"""

    response = _client().models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=5000,
            response_mime_type="application/json",
            response_schema=OutlineResponse,
        ),
    )

    if not response.text:
        raise RuntimeError(
            "Gemini Flash returned an empty outline."
        )

    try:
        data = json.loads(response.text)

        parsed = OutlineResponse.model_validate(data)

    except Exception as exc:
        raise RuntimeError(
            f"Could not parse Gemini outline: {exc}"
        ) from exc

    panels = sorted(
        parsed.panels,
        key=lambda item: item.panel_number,
    )

    if [p.panel_number for p in panels] != [1, 2, 3, 4, 5]:
        raise RuntimeError(
            "Gemini returned an invalid five-panel sequence."
        )

    return [
        panel.model_dump()
        for panel in panels
    ]