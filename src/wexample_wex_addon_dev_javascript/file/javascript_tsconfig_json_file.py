from __future__ import annotations

from wexample_filestate.item.file.json_file import JsonFile
from wexample_helpers.decorator.base_class import base_class


@base_class
class JavascriptTsconfigJsonFile(JsonFile):
    def dumps(self, content: dict | None = None) -> str:
        content = content or self.read_parsed()

        compiler_options = content.get("compilerOptions")
        if not isinstance(compiler_options, dict):
            compiler_options = {}
            content["compilerOptions"] = compiler_options

        compiler_options.setdefault("target", "ES2020")
        compiler_options.setdefault("module", "NodeNext")
        compiler_options.setdefault("moduleResolution", "NodeNext")
        compiler_options.setdefault("rootDir", "src")
        compiler_options.setdefault("outDir", "dist")
        compiler_options.setdefault("declaration", True)
        compiler_options.setdefault("declarationMap", True)
        compiler_options.setdefault("sourceMap", True)
        compiler_options.setdefault("strict", False)
        compiler_options.setdefault("esModuleInterop", True)
        compiler_options.setdefault("skipLibCheck", True)
        compiler_options.setdefault("forceConsistentCasingInFileNames", True)

        content.setdefault("include", ["src"])
        content.setdefault("exclude", ["dist", "node_modules", "tests"])

        return super().dumps(content)
