"""prompt loader"""
import shutil
from dataclasses import dataclass
from pathlib import Path
from subprocess import Popen

from markata.hookspec import hook_impl, register_attr


@dataclass
class Prompt:
    file: Path
    command: str
    status: str = "published"

    def __post_init__(self):
        self.title = self.file.name
        self.webp = self.file.with_suffix(".webp")
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

    def to_webp(self):
        if self.file.exists():
            cmd = (
                """npx @squoosh/cli --webp '{"quality":70,"target_size":0,"target_PSNR":0,"method":4,"sns_strength":50,"filter_strength":60,"filter_sharpness":0,"filter_type":1,"partitions":0,"segments":4,"pass":1,"show_compressed":0,"preprocessing":0,"autofilter":0,"partition_limit":0,"alpha_compression":1,"alpha_filtering":1,"alpha_quality":100,"lossless":0,"exact":0,"image_hint":0,"emulate_jpeg_size":0,"thread_level":0,"low_memory":0,"near_lossless":100,"use_delta_palette":0,"use_sharp_yuv":0}' """
                + str(self.file)
            )
            proc = Popen(cmd, shell=True)
            proc.wait()


@hook_impl
def configure(markata) -> None:
    markata.content_directories = [Path("original")]


@hook_impl
@register_attr("articles")
def load(markata) -> None:
    prompts = Path("prompts.txt").read_text().split("\n")
    markata.articles = [
        Prompt(Path(pair[0]), pair[1])
        for p in prompts
        if len(pair := p.split(":")) == 2
    ]


@hook_impl
def render(markata) -> None:
    for article in markata.articles:
        if not article.webp.exists():
            article.to_webp()


@hook_impl
def save(markata) -> None:
    assets_dir = Path(markata.config.get("assets_dir", ""))
    for article in markata.articles:
        # copy from original to static
        # only in local dev, originals are not in prod
        if article.webp.exists():
            shutil.copy(article.webp, assets_dir)
