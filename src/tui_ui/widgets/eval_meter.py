"""eval_meter.py: Widget to display evaluation score/bar."""

from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import reactive


class EvalMeter(Widget):
    """Widget displaying the engine evaluation score."""

    DEFAULT_CSS = """
    EvalMeter {
        height: 3;
        width: 100%;
        border: solid green;
        content-align: center middle;
    }
    """

    # Define score as a reactive property with a default value
    score: reactive[float | str] = reactive(0.0)

    def update_eval(self, score: float | str) -> None:
        """Update the eval score."""
        self.score = score  # Changing a reactive automatically triggers re-render!

    def render(self) -> str:
        # Example render using self.score
        if isinstance(self.score, str):
            return f"Eval: {self.score}"
        
        # Display formatted score (e.g., +1.50 or -0.30)
        return f"Eval: {self.score:+.2f}"