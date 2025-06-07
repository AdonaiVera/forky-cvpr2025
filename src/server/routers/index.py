""" This module defines the FastAPI router for the home page of the application. """

import json
import os
import uuid

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Body, Cookie, Form, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

from server.ai.content_provider import gemini_client
from server.server_config import EXAMPLE_REPOS, templates
from server.server_utils import limiter

router = APIRouter()

# Load environment variables from .env file
load_dotenv()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """
    Render the home page with example repositories and default parameters.

    This endpoint serves the home page of the application, rendering the `index.jinja` template
    and providing it with a list of example repositories and default file size values.

    Parameters
    ----------
    request : Request
        The incoming request object, which provides context for rendering the response.

    Returns
    -------
    HTMLResponse
        An HTML response containing the rendered home page template, with example repositories
        and other default parameters such as file size.
    """
    return templates.TemplateResponse(
        "index.jinja",
        {
            "request": request,
            "examples": EXAMPLE_REPOS,
            "default_file_size": 243,
        },
    )

@router.post("/search_cvpr_papers", response_class=JSONResponse)
@limiter.limit("10/minute")
async def search_cvpr_papers(
    request: Request,
    query: str = Form(...),
) -> JSONResponse:
    """
    Search CVPR 2025 papers based on the provided query.

    This endpoint searches through the CVPR 2025 papers list and returns the top 5 most relevant papers
    that match the query.

    Parameters
    ----------
    request : Request
        The incoming request object
    query : str
        The search query to find relevant papers

    Returns
    -------
    JSONResponse
        A JSON response with the top 5 most relevant papers
    """
    try:
        # Get paper recommendations from Gemini
        papers = await gemini_client.search_cvpr_papers(query)

        if not papers:
            return JSONResponse(content={"papers": []})

        return JSONResponse(content={"papers": papers})

    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
