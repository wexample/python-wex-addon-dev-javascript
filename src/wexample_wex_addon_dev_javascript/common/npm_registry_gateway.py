from __future__ import annotations

from wexample_api.common.abstract_gateway import AbstractGateway
from wexample_helpers.classes.field import public_field
from wexample_helpers.decorator.base_class import base_class


@base_class
class NpmRegistryGateway(AbstractGateway):
    """Thin HTTP gateway over an npm registry JSON API.

    Targets public npm (`https://registry.npmjs.org`) and private registries
    that expose the same package-manifest layout (e.g. GitLab npm registry).
    Optional Bearer auth via `token`.
    """

    token: str | None = public_field(
        default=None,
        description="Optional Bearer token for private registries.",
    )

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        if self.token:
            self.default_headers["Authorization"] = f"Bearer {self.token}"

    def has_version(self, package: str, version: str) -> bool:
        """Return True iff `package@version` is published on this registry.

        Fetches the package manifest and looks up the version in the
        `versions` map — works for both public npm and private (GitLab)
        registries that don't expose per-version URLs. Returns False on
        404 (unknown package or version not yet propagated).
        """
        encoded = package.replace("/", "%2F")
        response = self.make_request(
            endpoint=encoded,
            expected_status_codes=[200, 404],
            fatal_if_unexpected=False,
            quiet=True,
        )
        if response is None or response.status_code != 200:
            return False
        return version in (response.json().get("versions") or {})
