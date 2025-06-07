""" This module defines the dynamic router for handling dynamic path requests. """

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from server.server_config import templates
from server.server_utils import limiter

router = APIRouter()


@router.get("/{full_path:path}")
async def catch_all(request: Request, full_path: str) -> HTMLResponse:
    """
    Render a page with a Git URL based on the provided path.

    This endpoint catches all GET requests with a dynamic path, constructs a Git URL
    using the `full_path` parameter, and renders the `git.jinja` template with that URL.

    Parameters
    ----------
    request : Request
        The incoming request object, which provides context for rendering the response.
    full_path : str
        The full path extracted from the URL, which is used to build the Git URL.

    Returns
    -------
    HTMLResponse
        An HTML response containing the rendered template, with the Git URL
        and other default parameters such as loading state and file size.
    """
    return templates.TemplateResponse(
        "git.jinja",
        {
            "request": request,
            "repo_url": full_path,
            "loading": True,
            "default_file_size": 243,
        },
    )
