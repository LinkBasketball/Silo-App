import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import candidates, conflicts, finance, news, rhetoric, system
from app.core.config import APP_VERSION, get_settings
from app.core.database import SessionLocal, engine
from app.core.errors import install_error_handlers

logging.basicConfig(level=logging.INFO, format='{"level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}')
log = logging.getLogger("silo")
BACKEND_DIR = Path(__file__).resolve().parent.parent


def run_migrations(url: str | None = None) -> None:
    from alembic.config import Config

    from alembic import command

    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    cfg.set_main_option("sqlalchemy.url", url or get_settings().database_url)
    cfg.attributes["configure_logger"] = False
    logging.getLogger("alembic").setLevel(logging.WARNING)
    command.upgrade(cfg, "head")


@asynccontextmanager
async def lifespan(_: FastAPI):
    s = get_settings()
    if s.auto_migrate:
        run_migrations()
    if s.seed_demo_data:
        from app.seed.loader import seed_demo
        with SessionLocal() as db:
            if seed_demo(db):
                log.info("Loaded demonstration fixtures")
    from app.nlp.engine import get_engine
    log.info("NLP engine: %s", get_engine().name)
    yield
    engine.dispose()


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(
        title="SILO API", version=APP_VERSION, lifespan=lifespan,
        description="Civic intelligence, without the noise. Evidence-first, nonpartisan analysis of political text and public records.",
        docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url=None,
    )
    app.add_middleware(CORSMiddleware, allow_origins=s.cors_origin_list, allow_methods=["GET", "POST"],
                       allow_headers=["Content-Type"], allow_credentials=False)
    install_error_handlers(app)
    for r in (system.router, news.router, candidates.router, finance.router, rhetoric.router, conflicts.router):
        app.include_router(r, prefix="/api")
    return app


app = create_app()
