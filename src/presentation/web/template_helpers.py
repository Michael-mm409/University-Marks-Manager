from fastapi import Request
from fastapi.responses import HTMLResponse


def _render(request: Request, template: str, context: dict) -> HTMLResponse:
    """
    Helper to render a template with context.

    Args:
        request (Request): The incoming HTTP request.
        template (str): Template filename.
        context (dict): Context variables for the template.

    Returns:
        HTMLResponse: Rendered HTML response.
    """
    env = request.app.state.jinja_env
    tpl = env.get_template(template)
    return HTMLResponse(tpl.render(**context))

__all__ = ["_render"]