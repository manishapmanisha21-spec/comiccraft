import re
from uuid import uuid4

from PIL import Image

from .config import get_settings


def _safe_filename(value: str) -> str:
    cleaned = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        value,
    )

    cleaned = cleaned.strip("_")

    return cleaned[:60] or "panel"


def _generate_hf(prompt: str) -> Image.Image:

    from huggingface_hub import InferenceClient

    settings = get_settings()

    if not settings.hf_token:
        raise RuntimeError(
            "HF_TOKEN is not configured. "
            "Add it to your .env file."
        )

    client = InferenceClient(
        provider=settings.hf_provider,
        api_key=settings.hf_token,
    )

    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
    )

    if not isinstance(image, Image.Image):
        raise RuntimeError(
            "Hugging Face did not return a PIL image."
        )

    return image.convert("RGB")


def _generate_local(prompt: str) -> Image.Image:

    try:
        import torch

        from diffusers import StableDiffusionPipeline

    except ImportError as exc:

        raise RuntimeError(
            "Local Diffusers backend requires "
            "torch and diffusers."
        ) from exc

    settings = get_settings()

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    dtype = (
        torch.float16
        if device == "cuda"
        else torch.float32
    )

    pipe = StableDiffusionPipeline.from_pretrained(
        settings.local_image_model,
        torch_dtype=dtype,
    )

    pipe = pipe.to(device)

    result = pipe(
        prompt,
        num_inference_steps=25,
        guidance_scale=7.0,
        height=768,
        width=512,
    )

    return result.images[0].convert("RGB")


def generate_image(
    image_prompt: str,
    panel_number: int,
) -> str:

    settings = get_settings()

    visual_prompt = (
        f"{image_prompt}. "
        "Clean comic illustration, "
        "strong composition, "
        "readable visual storytelling, "
        "consistent character design, "
        "no speech bubbles, "
        "no written words, "
        "no watermark."
    )

    backend = settings.image_backend.lower()

    if backend == "local":

        image = _generate_local(
            visual_prompt
        )

    elif backend == "hf":

        image = _generate_hf(
            visual_prompt
        )

    else:

        raise RuntimeError(
            "IMAGE_BACKEND must be either "
            "'hf' or 'local'."
        )

    filename = (
        f"panel_{panel_number}_"
        f"{_safe_filename(str(uuid4()))}.png"
    )

    path = settings.panels_dir / filename

    image.save(
        path,
        format="PNG",
        optimize=True,
    )

    return f"/static/panels/{filename}"