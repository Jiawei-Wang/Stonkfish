"""move_history.py: Widget displaying the game's move log."""

from textual.widget import Widget
from textual.widgets import DataTable
from textual.coordinate import Coordinate


class MoveHistory(Widget):
    """Widget displaying chess moves in standard two-column format."""

    DEFAULT_CSS = """
    MoveHistory {
        height: 100%;
        width: 100%;
        border: solid green;
    }
    DataTable {
        height: 100%;
    }
    """

    def compose(self):
        table = DataTable()
        table.add_columns("#", "White", "Black")
        yield table

    def add_move(self, san_move: str) -> None:
        """Add a SAN move to the history list."""
        table = self.query_one(DataTable)
        row_count = table.row_count

        # If odd number of moves, White just moved; if even, Black just moved
        if table.row_count == 0 or len(table.get_row_at(row_count - 1)) == 3 and table.get_row_at(row_count - 1)[2] != "":
            # Start new move pair
            move_num = row_count + 1
            table.add_row(str(move_num), san_move, "")
        else:
            # Update the last row (index: row_count - 1) at column index 2 (or column key 'black')
            table.update_cell_at(Coordinate(row_count - 1, 2), san_move)