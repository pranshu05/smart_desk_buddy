"""summary.py - the end-of-session screen (Pransu's part).

    from summary import show_summary, summarize

    show_summary(log)                              # log = [(minute, "FIDGET"), ...]
    show_summary(log, session_length=25)           # how long the session was (default: guessed)
    show_summary(log, session_length=60, unit="sec")   # for demo mode, where a session is seconds

It draws one lane per kind of interruption with a dot for each time it happened,
and one calm sentence such as "Focus dipped most around minute 18 to 22."
No scores, no blame: it only makes the pattern visible.

`summarize(log)` does the counting without opening any window. Pranshu can use
`summarize(log)["sentence"]` as the answer to "how am I doing?" in the chat box.
"""
import math
import tkinter as tk

import theme

# The kinds of event that count as an interruption, in the order the lanes appear.
KINDS = (
    ("FIDGET", "Fidget"),
    ("SEAT_LEAVE", "Left seat"),
    ("TAB_SWITCH", "Tab switch"),
    ("PHONE", "Phone"),
)
KIND_NAMES = dict(KINDS)


# ---------------------------------------------------------------- the maths
def _interruptions(log):
    """Keep only the interruption events, as sorted (minute, NAME) pairs."""
    out = []
    for item in log or []:
        try:
            minute, name = item
            name = str(getattr(name, "name", name)).upper()
            if name in KIND_NAMES:
                out.append((float(minute), name))
        except (TypeError, ValueError):
            continue            # ignore anything that is not a (minute, name) pair
    return sorted(out)


def _at(m, unit):
    m = int(round(m))
    return f"minute {m}" if unit == "min" else f"{m} seconds"


def _span(a, b, unit):
    return f"minute {a} to {b}" if unit == "min" else f"{a} to {b} seconds"


def _plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def summarize(log, session_length=None, unit="min"):
    """Count the interruptions and find the busiest stretch. Returns a dict."""
    events = _interruptions(log)
    last = max((m for m, _ in events), default=0.0)
    # Default timeline is the standard 25-minute session; it only grows if the log is longer.
    default = 25 if unit == "min" else max(math.ceil(last) + 1, 5)
    length = session_length or default
    length = max(length, last)
    counts = {k: 0 for k, _ in KINDS}
    for _, name in events:
        counts[name] += 1
    total = len(events)

    # busiest stretch = the window (about 1/6 of the session) holding the most events;
    # on a tie, the tighter cluster wins, then the earlier one
    width = max(1.0, round(length / 6.0))
    best_key, best_inside = None, []
    for start, _ in events:
        inside = [m for m, _ in events if start <= m <= start + width]
        key = (len(inside), -(max(inside) - min(inside)))
        if best_key is None or key > best_key:
            best_key, best_inside = key, inside
    peak = None
    if best_key is not None and best_key[0] >= 2:
        lo, hi = min(best_inside), max(best_inside)
        w = int(width)
        a = int(math.floor((lo + hi) / 2 - w / 2 + 0.5))      # centre the stretch on the cluster
        a = max(0, min(a, int(math.floor(lo))))               # ...but never cut an event off
        b = max(a + w, int(math.ceil(hi)))
        b = min(b, int(math.ceil(length)))
        peak = (a, max(b, a + 1))

    if total == 0:
        sentence = "No interruptions this session. Steady from start to finish."
    elif total == 1:
        sentence = f"One interruption, around {_at(events[0][0], unit)}."
    elif peak is None:
        sentence = "Interruptions were spread out; no single stretch stood out."
    else:
        sentence = f"Focus dipped most around {_span(peak[0], peak[1], unit)}."

    unit_word = "minute" if unit == "min" else "second"
    length_text = _plural(int(round(length)), unit_word)
    return {
        "events": events, "counts": counts, "total": total, "length": length,
        "peak": peak, "unit": unit, "sentence": sentence,
        "caption": f"{_plural(total, 'interruption')} in {length_text}",
    }


# ------------------------------------------------------------- the window
def _nice_step(length):
    for step in (1, 2, 5, 10, 15, 20, 30, 60, 120, 300, 600):
        if length / step <= 8:
            return step
    return 600


