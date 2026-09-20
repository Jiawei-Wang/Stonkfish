"""eval_meter.py: Widget to display evaluation score/bar."""

from textual.widget import Widget
from textual.widgets import Static


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score_text = "Eval: 0.0"

    def compose(self):
        yield Static(self.score_text, id="eval_label")

    def update_eval(self, score: float | str) -> None:
        """Update evaluation reading (e.g., +0.5 or '#M3')."""
        label = self.query_one("#eval_label", Static)
        if isinstance(score, float):
            prefix = "+" if score > 0 else ""
            self.score_text = f"Eval: {prefix}{score:.2f}"
        else:
            self.score_text = f"Eval: {score}"
        label.update(self.score_text)