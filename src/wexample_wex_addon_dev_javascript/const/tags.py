"""Domain tags exposed by this addon — one entry per `domain:*` value its commands use."""
from __future__ import annotations


class DomainTag:
    """Functional domain this addon's commands touch."""

    DEV_SERVER = "domain:dev-server"
    FRONTEND = "domain:frontend"
    SERVICE = "domain:service"