def show_summary(log, session_length=None, unit="min", parent=None):
    """Open the summary window. Returns the Toplevel."""
    data = summarize(log, session_length, unit)
    owns_root = False
    if parent is None:
        parent = tk._default_root
    if parent is None:                       # run on its own (python summary.py)
        parent = tk.Tk()
        parent.withdraw()
        owns_root = True

    win = tk.Toplevel(parent)
    win.title("Session summary")
    win.configure(bg=theme.BG)
    win.resizable(False, False)
    if not owns_root:
        win.transient(parent.winfo_toplevel())

    pad = 28
    tk.Label(win, text="SESSION SUMMARY", bg=theme.BG, fg=theme.MUTED,
             font=theme.font(10, "bold", mono=True, root=win)).pack(anchor="w", padx=pad, pady=(22, 2))
    tk.Label(win, text=data["sentence"], bg=theme.BG, fg=theme.TEXT, justify="left",
             wraplength=680, font=theme.font(18, "bold", root=win)).pack(anchor="w", padx=pad)
    tk.Label(win, text=data["caption"], bg=theme.BG, fg=theme.MUTED,
             font=theme.font(11, root=win)).pack(anchor="w", padx=pad, pady=(2, 14))

    _draw_timeline(win, data).pack(padx=pad)

    row = tk.Frame(win, bg=theme.BG)
    row.pack(fill="x", padx=pad, pady=(14, 22))
    theme.button(row, "Close", win.destroy, accent=True).pack(side="right")

    win.bind("<Escape>", lambda _e: win.destroy())
    if owns_root:                            # standalone run: closing the window ends the program
        win.bind("<Destroy>", lambda e: parent.quit() if e.widget is win else None)
    win.focus_set()
    return win


def _draw_timeline(master, data):
    W, lane_h, top = 704, 42, 34
    lanes = len(KINDS)
    axis_y = top + lanes * lane_h + 8
    H = axis_y + 34
    x0, x1 = 150, W - 70
    length = data["length"]

    def X(m):
        return x0 + (m / length) * (x1 - x0)

    c = tk.Canvas(master, width=W, height=H, bg=theme.BG, highlightthickness=0)

    # the busiest stretch, as a soft band behind everything
    if data["peak"]:
        a, b = data["peak"]
        c.create_rectangle(X(a), top - 14, X(b), axis_y, fill="#1a2431", outline="")
        c.create_text((X(a) + X(b)) / 2, top - 22, text="busiest stretch",
                      fill=theme.MUTED, font=theme.font(9, root=master))

    # time axis with gridlines
    step = _nice_step(length)
    t = 0
    while t <= length + 1e-9:
        c.create_line(X(t), top - 14, X(t), axis_y, fill=theme.BORDER, dash=(2, 4))
        c.create_text(X(t), axis_y + 14, text=str(t), fill=theme.MUTED,
                      font=theme.font(10, root=master))
        t += step
    c.create_line(x0, axis_y, x1, axis_y, fill=theme.BORDER)
    c.create_text(x1 + 12, axis_y + 14, anchor="w", text=data["unit"], fill=theme.MUTED,
                  font=theme.font(10, root=master))

    # one lane per kind of interruption
    for i, (kind, label) in enumerate(KINDS):
        y = top + i * lane_h + lane_h / 2 - 6
        colour = theme.KIND_COLORS[kind]
        c.create_line(x0, y, x1, y, fill=theme.BORDER)
        c.create_oval(14, y - 5, 24, y + 5, fill=colour, outline="")
        c.create_text(34, y, anchor="w", text=label, fill=theme.TEXT,
                      font=theme.font(12, root=master))
        c.create_text(W - 14, y, anchor="e", text=str(data["counts"][kind]),
                      fill=theme.MUTED, font=theme.font(12, "bold", root=master))
        for minute, name in data["events"]:
            if name == kind:
                c.create_oval(X(minute) - 7, y - 7, X(minute) + 7, y + 7, fill=colour,
                              outline=theme.BG, width=2)
    return c


if __name__ == "__main__":
    # Standalone test:   python3 summary.py
    demo = [(3, "FIDGET"), (7, "TAB_SWITCH"), (8, "TAB_SWITCH"), (14, "SEAT_LEAVE")]
    show_summary(demo, session_length=25)
    tk._default_root.mainloop()
