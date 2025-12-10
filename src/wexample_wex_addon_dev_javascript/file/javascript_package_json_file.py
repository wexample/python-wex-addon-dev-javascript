from __future__ import annotations

from wexample_filestate.item.file.json_file import JsonFile
from wexample_helpers.decorator.base_class import base_class
from wexample_wex_addon_app.item.file.mixin.app_dependencies_config_file_mixin import AppDependenciesConfigFileMixin


@base_class
class JavascriptPackageJsonFile(AppDependenciesConfigFileMixin, JsonFile):
    def add_dependency_from_string(
            self,
            package_name: str,
            version: str,
            operator: str = "",
            optional: bool = False,
            group: None | str = None,
    ) -> bool:
        """
        Add or update an npm dependency entry from a raw package name + version string.
        Equivalent to add_dependency() but without requiring a CodeBaseWorkdir.
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

        if deps.get(package_name) == constraint:
            return False

        deps[package_name] = constraint
        config.update_nested({section: deps})
        self.write_config(config)

        return True

    def dumps(self, content: dict | None = None) -> str:
        content = content or self.read_parsed()

        workdir = self.get_parent_item()
        content["name"] = workdir.get_project_name()
        content["version"] = workdir.get_project_version()

        return super().dumps(content or {})

    def get_dependencies_versions(
            self, optional: bool = False, group: str = "dev"
    ) -> dict[str, str]:
        return (
            self.read_config()
            .search(path="dependencies")
            .get_dict_or_default(default={})
        )
