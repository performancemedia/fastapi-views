from fastapi import FastAPI

from fastapi_views import configure_app


def test_configure_app():
    app = FastAPI()
    configure_app(app)
