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
    from wexample_filestate.config_value.readme_content_config_value import (
        ReadmeContentConfigValue,
    )
    from wexample_wex_addon_app.workdir.framework_packages_suite_workdir import (
        FrameworkPackageSuiteWorkdir,
    )


class JavascriptPackageWorkdir(JavascriptWorkdir):
    def get_project_name(self) -> str:
        return f"@{self.get_vendor_name()}/{string_to_kebab_case(super().get_project_name())}"

    def get_package_dependency_name(self) -> str:
        return self.get_package_import_name()

    def get_package_import_name(self) -> str:
        """Get the full package import name with vendor prefix."""
        return self.get_project_name()

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

    def _publish(self, force: bool = False) -> None:
        """Create a git tag (vX.Y.Z) to trigger Trusted Publisher workflow."""
        tag = f"v{self.get_project_version()}"
        cwd = self.get_path()

        if git_tag_exists(tag, cwd=cwd, inherit_stdio=False):
            self.log(f"Tag {tag} already exists, skipping creation.")
        else:
            git_tag_annotated(tag, f"Release {tag}", cwd=cwd, inherit_stdio=True)

        # Uses git repo to deploy packages (tag push triggers GitHub Actions publication).
        self.push_to_deployment_remote()
