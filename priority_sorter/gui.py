from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Dict, List

from .items import Item, seeded_items
from .sorter import Choice, PairwiseSorter, CompareState


class ScrollableFrame(ttk.Frame):
    """Minimal vertical scroll container for item rows."""

    def __init__(self, master: tk.Widget, **kwargs) -> None:
        super().__init__(master, **kwargs)
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = ttk.Frame(canvas)
        self.inner.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        window = canvas.create_window((0, 0), window=self.inner, anchor="nw")

        def _on_mousewheel(event: tk.Event) -> None:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfig(window, width=event.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class PrioritySorterApp:
    """Tkinter rendition of the interactive priority sorter."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Priority Sorter")
        self.root.geometry("500x800")
        self.root.minsize(360, 600)

        self.items: List[Item] = seeded_items()
        self.sorter: PairwiseSorter[Item] = PairwiseSorter()
        self.mode: str = "list"
        self._original_index: Dict[int, int] = {}
        self._edit_vars: Dict[int, tk.StringVar] = {}

        self._build_ui()
        self._bind_shortcuts()
        self.refresh_items()
        self._update_sort_button()

    def _build_ui(self) -> None:
        self.style = ttk.Style(self.root)
        self.style.configure("Title.TLabel", font=("Helvetica", 30, "bold"))

        # List view container
        self.list_frame = ttk.Frame(self.root, padding=20)
        self.title_label = ttk.Label(
            self.list_frame, text="Priorities", style="Title.TLabel"
        )
        self.title_label.pack(anchor="center", pady=(0, 20))

        entry_row = ttk.Frame(self.list_frame)
        entry_row.pack(fill="x", pady=(0, 20))

        self.new_item_var = tk.StringVar()
        self.new_item_entry = ttk.Entry(
            entry_row, textvariable=self.new_item_var, font=("Helvetica", 12)
        )
        self.new_item_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.new_item_entry.bind("<Return>", lambda event: self.create_item())

        add_button = ttk.Button(entry_row, text="Add", command=self.create_item)
        add_button.pack(side="right")

        self.sort_button = ttk.Button(
            self.list_frame, text="Sort Items", command=self.enter_compare_mode
        )
        self.sort_button.pack(fill="x", pady=(0, 20))

        self.scroll_frame = ScrollableFrame(self.list_frame)
        self.scroll_frame.pack(fill="both", expand=True)

        # Comparison view container
        self.compare_frame = ttk.Frame(self.root, padding=30)
        self.prompt_label = ttk.Label(
            self.compare_frame, text="", style="Title.TLabel", wraplength=400
        )

        # Main comparison body: choices on the left, live ordering on the right.
        self.body_frame = ttk.Frame(self.compare_frame)

        # Left column: pairwise choice buttons.
        self.choice_frame = ttk.Frame(self.body_frame)
        self.choice_frame.pack(side="left", fill="both", expand=True, pady=(0, 20))

        self.left_button = ttk.Button(
            self.choice_frame,
            text="",
            command=lambda: self._select_choice(Choice.LEFT),
        )
        self.left_button.pack(fill="x", pady=10)

        self.right_button = ttk.Button(
            self.choice_frame,
            text="",
            command=lambda: self._select_choice(Choice.RIGHT),
        )
        self.right_button.pack(fill="x")

        # Right column: legend + toggle + scrollable live view of current ordering.
        self.state_column = ttk.Frame(self.body_frame, width=180)
        self.state_column.pack(side="right", fill="y", padx=(20, 0))

        # Legend explaining movement and search symbols.
        self.state_legend_frame = ttk.Frame(self.state_column)

        legend_title = ttk.Label(
            self.state_legend_frame,
            text="Legend:",
            font=("Helvetica", 9, "bold"),
        )
        legend_title.pack(anchor="w")

        legend_text = ttk.Label(
            self.state_legend_frame,
            text="↑ up  ↓ down  • same\n● current  □ search",
            justify="left",
        )
        legend_text.pack(anchor="w")

        self.show_state_var = tk.BooleanVar(value=False)
        self.state_toggle = ttk.Checkbutton(
            self.state_column,
            text="Show live order",
            variable=self.show_state_var,
            command=self._on_toggle_state_view,
        )
        self.state_toggle.pack(anchor="w", pady=(0, 8))

        self.state_scroll = ScrollableFrame(self.state_column)
        self.state_scroll.pack(fill="both", expand=True)

        self.results_var = tk.StringVar(value="")
        self.results_frame = ttk.Frame(self.compare_frame)
        self.results_title = ttk.Label(
            self.results_frame,
            text="Sorted items",
            style="Title.TLabel",
        )
        self.results_title.pack(anchor="center", pady=(0, 20))
        self.results_label = ttk.Label(
            self.results_frame,
            textvariable=self.results_var,
            justify="left",
            anchor="w",
            wraplength=400,
        )
        self.results_label.pack(fill="x")

        self.back_button = ttk.Button(
            self.compare_frame, text="Back to Items View", command=self.return_to_list
        )
        self.back_button.pack(pady=(30, 0))

        self.show_list_view()

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Escape>", lambda event: self.return_to_list())
        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Left>", lambda event: self._select_choice(Choice.LEFT))
        self.root.bind("<Right>", lambda event: self._select_choice(Choice.RIGHT))

    def _toggle_fullscreen(self, event: tk.Event | None = None) -> None:
        current = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current)

    def show_list_view(self) -> None:
        self.mode = "list"
        self.compare_frame.pack_forget()
        self.list_frame.pack(fill="both", expand=True)
        self.new_item_entry.focus_set()

    def show_compare_view(self) -> None:
        self.mode = "compare"
        self.list_frame.pack_forget()
        self.compare_frame.pack(fill="both", expand=True)
        if not self.prompt_label.winfo_ismapped():
            self.prompt_label.pack(pady=(0, 30))
        if not self.body_frame.winfo_ismapped():
            self.body_frame.pack(fill="both", expand=True, pady=(0, 20))
        self.update_compare_view()

    def refresh_items(self) -> None:
        for child in self.scroll_frame.inner.winfo_children():
            child.destroy()
        self._edit_vars = {}
        for index, item in enumerate(self.items):
            self._render_item_row(index, item)

    def _render_item_row(self, index: int, item: Item) -> None:
        row = ttk.Frame(self.scroll_frame.inner, padding=8)
        row.pack(fill="x", pady=4)
        counter = ttk.Label(row, text=f"{index + 1}.", width=4)
        counter.pack(side="left")

        if not item.is_editing:
            description = ttk.Label(
                row,
                text=item.description,
                wraplength=280,
            )
            description.pack(side="left", fill="x", expand=True)
            edit_btn = ttk.Button(
                row, text="Edit", command=lambda i=index: self.start_edit(i)
            )
            edit_btn.pack(side="left", padx=5)
            delete_btn = ttk.Button(
                row, text="Delete", command=lambda i=index: self.delete_item(i)
            )
            delete_btn.pack(side="left")
        else:
            var = tk.StringVar(value=item.description)
            self._edit_vars[index] = var
            entry = ttk.Entry(row, textvariable=var)
            entry.pack(side="left", fill="x", expand=True)
            entry.bind("<Return>", lambda event, i=index: self.finish_edit(i))
            self.root.after(0, entry.focus_set)
            done_btn = ttk.Button(
                row, text="Done", command=lambda i=index: self.finish_edit(i)
            )
            done_btn.pack(side="left", padx=5)
            delete_btn = ttk.Button(
                row, text="Delete", command=lambda i=index: self.delete_item(i)
            )
            delete_btn.pack(side="left")

    def create_item(self) -> None:
        text = self.new_item_var.get().strip()
        if not text:
            return
        self.items.append(Item(description=text))
        self.new_item_var.set("")
        self.refresh_items()
        self._update_sort_button()

    def delete_item(self, index: int) -> None:
        del self.items[index]
        self.refresh_items()
        self._update_sort_button()

    def start_edit(self, index: int) -> None:
        for item in self.items:
            item.is_editing = False
        self.items[index].is_editing = True
        self.refresh_items()

    def finish_edit(self, index: int) -> None:
        text = (
            self._edit_vars.get(index).get().strip() if index in self._edit_vars else ""
        )
        if text:
            self.items[index].description = text
            self.items[index].is_editing = False
            self.refresh_items()

    def _update_sort_button(self) -> None:
        state = "normal" if len(self.items) >= 2 else "disabled"
        self.sort_button.configure(state=state)

    def enter_compare_mode(self) -> None:
        if len(self.items) < 2:
            return
        for item in self.items:
            item.is_editing = False
        # Remember original positions so we can show how things move during sorting.
        self._original_index = {id(item): index for index, item in enumerate(self.items)}
        self.sorter.start_sorting(self.items)
        if self.sorter.current_pair() is None and not self.sorter.is_done():
            return
        self.show_compare_view()

    def _select_choice(self, choice: Choice) -> None:
        if self.mode != "compare":
            return
        self.sorter.make_choice(choice)
        self.update_compare_view()

    def update_compare_view(self) -> None:
        pair = self.sorter.current_pair()
        if pair:
            left, right = pair
            self.prompt_label.configure(text="Which one is more important?")
            self.left_button.configure(text=left.description, state="normal")
            self.right_button.configure(text=right.description, state="normal")
            self.results_frame.pack_forget()
            self.results_var.set("")
            self._refresh_state_view()
        elif self.sorter.is_done():
            # Hide the comparison controls and show the final ordered list
            self.prompt_label.pack_forget()
            self.body_frame.pack_forget()
            ordered = self.sorter.finish_sorting(self.items)
            listing = "\n".join(
                f"{index + 1}. {item.description}" for index, item in enumerate(ordered)
            )
            self.results_var.set(listing or "No items to show.")
            if not self.results_frame.winfo_ismapped():
                self.results_frame.pack(fill="both", expand=True)
            # No need for live view once the final order is shown.
        else:
            self.prompt_label.configure(text="There is nothing to compare.")
            self.left_button.configure(text="", state="disabled")
            self.right_button.configure(text="", state="disabled")
            self.results_frame.pack_forget()
            self.results_var.set("")
            self._refresh_state_view()

    def _on_toggle_state_view(self) -> None:
        # Show or hide the legend together with the live ordering.
        if self.show_state_var.get():
            if not self.state_legend_frame.winfo_ismapped():
                self.state_legend_frame.pack(fill="x", pady=(0, 6))
        else:
            self.state_legend_frame.pack_forget()
        self._refresh_state_view()

    def _refresh_state_view(self) -> None:
        """Render the current best-known ordering with movement indicators."""
        # Clear existing rows
        for child in self.state_scroll.inner.winfo_children():
            child.destroy()

        if not self.show_state_var.get():
            return

        # Inspect sorter internals to highlight the current item and search window.
        current_id: int | None = None
        lo: int | None = None
        hi: int | None = None
        sorted_len: int = 0
        if isinstance(self.sorter.state, CompareState):
            state = self.sorter.state
            lo = state.lo
            hi = state.hi
            sorted_len = len(state.sorted)
            if state.unsorted:
                current_id = id(state.unsorted[-1])

        snapshot = self.sorter.snapshot_ordering(self.items)
        for index, item in enumerate(snapshot):
            row = ttk.Frame(self.state_scroll.inner, padding=2)
            row.pack(fill="x", pady=1)

            original_index = self._original_index.get(id(item))
            indicator = ""
            color = None
            if original_index is not None:
                delta = original_index - index
                if delta > 0:
                    indicator = "↑"
                    color = "#1a7f37"  # moved up (from below)
                elif delta < 0:
                    indicator = "↓"
                    color = "#b42318"  # moved down (from above)
                else:
                    indicator = "•"
                    color = "#6c6c6c"

            # Visualize the binary-search step:
            # - "●" marks the current item being inserted.
            # - "□" marks the active search window in the sorted prefix.
            status_symbol = ""
            if current_id is not None and id(item) == current_id:
                status_symbol = "●"
            elif (
                lo is not None
                and hi is not None
                and index < sorted_len
                and lo <= index < hi
            ):
                status_symbol = "□"

            if status_symbol:
                status_label = ttk.Label(row, text=status_symbol, width=2)
                status_label.pack(side="left")

            arrow_label = ttk.Label(row, text=indicator, width=2)
            if color is not None:
                try:
                    arrow_label.configure(foreground=color)
                except tk.TclError:
                    # Some themes may not support custom foreground; ignore.
                    pass
            arrow_label.pack(side="left")

            text_label = ttk.Label(
                row,
                text=f"{index + 1}. {item.description}",
                wraplength=160,
                anchor="w",
                justify="left",
            )
            text_label.pack(side="left", fill="x", expand=True)

    def return_to_list(self) -> None:
        if self.mode == "compare":
            ordered = self.sorter.finish_sorting(self.items)
            for item in ordered:
                item.is_editing = False
            self.items = ordered
        self.show_list_view()
        self.refresh_items()
        self._update_sort_button()

    def run(self) -> None:
        self.root.mainloop()


def run_app() -> None:
    app = PrioritySorterApp()
    app.run()
