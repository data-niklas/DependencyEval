import emoji

THUMBS_UP = emoji.emojize(":thumbs_up:")
THUMBS_DOWN = emoji.emojize(":thumbs_down:")

def does_the_text_contain_only_emojis(text: str) -> str:
    """Return either thumbs up or down depending on text containing only emojis.

    Args:
        text (str): Any input text

    Returns:
        str: Thumbs up emoji if text only contains emojis. Else thumbs down.
    """
    return THUMBS_UP if emoji.purely_emoji(text) else THUMBS_DOWN