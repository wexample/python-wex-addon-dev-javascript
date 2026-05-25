from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE
from wexample_cli.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_addon_app.service.app_service import AppService
    from wexample_cli.context.execution_context import ExecutionContext


@command(
    type=COMMAND_TYPE_SERVICE,
    description="Patch vite.config.ts to allow all hosts (needed behind a reverse proxy)",
)
def vite__service__install(
    context: ExecutionContext,
    service: AppService,
) -> None:
    import re

    app_path = service.app_workdir.get_path()

    for config_name in ["vite.config.ts", "vite.config.js"]:
        config_path = app_path / config_name
        if not config_path.exists():
            continue

        content = config_path.read_text()

        if "allowedHosts" in content:
            context.io.log(f"  {config_name}: allowedHosts already set, skipping")
            return

        # defineConfig() → defineConfig({ vite: { server: { allowedHosts: true } } })
        # defineConfig({ ... }) → add server.allowedHosts: true inside vite: {}
        if "defineConfig()" in content:
            content = content.replace(
                "defineConfig()",
                "defineConfig({ vite: { server: { allowedHosts: true } } })",
            )
        elif re.search(r"defineConfig\(\s*\{", content):
            content = re.sub(
                r"(defineConfig\(\s*\{)",
                r"\1 vite: { server: { allowedHosts: true } },",
                content,
                count=1,
            )
        else:
            context.io.log(f"  {config_name}: unrecognized format, skipping")
            return

        config_path.write_text(content)
        context.io.log(f"  ✓ {config_name}: allowedHosts patched")
        return

    context.io.log("  No vite.config.ts/js found, skipping allowedHosts patch")
