from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from app.config import get_settings
from app.exporters import save_pdf
from app.layout_builder import build_comic_layout
from app.main import app


client = TestClient(app)


def test_homepage():

    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_prompt_validation():

    payload = {
        "story_prompt": "short",

        "character_name": "Finn",

        "setting": "forest",

        "tone": "funny",

        "art_style": "comic book",
    }

    response = client.post(
        "/generate-comic/json",
        json=payload,
    )

    assert response.status_code == 422


def test_layout_and_pdf_export(
    tmp_path,
    monkeypatch,
):

    settings = get_settings()

    monkeypatch.setattr(
        settings,
        "exports_dir",
        tmp_path,
    )

    monkeypatch.setattr(
        settings,
        "static_dir",
        tmp_path / "static",
    )

    monkeypatch.setattr(
        settings,
        "panels_dir",
        tmp_path / "static" / "panels",
    )

    settings.panels_dir.mkdir(
        parents=True
    )

    image_paths = []

    for i in range(1, 6):

        filename = f"panel_{i}.png"

        path = (
            settings.panels_dir
            / filename
        )

        Image.new(
            "RGB",
            (512, 384),
            "white",
        ).save(path)

        image_paths.append(
            f"/static/panels/{filename}"
        )

    outline = [
        {
            "panel_number": i,
            "title": f"Panel {i}",
            "scene_description": "A scene",
            "image_prompt": "A comic scene",
        }

        for i in range(1, 6)
    ]

    story = [
        {
            "panel_number": i,
            "caption": "Caption",
            "narration": "Narration",
            "dialogue": "Finn: Hello!",
        }

        for i in range(1, 6)
    ]

    layout = build_comic_layout(
        outline,
        story,
        image_paths,
    )

    assert len(layout) == 5

    pdf_url = save_pdf(
        "Test Comic",
        layout,
    )

    assert pdf_url.startswith(
        "/static/exports/"
    )

    assert (
        settings.exports_dir
        / Path(pdf_url).name
    ).exists()