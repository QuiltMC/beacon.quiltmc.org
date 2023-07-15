import asyncio
import os

import asyncpg
from aiohttp import web


async def signal_handler(request: web.Request) -> web.Response:
    """Handle the signal."""
    pool = request.app["pool"]

    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO signals (signal) VALUES (timezone('utc', now()))")

    return web.Response(text="OK", status=200)


async def main(loop: asyncio.AbstractEventLoop) -> web.Application:
    """Construct the main application."""
    dsn = os.environ.get("DATABASE_URL", None)

    if not dsn:
        raise RuntimeError("DSN not set")

    app = web.Application()
    app["pool"] = await asyncpg.create_pool(dsn, loop=loop)

    async with app["pool"].acquire() as conn:
        await conn.execute("CREATE TABLE IF NOT EXISTS signals (signal timestamptz)")

    app.add_routes([web.post("/signal", signal_handler)])
    return app


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(main(loop))
    web.run_app(app, port=8000, loop=loop)
