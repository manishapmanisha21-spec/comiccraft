# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application that turns a user's
story idea into a five-panel comic.

The project pipeline is:

Prompt
↓
Gemini structured outline
↓
Gemini narration/dialogue
↓
AI panel images
↓
Comic layout
↓
PDF export

## Features

- Story prompt
- Character name
- Setting
- Story tone
- Art style
- Five-panel comic
- AI-generated narration
- AI-generated dialogue
- AI-generated images
- Comic preview
- PDF download
- JSON API
- Image testing endpoint
- Health endpoint

## Project Structure

```text
ComicCraft/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   ├── gemini_flash.py
│   ├── gemini_pro.py
│   ├── image_generator.py
│   ├── layout_builder.py
│   └── exporters.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── comic_preview.html
│   ├── export_success.html
│   └── error.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── panels/
│   └── exports/
│
├── tests/
│   └── test_app.py
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md