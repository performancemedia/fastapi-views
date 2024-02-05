from __future__ import annotations

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
except ImportError:
    FastAPIInstrumentor = None

try:
    from opentelemetry.context import Context
except ImportError:
    Context = None


def get_context_trace_id() -> str | None:
    if Context is None:
        return None
    try:
        return Context.get_current().trace_id

    except Exception:
        return None


def maybe_instrument_app(app, **options):
    if FastAPIInstrumentor is not None:
        FastAPIInstrumentor.instrument_app(app, **options)
