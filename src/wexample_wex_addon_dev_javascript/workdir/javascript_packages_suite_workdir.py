from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.workdir.framework_packages_suite_workdir import (
    FrameworkPackageSuiteWorkdir,
)

if TYPE_CHECKING:
    from wexample_wex_core.workdir.code_base_workdir import CodeBaseWorkdir


class JavascriptPackagesSuiteWorkdir(FrameworkPackageSuiteWorkdir):

    def _get_children_default_workdir_class(self) -> type[CodeBaseWorkdir]:
        from wexample_wex_addon_dev_javascript.workdir.javascript_package_workdir import (
            JavascriptPackageWorkdir,
        )

        return JavascriptPackageWorkdir
