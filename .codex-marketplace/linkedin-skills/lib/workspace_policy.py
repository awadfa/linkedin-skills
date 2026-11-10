"""The fork defaults to offline, manual delivery, even with stored API keys."""
from __future__ import annotations
import os


class WorkspacePolicyError(RuntimeError):
    pass


def zero_cost_mode() -> bool:
    # Deliberately not loaded by _env.load_env(). Unknown values fail closed.
    return os.environ.get('LINKEDIN_SKILLS_PROFILE', 'zero-cost') != 'legacy'


def require_legacy_network() -> None:
    if zero_cost_mode():
        raise WorkspacePolicyError(
            'Zero-cost workspace: external service calls are disabled. '
            'Use the connected Clay research workflow after confirming it is free, '
            'or import existing results. Publishing and outreach remain manual.'
        )


def guarded_session():
    """Guard the transport, including direct client calls and GET/DELETE paths."""
    import requests

    class GuardedSession(requests.Session):
        def request(self, *args, **kwargs):
            require_legacy_network()
            return super().request(*args, **kwargs)

    return GuardedSession()
