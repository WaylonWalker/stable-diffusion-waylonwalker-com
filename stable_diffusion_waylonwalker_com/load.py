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

    def __getitem__(self, key):
        return self.to_dict()[key]

    def keys(self):
        return self.to_dict().keys()

    def to_dict(self):
        return {
            "file": self.file,
            "command": self.command,
            "title": self.file.name,
            "slug": self.file.name,
        }


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
