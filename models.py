from typing import Literal

from pydantic import BaseModel, Field, field_validator


Tone = Literal[
    "light-hearted",
    "dramatic",
    "poetic",
    "funny",
]

ArtStyle = Literal[
    "anime",
    "pixel art",
    "comic book",
    "realistic",
]


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        ...,
        min_length=10,
        max_length=1200,
    )

    character_name: str = Field(
        ...,
        min_length=1,
        max_length=60,
    )

    setting: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    tone: Tone = "light-hearted"

    art_style: ArtStyle = "comic book"

    @field_validator(
        "story_prompt",
        "character_name",
        "setting",
    )
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = " ".join(value.strip().split())

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class ComicPanel(BaseModel):
    panel_number: int = Field(..., ge=1, le=5)

    title: str = Field(
        ...,
        min_length=1,
        max_length=120,
    )

    scene_description: str = Field(
        ...,
        min_length=1,
        max_length=800,
    )

    image_prompt: str = Field(
        ...,
        min_length=1,
        max_length=1200,
    )


class StoryPanel(BaseModel):
    panel_number: int = Field(..., ge=1, le=5)

    caption: str = Field(
        default="",
        max_length=500,
    )

    narration: str = Field(
        default="",
        max_length=1500,
    )

    dialogue: str = Field(
        default="",
        max_length=1000,
    )


class ComicLayoutItem(BaseModel):
    panel_number: int
    title: str
    image_url: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str


class ComicResponse(BaseModel):
    title: str
    panels: list[ComicLayoutItem]
    pdf_url: str