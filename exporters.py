from pathlib import Path
from uuid import uuid4

from fpdf import FPDF
from PIL import Image

from .config import get_settings


def _pdf_text(value: str) -> str:

    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "•": "*",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    return (
        value
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


class ComicPDF(FPDF):

    def header(self) -> None:

        if self.page_no() > 1:

            self.set_font(
                "Helvetica",
                "B",
                10,
            )

            self.set_text_color(
                100,
                100,
                100,
            )

            self.cell(
                0,
                7,
                "ComicCraft",
                align="R",
            )

            self.ln(5)


def _absolute_image_path(
    image_url: str,
) -> Path:

    settings = get_settings()

    relative = image_url.replace(
        "/static/",
        "",
        1,
    )

    path = settings.static_dir / relative

    if not path.exists():

        raise FileNotFoundError(
            f"Panel image not found: {path}"
        )

    return path


def save_pdf(
    title: str,
    layout: list[dict],
) -> str:

    settings = get_settings()

    pdf = ComicPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for item in layout:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        pdf.set_text_color(
            25,
            25,
            35,
        )

        pdf.multi_cell(
            0,
            10,
            _pdf_text(
                f"Panel {item['panel_number']}: "
                f"{item['title']}"
            ),
        )

        pdf.ln(3)

        image_path = _absolute_image_path(
            item["image_url"]
        )

        with Image.open(image_path) as img:
            width, height = img.size

        max_width = 170
        max_height = 100

        ratio = min(
            max_width / width,
            max_height / height,
        )

        display_width = width * ratio
        display_height = height * ratio

        x = (
            210 - display_width
        ) / 2

        pdf.image(
            str(image_path),
            x=x,
            y=pdf.get_y(),
            w=display_width,
            h=display_height,
        )

        pdf.set_y(
            pdf.get_y()
            + display_height
            + 8
        )

        pdf.set_font(
            "Helvetica",
            "I",
            10,
        )

        pdf.set_text_color(
            80,
            80,
            80,
        )

        pdf.multi_cell(
            0,
            6,
            _pdf_text(
                item["scene_description"]
            ),
        )

        pdf.ln(3)

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.set_text_color(
            25,
            25,
            35,
        )

        pdf.multi_cell(
            0,
            6,
            "Caption",
        )

        pdf.set_font(
            "Helvetica",
            size=10,
        )

        pdf.multi_cell(
            0,
            6,
            _pdf_text(
                item["caption"]
            )
            if item["caption"]
            else "-",
        )

        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            "Narration",
        )

        pdf.set_font(
            "Helvetica",
            size=10,
        )

        pdf.multi_cell(
            0,
            6,
            _pdf_text(
                item["narration"]
            )
            if item["narration"]
            else "-",
        )

        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            "Dialogue",
        )

        pdf.set_font(
            "Helvetica",
            size=10,
        )

        pdf.multi_cell(
            0,
            6,
            _pdf_text(
                item["dialogue"]
            )
            if item["dialogue"]
            else "-",
        )

    filename = (
        f"comic_{uuid4().hex[:10]}.pdf"
    )

    path = settings.exports_dir / filename

    pdf.output(str(path))

    return f"/static/exports/{filename}"