import emoji

THUMBS_UP = emoji.emojize(":thumbs_up:")
THUMBS_DOWN = emoji.emojize(":thumbs_down:")

def does_the_text_contain_only_emojis(text: str) -> str:
    return THUMBS_UP if emoji.purely_emoji(text) else THUMBS_DOWN