"""prompt loader"""
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Optional

import frontmatter
from markata.background import task
from markata.hookspec import hook_impl, register_attr
from rich.progress import BarColumn, Progress
from yaml.parser import ParserError


@dataclass
class Prompt:
    file: Path
    command: str

    def __post_init__(self):
        self.title = self.file.name
        self.slug = self.file.name
        self.prompt = self.command.split('"')[1]
        self.params = {p[1]: p[2:] for p in self.command.split('"')[2].split()}
        self.height = self.params["H"]
        self.width = self.params["W"]

    def __getitem__(self, key):
        return self.to_dict()[key]

    def keys(self):
        return self.to_dict().keys()

    def to_dict(self):
        return vars(self)


@hook_impl
@register_attr("articles")
def load(markata: "MarkataMarkdown") -> None:
    markata.content_dirdirectories = [Path(".")]
    prompts = Path("prompts.txt").read_text().split("\n")
    markata.articles = [
        Prompt(Path(pair[0]), pair[1])
        for p in prompts
        if len(pair := p.split(":")) == 2
    ]
