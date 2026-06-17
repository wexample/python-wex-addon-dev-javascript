from __future__ import annotations

from wexample_filestate.item.file.json_file import JsonFile
from wexample_helpers.decorator.base_class import base_class
from wexample_wex_addon_app.item.file.mixin.app_dependencies_config_file_mixin import (
    AppDependenciesConfigFileMixin,
)


@base_class
class JavascriptPackageJsonFile(AppDependenciesConfigFileMixin, JsonFile):
    def add_dependency(
        self,
        operator: str = "",
        **kwargs,
    ) -> bool:
        # NPM uses bare versions (or ^/~), not "==".
        return super().add_dependency(
            operator=operator,
            **kwargs,
        )

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
        content["version"] = workdir.get_setup_version()

        remote_url = workdir.get_public_remote_repository_url()
        if remote_url:
            content["repository"] = remote_url

        self._apply_default_publish_config(content)

        return super().dumps(content)

    def get_dependencies_versions(
        self, optional: bool = False, group: str = "dev"
    ) -> dict[str, str]:
        config = self.read_config()
        # Use to_dict_or_none() (not get_dict_or_default) so nested ConfigValue
        # wrappers are unwrapped to native str — matches the dict[str, str] signature.
        deps = config.search(path="dependencies").to_dict_or_none() or {}
        peer = config.search(path="peerDependencies").to_dict_or_none() or {}
        return {**deps, **peer}

    def _apply_default_publish_config(self, content: dict) -> None:
        content.setdefault("type", "module")

        publish_config = content.get("publishConfig")
        if publish_config is None:
            content["publishConfig"] = {"access": "public"}
        elif isinstance(publish_config, dict):
            publish_config.setdefault("access", "public")

        files = content.get("files")
        exports = content.get("exports")

        exports_text = str(exports) if exports is not None else ""
        files_list = files if isinstance(files, list) else []
        uses_dist = "dist" in exports_text or "dist" in files_list
        uses_src = "src" in exports_text or "src" in files_list

        # Default strategy: publish built artifacts (dist) so consumers don't need
        # to transpile TS/ESM sources from node_modules.
        if exports is None and (files is None or (uses_src and not uses_dist)):
            if "files" not in content:
                content["files"] = ["dist"]
            if "exports" not in content:
                content["exports"] = {
                    "./*": {
                        "types": "./dist/*.d.ts",
                        "default": "./dist/*.js",
                    }
                }
            if "typesVersions" not in content:
                content["typesVersions"] = {
                    "*": {
                        "*": ["dist/*"],
                    }
                }
            return

        if uses_src and not uses_dist:
            if files is None and "files" not in content:
                content["files"] = ["src"]
            if "typesVersions" not in content:
                content["typesVersions"] = {
                    "*": {
                        "*": ["src/*"],
                    }
                }
