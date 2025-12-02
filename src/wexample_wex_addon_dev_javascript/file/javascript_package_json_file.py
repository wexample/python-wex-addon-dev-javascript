from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.item.file.json_file import JsonFile
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_wex_addon_app.workdir.code_base_workdir import CodeBaseWorkdir


@base_class
class JavascriptPackageJsonFile(JsonFile):
    def get_dependencies_versions(
        self, optional: bool = False, group: str = "dev"
    ) -> dict[str, str]:
        return self.read_config().search(path="dependencies", default={}).to_dict()

    def dumps(self, content: dict | None = None) -> str:
        import json

        content = content or self.read_parsed()

        package = self.find_package_workdir()
        if package:
            content["version"] = package.get_project_version()

        return json.dumps(content or {}, ensure_ascii=False, indent=2)

    def find_package_workdir(self) -> CodeBaseWorkdir | None:
        from wexample_wex_addon_app.workdir.code_base_workdir import CodeBaseWorkdir

        return self.find_closest(CodeBaseWorkdir)
