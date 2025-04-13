# shuscribe/schemas/wikigen/summary.py

from typing import List
import re

from pydantic import BaseModel, Field

from shuscribe.schemas.base import Promptable


class TaggedBullet(BaseModel):
    tag: str
    content: str

class ChapterSummary(Promptable):
    chapter_id: int
    summary: str
    tagged_summary: str
    raw_summary: str
    tagged_bullets: List[TaggedBullet] = Field(default_factory=list)
    
    @classmethod
    def from_chapter_summary(cls, chapter_id: int, chapter_summary_str: str) -> "ChapterSummary":
        # Parse the chapter summary into a list of tagged bullets
        raw_summary = chapter_summary_str
        tagged_summary = chapter_summary_str.split("<|STARTOFSUMMARY|>")[1].split("<|ENDOFSUMMARY|>")[0]
        no_tags = []
        tagged_bullets = []
        for line in tagged_summary.split("\n"):
            if line.strip():
                # ends with a tag [!TAG]
                tags = re.findall(r'\[!([^\]]+)\]', line)
                content = re.sub(r'\[!([^\]]+)\]', '', line).rstrip()
                for tag in tags:
                    tagged_bullets.append(TaggedBullet(tag=tag, content=content))
                no_tags.append(content)
        return cls(
            chapter_id=chapter_id, 
            summary="\n".join(no_tags),
            tagged_summary=tagged_summary, 
            raw_summary=raw_summary, 
            tagged_bullets=tagged_bullets
            )

    
    def to_prompt(self) -> str:
        return f"<Content>\n{self.tagged_summary}\n</Content>"