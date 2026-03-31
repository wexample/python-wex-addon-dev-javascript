from __future__ import annotations

from typing import TYPE_CHECKING

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

        children.extend(
            [
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
            ]
        )

        return raw_value

    def _get_readme_content(self) -> ReadmeContentConfigValue | None:
        from wexample_wex_addon_dev_javascript.config_value.javascript_package_readme_config_value import (
            JavascriptPackageReadmeContentConfigValue,
        )

        return JavascriptPackageReadmeContentConfigValue(workdir=self)

    def _get_suite_package_workdir_class(self) -> type[FrameworkPackageSuiteWorkdir]:
        from wexample_wex_addon_dev_javascript.workdir.javascript_packages_suite_workdir import (
            JavascriptPackagesSuiteWorkdir,
        )

        return JavascriptPackagesSuiteWorkdir

    def _get_github_remote_name(self) -> str:
        return self.search_app_or_suite_runtime_config(
            "git.github_remote_name", default="github"
        ).get_str()

    def _wait_for_registry(self) -> None:
        """Poll the npm registry until the current version is available (max 20 min)."""
        import time
        import urllib.error
        import urllib.request

        package = self.get_project_name()
        version = self.get_project_version()
        url = f"https://registry.npmjs.org/{package}/{version}"
        max_attempts = 40
        delay = 30.0

        self.log(f"Waiting for {package}@{version} to appear on npm registry…")

        for attempt in range(1, max_attempts + 1):
            try:
                with urllib.request.urlopen(url, timeout=10) as resp:
                    if resp.status == 200:
                        self.success(f"{package}@{version} is available on npm.")
                        return
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    raise
            except Exception:
                pass

            self.log(
                f"Not yet available (attempt {attempt}/{max_attempts}), "
                f"retrying in {int(delay)}s…"
            )
            time.sleep(delay)

        raise RuntimeError(
            f"Timed out waiting for {package}@{version} on npm after "
            f"{max_attempts * int(delay) // 60} minutes."
        )

    def _publish(self, force: bool = False) -> None:
        """Create a git tag (vX.Y.Z) to trigger Trusted Publisher workflow."""
        from wexample_helpers_git.helpers.git import git_push_tag

        tag = f"v{self.get_project_version()}"
        cwd = self.get_path()

        if git_tag_exists(tag, cwd=cwd, inherit_stdio=False):
            self.log(f"Tag {tag} already exists, skipping creation.")
        else:
            git_tag_annotated(tag, f"Release {tag}", cwd=cwd, inherit_stdio=True)

        # Push the v* tag to GitHub to trigger GitHub Actions publication workflow.
        git_push_tag(tag, cwd=cwd, remote=self._get_github_remote_name(), inherit_stdio=True)
