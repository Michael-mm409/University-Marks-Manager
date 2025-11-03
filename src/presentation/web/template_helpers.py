from fastapi import Request
from fastapi.responses import HTMLResponse

from .types import TemplateContext


def _render(request: Request, template: str, context: TemplateContext) -> HTMLResponse:
    """Helper to render a template with context.

    Args:
        request (Request): The incoming HTTP request.
        template (str): Template filename.
        context (TemplateContext): Context variables for the template.

    Returns:
        HTMLResponse: Rendered HTML response.
    """
    env = request.app.state.jinja_env
    tpl = env.get_template(template)
    # Always include request in the template context so base layout and
    # components can access session and other request-scoped data.
    return HTMLResponse(tpl.render(request=request, **context))


__all__ = ["_render"]