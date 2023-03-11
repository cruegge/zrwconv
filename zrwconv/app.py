from datetime import datetime
from importlib import resources
import traceback

from aiohttp import web
from asyncio import get_event_loop
from mako.lookup import TemplateLookup

from .converter import convert_file


class TemplateRenderer:
    def __init__(self, path):
        self._lookup = TemplateLookup(directories=[path])

    def __call__(self, template, **kwargs):
        return web.Response(
            text=self._lookup.get_template(template).render(**kwargs),
            content_type="text/html",
        )


def render(request, *args, **kwargs):
    return request.app["renderer"](*args, **kwargs)


routes = web.RouteTableDef()


@routes.get("/")
async def index(request):
    return render(request, "index.html")


@routes.post("/convert")
async def convert(request: web.Request):
    try:
        data = await request.post()
        # TODO Handle request errors (missing file, etc)
        fileobj = data["file"].file
        # fileobj is a TemporaryFile, which at least on Linux is a nameless inode. The name
        # is simply the fd (integer). Later, some mamooth function calls dirname() on it,
        # which of course fails. Setting the name to None seems to work, however.
        fileobj.raw.name = None
        body, warnings = await get_event_loop().run_in_executor(
            None, lambda: convert_file(fileobj)
        )
    except Exception as error:
        return render(
            request,
            "conversion_error.html",
            error=error,
            backtrace=traceback.format_exc(),
        )
    timestamp = datetime.now().strftime("%F_%H-%M")
    return render(
        request,
        "result.html",
        body=body,
        warnings=warnings,
        download_name=f"zrw-artikel_konvertiert_{timestamp}.html",
    )


async def static_route(app):
    with resources.path("zrwconv", "static") as path:
        app.add_routes([web.static("/static", path)])
        yield


async def templates(app):
    with resources.path("zrwconv", "templates") as path:
        app["renderer"] = TemplateRenderer(path)
        yield


async def create_app(*_):
    app = web.Application()
    app.add_routes(routes)
    app.cleanup_ctx.append(static_route)
    app.cleanup_ctx.append(templates)
    return app
