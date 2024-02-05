from dataclasses import dataclass


@dataclass
class MetaInfo:
    title: str
    tags: [str]
    files: [str]
    body: str
