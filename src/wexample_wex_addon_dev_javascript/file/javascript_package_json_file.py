from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.item.file.json_file import JsonFile
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_wex_addon_app.workdir.code_base_workdir import CodeBaseWorkdir


@base_class
class JavascriptPackageJsonFile(JsonFile):
    def add_dependency(
            self,
            package: CodeBaseWorkdir,
            version: str,
            operator: str = "",
            optional: bool = False,
            group: None | str = None,
    ) -> bool:
        """
        Add or update an npm dependency entry (dependencies, devDependencies, etc.).
        Returns True if the dependency list changed.
        """
        if optional:
            section = "optionalDependencies"
        elif group == "dev":
            section = "devDependencies"
        elif group:
            section = group
        else:
            section = "dependencies"

        constraint = f"{operator}{version}".strip()

        config = self.read_config()
        deps_node = config.search(path=section, default={})
        deps = deps_node.to_dict() if deps_node else {}

        package_name = package.get_package_dependency_name()
        if deps.get(package_name) == constraint:
            return False

        deps[package_name] = constraint
        config.update_nested({section: deps})
        self.write_config(config)

        return True

    def dumps(self, content: dict | None = None) -> str:
        content = content or self.read_parsed()

        workdir = self.get_parent_item()
        content["name"] = workdir.get_package_import_name()
        content["version"] = workdir.get_project_version()

        if not content.get("type"):
            content["type"] = "module"

        return super().dumps(content or {})

    def get_dependencies_versions(
            self, optional: bool = False, group: str = "dev"
    ) -> dict[str, str]:
        return (
            self.read_config()
            .search(path="dependencies")
            .get_dict_or_default(default={})
        )
