import json

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from .config import get_settings
from .models import PromptRequest, StoryPanel


class StoryResponse(BaseModel):
    panels: list[StoryPanel] = Field(
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


def generate_story(
    request: PromptRequest,
    outline: list[dict],
) -> list[dict]:

    settings = get_settings()

    outline_json = json.dumps(
        outline,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
Expand the following five-panel comic outline
into polished comic writing.

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

Outline:

{outline_json}

Requirements:

- Return exactly five story panels.
- Keep the same panel order.
- Each panel needs a caption.
- Each panel needs narration.
- Each panel needs dialogue.
- Keep character actions consistent.
- Keep the writing family-friendly.
- Do not create extra panels.
"""

    response = _client().models.generate_content(
        model=settings.gemini_pro_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            max_output_tokens=7000,
            response_mime_type="application/json",
            response_schema=StoryResponse,
        ),
    )

    if not response.text:
        raise RuntimeError(
            "Gemini Pro returned an empty story."
        )

    try:
        data = json.loads(response.text)

        parsed = StoryResponse.model_validate(data)

    except Exception as exc:
        raise RuntimeError(
            f"Could not parse Gemini story: {exc}"
        ) from exc

    panels = sorted(
        parsed.panels,
        key=lambda item: item.panel_number,
    )

    if [p.panel_number for p in panels] != [1, 2, 3, 4, 5]:
        raise RuntimeError(
            "Gemini returned an invalid story sequence."
        )

    return [
        panel.model_dump()
        for panel in panels
    ]