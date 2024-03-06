from rich.style import Style

def clear_style(style: Style) -> Style:
    """Obtain a copy of style with all meta and links removed."""
    return style.clear_meta_and_links()