import os
import shutil
from pathlib import Path

import pathvalidate

from model import MetaInfo
import re
import typer
import time


path_base: str = "data"
path_in: str = os.path.join(path_base, "in")
path_in_notes: str = os.path.join(path_in, "notes")
path_in_attachments: str = os.path.join(path_in, "attachments")
path_out: str = os.path.join(path_base, "out")


def meta_parse(body: str) -> MetaInfo:
    match_head: re.Match = re.search(r"---\n(.*)\n---", body, re.DOTALL)
    title: str = f"_ERR_{int(time.time())}"
    tags: [str] = []
    attachment: [str] = []

    if match_head:
        result_head: str = match_head.group(1)
        body = body.replace(match_head.group(0) + "\n\n", "")
        match_tags: re.Match = re.search(r"tags: \[(.*)\]", result_head)
        match_title: re.Match = re.search(r"title: (.*)", result_head)

        if match_tags:
            tags: [str] = match_tags.group(1).replace("Notebooks/", "").replace("/", os.sep).split(",")

        if match_title:
            title: str = match_title.group(1)

        match_attachment = re.findall(r"\(@attachment/(.*?)\)", body)

        if match_attachment:
            attachment = match_attachment

    meta_info: MetaInfo = MetaInfo(title=title, tags=tags, files=attachment, body=body)

    return meta_info


def attachment_fix(body: str) -> str:
    result: str = body.replace("@attachment/", "")

    return result


def dir_structure(path_relative) -> None:
    for p in path_relative:
        os.makedirs(os.path.join(path_out, p), exist_ok=True)


def note_migrate(meta_info: MetaInfo) -> None:
    for t in meta_info.tags:
        path_base_tmp: str = os.path.join(path_out, t)

        sani = pathvalidate.FileNameSanitizer(platform=pathvalidate.Platform.UNIVERSAL, validate_after_sanitize=True)
        file_target = os.path.join(path_base_tmp, sani.sanitize(meta_info.title + ".md"))

        with open(file_target, "x", encoding="utf-8") as f:
            f.write(meta_info.body)

        for a in meta_info.files:
            file_src = os.path.join(path_in_attachments, a)

            if os.path.isfile(file_src):
                shutil.copy2(file_src, os.path.join(path_base_tmp, a))


def run() -> None:
    files = Path(path_in_notes).glob("*.md")
    #files = [os.path.join(path_in_notes, "Applikationshinweise Vitesco (Conti).md")]

    for file in files:
        print(file)

        with open(file, encoding="utf-8") as f:
            body: str = f.read()

        meta_info: MetaInfo = meta_parse(body)
        meta_info.body = attachment_fix(meta_info.body)

        dir_structure(meta_info.tags)
        note_migrate(meta_info)


if __name__ == "__main__":
    typer.run(run)
