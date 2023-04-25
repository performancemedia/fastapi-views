import sys

from fastapi_views import configure_app


def test_configure_app(app):
    configure_app(app)


def test_python_version():
    assert sys.version_info > (3, 8, 1)
