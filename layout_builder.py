from .models import ComicLayoutItem


def build_comic_layout(
    outline: list[dict],
    story: list[dict],
    image_paths: list[str],
) -> list[dict]:

    if (
        len(outline) != 5
        or len(story) != 5
        or len(image_paths) != 5
    ):
        raise ValueError(
            "Comic layout requires exactly five "
            "outline items, stories, and images."
        )

    story_by_panel = {
        item["panel_number"]: item
        for item in story
    }

    result: list[dict] = []

    sorted_outline = sorted(
        outline,
        key=lambda item: item["panel_number"],
    )

    for index, panel in enumerate(sorted_outline):

        number = panel["panel_number"]

        story_item = story_by_panel.get(number)

        if not story_item:
            raise ValueError(
                f"Missing story content for panel {number}."
            )

        item = ComicLayoutItem(
            panel_number=number,
            title=panel["title"],
            image_url=image_paths[index],
            scene_description=panel[
                "scene_description"
            ],
            caption=story_item.get(
                "caption",
                "",
            ),
            narration=story_item.get(
                "narration",
                "",
            ),
            dialogue=story_item.get(
                "dialogue",
                "",
            ),
            image_prompt=panel[
                "image_prompt"
            ],
        )

        result.append(
            item.model_dump()
        )

    return result