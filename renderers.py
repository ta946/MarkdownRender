from .dependancies import cmarkgfm


class GitHubRenderer:
    """
    Renders the specified Readme as Github Markdown using github's cmark renderer
    """
    def render(self, text):
        """
        Renders the specified markdown content and embedded styles.
        """
        return cmarkgfm.github_flavored_markdown_to_html(text)

