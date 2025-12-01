from __future__ import annotations

from wexample_wex_addon_app.workdir.code_base_workdir import CodeBaseWorkdir


class JavascriptWorkdir(CodeBaseWorkdir):
    def get_dependencies_versions(self) -> dict[str, str]:
        # TODO search in package.json
        return {}
