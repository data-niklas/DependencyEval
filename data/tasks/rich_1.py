from rich.style import Style


def clear_style(style: Style) -> Style:
    """Obtain a copy of style with all meta and links removed.

    Args:
        style (Style): target style

    Returns:
        Style: target style without meta and links
    """    
    return style.clear_meta_and_links()