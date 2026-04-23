from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine

configure_logging()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.include_router(router)
