from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command
from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE

from wexample_wex_addon_dev_javascript.const.tags import DomainTag

if TYPE_CHECKING:
    from wexample_app.response.boolean_response import BooleanResponse
    from wexample_cli.context.execution_context import ExecutionContext
    from wexample_wex_addon_app.service.app_service import AppService


@command(
    type=COMMAND_TYPE_SERVICE,
    description="Check if the Vite dev server is responding",
    tags=[
        DomainTag.DEV_SERVER,
        DomainTag.FRONTEND,
        DomainTag.SERVICE,
        EffectTag.IDEMPOTENT,
        EffectTag.NETWORK_CALL,
        EffectTag.READ_ONLY,
        EffectTag.SUBPROCESS_SPAWN,
        AudienceTag.AGENT_SAFE,
        ScopeTag.APP,
        ScopeTag.LOCAL,
    ],
)
def vite__service__ready(
    context: ExecutionContext,
    service: AppService,
) -> BooleanResponse:
    import subprocess

    from wexample_app.response.boolean_response import BooleanResponse

    runtime = service.app_workdir.get_runtime_config()
    app_project_name = runtime.search("app.project_name").get_str()
    container_name = f"{app_project_name}_vite"
    port = service.manifest.get("vars", {}).get("VITE_PORT", {}).get("default", "8080")

    result = subprocess.run(
        [
            "docker",
            "exec",
            container_name,
            "bun",
            "-e",
            f"await fetch('http://localhost:{port}')",
        ],
        capture_output=True,
    )

    return BooleanResponse(kernel=context.kernel, content=result.returncode == 0)
