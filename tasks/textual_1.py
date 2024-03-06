from textual.widgets import TextArea

def create_textual_text_area_with_indent() -> TextArea:
    """Create a TextArea widget, which indents its content when tab is pressed."""
    return TextArea(tab_behavior="indent")