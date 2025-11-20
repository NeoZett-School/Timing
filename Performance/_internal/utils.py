from typing import List, Sequence, Tuple, Optional
from .core import GlobalEnvironment, Environment


# ---------- table utilities ----------

def _fmt(x: Optional[float]) -> str:
    return f"{x:.6f}" if x is not None else "N/A"

def _is_number_string(s: str) -> bool:
    """Return True if s represents an int/float (simple heuristic)."""
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_table_string(
    titles: Sequence[str],
    rows: Sequence[Sequence[str]],
    sep: str = " | ",
    color_header: bool = False,
) -> str:
    """
    Build and return a left/right-aligned table as a single string.

    - titles: sequence of column titles
    - rows: sequence of rows (each row is a sequence of strings)
    - sep: column separator string (default " | ")
    - color_header: if True, colorize header using ANSI escapes (if your terminal supports it)

    The function auto-detects numeric columns and right-aligns them; other columns are left-aligned.
    """
    ncols = len(titles)
    # normalize rows (ensure each row has exactly ncols columns)
    norm_rows: List[Tuple[str, ...]] = []
    for r in rows:
        rlist = list(r)
        if len(rlist) < ncols:
            rlist.extend("" for _ in range(ncols - len(rlist)))
        elif len(rlist) > ncols:
            rlist = rlist[:ncols]
        norm_rows.append(tuple(str(v) for v in rlist))

    # Determine column widths (consider header and all rows)
    widths = [
        max(len(str(titles[c])), *(len(row[c]) for row in norm_rows)) if norm_rows else len(str(titles[c]))
        for c in range(ncols)
    ]

    # Determine numeric columns: True if every non-empty row value in that column parses as a number
    numeric_cols = []
    for c in range(ncols):
        col_vals = [row[c] for row in norm_rows if row[c] != ""]
        numeric_cols.append(bool(col_vals) and all(_is_number_string(v) for v in col_vals))

    # Format header
    header_cells = []
    for c in range(ncols):
        if numeric_cols[c]:
            header_cells.append(f"{titles[c]:>{widths[c]}}")
        else:
            header_cells.append(f"{titles[c]:<{widths[c]}}")
    header = sep.join(header_cells)

    # Optionally colorize header (ANSI)
    if color_header:
        # bold cyan for header, reset after
        header = f"\033[1;36m{header}\033[0m"

    # Divider (match printed width without ANSI escapes)
    total_width = sum(widths) + len(sep) * (ncols - 1)
    divider = "=" * total_width

    # Format rows
    row_lines = []
    for row in norm_rows:
        cells = []
        for c in range(ncols):
            if numeric_cols[c]:
                cells.append(f"{row[c]:>{widths[c]}}")
            else:
                cells.append(f"{row[c]:<{widths[c]}}")
        row_lines.append(sep.join(cells))

    # Assemble
    parts = [header, divider]
    if row_lines:
        parts.extend(row_lines)
    else:
        parts.append("(no entries)")

    return "\n".join(parts)


def print_table(
    titles: Sequence[str],
    rows: Sequence[Sequence[str]],
    sep: str = " | ",
    color_header: bool = False,
) -> None:
    """Build table with get_table_string and print it."""
    print(get_table_string(titles, rows, sep=sep, color_header=color_header))


# ---------- specialized printers for your environment ----------

def print_total_log(count: int = 10, color_header: bool = False) -> None:
    """
    Print the history of individual calls relative to environment start time.

    Columns: Name (left), Start (right), Duration (right), End (right)
    Numeric values formatted to 6 decimal places.
    """
    env: Environment = GlobalEnvironment()
    start = env.start

    rows: List[List[str]] = [
        [
            res.method.name,
            _fmt(res.start - start),
            _fmt(res.duration),
            _fmt(res.end - start),
        ]
        for res in env.history
    ]

    titles = ["Name", "Start", "Duration", "End"]
    print_table(titles, rows[:count], sep=" | ", color_header=color_header)
    row_count = len(rows)
    if row_count > count:
        print(f"+{row_count - count} others...")


def print_overview_log(color_header: bool = False) -> None:
    """
    Print a summary/overview of tracked methods.

    Columns:
      Name (left),
      Creation (right),
      Total (right),
      Avg. (right),
      Min. (right),
      Max. duration (right),
      Calls per second (right),
      Total calls (right)
    Numeric values formatted to 6 decimals (except Total calls).
    """
    env: Environment = GlobalEnvironment()
    start = env.start

    rows: List[List[str]] = []
    for mthd in env.methods:
        rows.append([
            mthd.name,
            _fmt(mthd.created_at - start),
            _fmt(mthd.total_duration),
            _fmt(mthd.avg_duration),
            _fmt(mthd.min_duration),
            _fmt(mthd.max_duration),
            _fmt(mthd.calls_per_second),
            str(mthd.total_calls),
        ])

    titles = [
        "Name", "Creation", "Total", "Avg.", "Min.", "Max. duration",
        "Calls per second", "Total calls"
    ]
    print_table(titles, rows, sep=" | ", color_header=color_header)
