from typing import Iterable
from jinja2 import Template
from pathlib import Path
import toml

BUILD = Path("build")
SRC = Path("src")

TEMPLATE = Path("index.html.j2")
PYPROJECT = Path("pyproject.toml")

OUTPUT_HTML = BUILD / "index.html"


def get_packages():
    yield from toml.loads(PYPROJECT.read_text())["tool"]["poetry"]["group"]["stlite"]["dependencies"]


def escape_contents(lines: list[str]):
    for line in lines:
        yield line.encode("unicode_escape").decode("utf-8").replace("`", r"\`")


def js_files_dict():
    for path in SRC.glob("*.py"):
        escaped = escape_contents(path.read_text().split("\n"))
        joined = "\n".join(escaped)
        yield f'"{path.name}": `\n{joined}\n`'


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    
    template = Template(TEMPLATE.read_text())
    rendered = template.render(
        title="Pack Stats",
        requirements=list(get_packages()),
        files_dict=",\n".join(js_files_dict()),
    )

    OUTPUT_HTML.write_text(rendered)


if __name__ == "__main__":
    main()
