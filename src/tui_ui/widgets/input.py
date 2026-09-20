"""input.py: Input bar widget for typing move SAN commands."""

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input


class MoveInputBar(Widget):
    """Widget for typing SAN moves or CLI commands."""

    DEFAULT_CSS = """
    MoveInputBar {
        height: 3;
        width: 100%;
    }
    """

    class MoveSubmitted(Message):
        """Custom event posted when user submits a move string."""
        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Type move in SAN (e.g., e4, Nf3, quit)...", id="move_input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Catch Enter key inside Input widget."""
        value = event.value.strip()
        if value:
            self.post_message(self.MoveSubmitted(value))
            event.input.value = ""  # Clear input field