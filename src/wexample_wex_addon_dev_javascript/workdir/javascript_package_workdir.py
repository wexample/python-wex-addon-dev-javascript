from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_helpers.decorator.base_class import base_class
from wexample_helpers.helpers.string import string_to_kebab_case
from wexample_helpers_git.helpers.git import (
    git_tag_annotated,
    git_tag_exists,
)

from wexample_wex_addon_dev_javascript.workdir.javascript_workdir import (
    JavascriptWorkdir,
)

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig
    from wexample_filestate.config_value.readme_content_config_value import (
        ReadmeContentConfigValue,
    )
    from wexample_wex_addon_app.workdir.framework_packages_suite_workdir import (
        FrameworkPackageSuiteWorkdir,
    )


@base_class
class JavascriptPackageWorkdir(JavascriptWorkdir):
    def get_package_dependency_name(self) -> str:
        return self.get_package_import_name()

    def get_package_import_name(self) -> str:
        """Get the full package import name with vendor prefix."""
        return self.get_project_name()

    def get_project_name(self) -> str:
        return f"@{self.get_vendor_name()}/{string_to_kebab_case(super().get_project_name())}"

    def prepare_value(self, raw_value: DictConfig | None = None) -> DictConfig:
        from wexample_filestate.const.disk import DiskItemType
        from wexample_helpers.helpers.file import file_read
        from wexample_helpers.helpers.module import module_get_path

        import wexample_wex_addon_dev_javascript

        raw_value = super().prepare_value(raw_value=raw_value)
        children = raw_value["children"]

        children.append(
            {
                "name": ".github",
                "type": DiskItemType.DIRECTORY,
                "should_exist": True,
                "children": [
                    {
                        "name": "workflows",
                        "type": DiskItemType.DIRECTORY,
                        "should_exist": True,
                        "children": [
                            {
                                "name": "publish.yml",
                                "type": DiskItemType.FILE,
                                "should_exist": True,
                                "content": file_read(
                                    module_get_path(
                                        wexample_wex_addon_dev_javascript
                                    )
                                    / "resources"
                                    / "package_publish.yml"
                                ),
                            }
                        ],
                    }
                ],
            }
        )

        return raw_value

    def _classify_version_bump(self, last_tag: str) -> str:
        from wexample_helpers.const.types import (
            UPGRADE_TYPE_MAJOR,
            UPGRADE_TYPE_MINOR,
        )
        from wexample_helpers.helpers.shell import shell_run
        from wexample_helpers_git.helpers.git import git_has_changes_since_tag

        if not git_has_changes_since_tag(last_tag, "src", cwd=self.get_path()):
            return UPGRADE_TYPE_MINOR

        # Check if all changes in src/ are whitespace-only — safe to treat as patch
        result = shell_run(
            ["git", "diff", "-w", "--ignore-blank-lines", last_tag, "--", "src/"],
            cwd=self.get_path(),
            check=False,
            capture=True,
        )
        if not result.stdout.strip():
            self.log("Only whitespace changes in src/, treating as patch.")
            return UPGRADE_TYPE_MINOR

        # Check if all changed files in src/ are non-TypeScript — cannot break the TS API
        changed_files = shell_run(
            ["git", "diff", "--name-only", last_tag, "--", "src/"],
            cwd=self.get_path(),
            check=False,
            capture=True,
        )
        if not any(f.endswith((".ts", ".tsx")) for f in changed_files.stdout.splitlines()):
            self.log("Only non-TypeScript files changed in src/, treating as minor.")
            return UPGRADE_TYPE_INTERMEDIATE

        return UPGRADE_TYPE_MAJOR

    def _get_critical_directories(self) -> list[str]:
        return ["src"]

    def _get_readme_content(self) -> ReadmeContentConfigValue | None:
        from wexample_wex_addon_dev_javascript.config_value.javascript_package_readme_config_value import (
            JavascriptPackageReadmeContentConfigValue,
        )

        return JavascriptPackageReadmeContentConfigValue(workdir=self)

    def _get_suite_workdir_class(self) -> type[FrameworkPackageSuiteWorkdir]:
        from wexample_wex_addon_dev_javascript.workdir.javascript_packages_suite_workdir import (
            JavascriptPackagesSuiteWorkdir,
        )

        return JavascriptPackagesSuiteWorkdir

    def _publish(self, force: bool = False) -> None:
        """Push a git tag to the deployment remote to trigger a CI/CD publication workflow."""
        from wexample_helpers_git.helpers.git import git_push_tag

        remote = self._get_deployment_remote_name()
        if not remote:
            self.log("No deployment remote configured, skipping publication.")
            return

        tag = f"v{self.get_setup_version()}"
        cwd = self.get_path()

        if git_tag_exists(tag, cwd=cwd, inherit_stdio=False):
            self.log(f"Tag {tag} already exists, skipping creation.")
        else:
            git_tag_annotated(tag, f"Release {tag}", cwd=cwd, inherit_stdio=True)

        git_push_tag(tag, cwd=cwd, remote=remote, inherit_stdio=True)

    def _wait_for_registry(self) -> None:
        """Poll the configured npm registry until the current version is available (max 20 min).

        Works for both public npm and private registries (e.g. GitLab) that
        don't expose per-version URLs — relies on the package manifest's
        `versions` map.
        """
        from wexample_helpers.helpers.polling_callback_manager import (
            PollingCallbackManager,
        )

        from wexample_wex_addon_dev_javascript.common.npm_registry_gateway import (
            NpmRegistryGateway,
        )

        package = self.get_project_name()
        version = self.get_setup_version()

        registry_base = (
            self.get_runtime_config().search("npm.registry_url").get_str_or_none()
            or "https://registry.npmjs.org"
        )
        token = self.get_runtime_config().search("npm.api_token").get_str_or_none()

        gateway = NpmRegistryGateway(
            base_url=registry_base,
            token=token,
            io=self.io,
            timeout=10,
        )

        max_attempts = 40
        delay_seconds = 30

        self.log(f"Waiting for {package}@{version} to appear on registry…")

        def on_retry(attempt, max_a, delay, _exc, _msg) -> None:
            self.log(
                f"Not yet available (attempt {attempt}/{max_a}), retrying in {delay}s…"
            )

        PollingCallbackManager(
            callback=lambda: True if gateway.has_version(package, version) else None,
            max_attempts=max_attempts,
            delay_seconds_callback=lambda _attempt: delay_seconds,
            on_retry_callback=on_retry,
            timeout_message=(
                f"Timed out waiting for {package}@{version} on registry after "
                f"{max_attempts * delay_seconds // 60} minutes."
            ),
        ).run()

        self.success(f"{package}@{version} is available.")
