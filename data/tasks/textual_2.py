from textual.app import App
from textual.types import AnimationLevel

def create_app_without_animations() -> App:
    """Create a minimal textual App without animations.

    Returns:
        App: New App instance with disabled animations
    """
    app = App()
    app.animation_level = "none"
    return app