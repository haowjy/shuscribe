# shuscribe/schemas/wikigen/story.py


from shuscribe.schemas.base import Promptable


class WikiPage(Promptable):
    title: str
    content: str
    
    @classmethod
    def from_wiki_content(cls, title: str, wiki_content_str: str) -> "WikiPage":
        # Parse the chapter summary into a list of tagged bullets
        wiki_content = wiki_content_str.split("<|STARTWIKI|>")[1].split("<|ENDWIKI|>")[0]

        return cls(title=title, content=wiki_content)
    
    def to_prompt(self) -> str:
        return f"# {self.title} <Content>\n{self.content}\n</Content>"
    