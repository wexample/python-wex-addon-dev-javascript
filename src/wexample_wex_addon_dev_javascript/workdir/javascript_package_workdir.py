from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_addon_dev_javascript.workdir.javascript_workdir import (
    JavascriptWorkdir,
)

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig


class JavascriptPackageWorkdir(JavascriptWorkdir):
    def prepare_value(self, raw_value: DictConfig | None = None) -> DictConfig:
        raw_value = super().prepare_value(raw_value=raw_value)

        return raw_value
