import logging
from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
)
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .exporters import save_pdf
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .models import PromptRequest


logger = logging.getLogger(__name__)

router = APIRouter()

settings = get_settings()

templates = Jinja2Templates(
    directory=str(
        settings.templates_dir
    )
)


def _request_data(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> PromptRequest:

    return PromptRequest(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )


def _generate_comic(
    request_data: PromptRequest,
) -> tuple[list[dict], str]:

    created_images: list[str] = []

    try:

        outline = generate_outline(
            request_data
        )

        story = generate_story(
            request_data,
            outline,
        )

        for panel in outline:

            created_images.append(
                generate_image(
                    panel["image_prompt"],
                    panel["panel_number"],
                )
            )

        layout = build_comic_layout(
            outline,
            story,
            created_images,
        )

        title = (
            f"{request_data.character_name}"
            "'s Comic Adventure"
        )

        pdf_url = save_pdf(
            title,
            layout,
        )

        return layout, pdf_url

    except Exception:

        for image_url in created_images:

            filename = Path(
                image_url
            ).name

            path = (
                settings.panels_dir
                / filename
            )

            try:

                path.unlink(
                    missing_ok=True
                )

            except OSError:

                logger.warning(
                    "Could not remove "
                    "partial image %s",
                    path,
                )

        raise


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate_form(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):

    try:

        data = _request_data(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style,
        )

        layout, pdf_url = _generate_comic(
            data
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_url": pdf_url,
                "character_name":
                    data.character_name,
            },
        )

    except ValueError as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "message": str(exc)
            },
            status_code=422,
        )

    except Exception as exc:

        logger.exception(
            "Comic generation failed"
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "message": str(exc)
            },
            status_code=500,
        )


@router.post(
    "/generate-comic/json"
)
async def generate_json(
    payload: PromptRequest,
):

    try:

        layout, pdf_url = _generate_comic(
            payload
        )

        return JSONResponse(
            content={
                "title":
                    f"{payload.character_name}"
                    "'s Comic Adventure",

                "panels": layout,

                "pdf_url": pdf_url,
            }
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "JSON comic generation failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post(
    "/test-image"
)
async def test_image(
    prompt: str = Form(...),
):

    if not prompt.strip():

        raise HTTPException(
            status_code=422,
            detail="Prompt cannot be empty.",
        )

    try:

        image_url = generate_image(
            prompt.strip(),
            1,
        )

        return {
            "image_url": image_url
        }

    except Exception as exc:

        logger.exception(
            "Image test failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
    pdf_url: str = "",
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_url": pdf_url
        },
    )


@router.get("/health")
async def health():

    return {
        "status": "ok",

        "gemini_configured":
            bool(settings.gemini_api_key),

        "image_backend":
            settings.image_backend,

        "huggingface_configured":
            bool(settings.hf_token),
    }