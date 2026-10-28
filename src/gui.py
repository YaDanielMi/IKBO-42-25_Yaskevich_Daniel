"""Tkinter front end: a terminal-like window for the shell emulator."""
import tkinter as tk

from runner import run_line

BG_COLOR = "#1e1e1e"
FG_COLOR = "#d4d4d4"
PROMPT_COLOR = "#6a9955"
ERROR_COLOR = "#f48771"
DEBUG_COLOR = "#808080"
FONT = "TkFixedFont"
WINDOW_SIZE = "900x560"
LOG_END = "end"


class TerminalWindow:
    """Read-only log of the dialog plus an entry for new commands."""

    def __init__(self, shell, title):
        self.shell = shell
        self.history = []
        self.history_pos = 0
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(WINDOW_SIZE)
        self._build_widgets()
        self._bind_keys()

    def _build_widgets(self):
        """Create the log, the scrollbar, the prompt and the entry."""
        bottom = tk.Frame(self.root, bg=BG_COLOR)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)
        self.prompt_label = tk.Label(
            bottom, font=FONT, bg=BG_COLOR, fg=PROMPT_COLOR
        )
        self.prompt_label.pack(side=tk.LEFT)
        self.entry = tk.Entry(
            bottom, font=FONT, bg=BG_COLOR, fg=FG_COLOR,
            insertbackground=FG_COLOR, relief=tk.FLAT,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scroll = tk.Scrollbar(self.root)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log = tk.Text(
            self.root, font=FONT, bg=BG_COLOR, fg=FG_COLOR,
            state=tk.DISABLED, wrap=tk.WORD, yscrollcommand=scroll.set,
        )
        scroll.configure(command=self.log.yview)
        self.log.pack(fill=tk.BOTH, expand=True)
        self.log.tag_configure("prompt", foreground=PROMPT_COLOR)
        self.log.tag_configure("error", foreground=ERROR_COLOR)
        self.log.tag_configure("debug", foreground=DEBUG_COLOR)

    def _bind_keys(self):
        """Bind Enter, Up and Down in the command entry."""
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Up>", self._on_history_up)
        self.entry.bind("<Down>", self._on_history_down)
        self.entry.focus_set()

    def _append(self, text, tag=""):
        """Append text to the read-only log and scroll to its end."""
        self.log.configure(state=tk.NORMAL)
        self.log.insert(LOG_END, text, tag)
        self.log.configure(state=tk.DISABLED)
        self.log.see(LOG_END)

    def echo(self, prompt, line):
        """Show a prompt followed by the typed command line."""
        self._append(prompt, "prompt")
        self._append(line + "\n")

    def out(self, text):
        """Show standard output of a command."""
        self._append(text + "\n")

    def err(self, text):
        """Show standard error of a command."""
        self._append(text + "\n", "error")

    def debug(self, lines):
        """Show service lines (debug output, notices)."""
        for line in lines:
            self._append(line + "\n", "debug")

    def refresh_prompt(self):
        """Update the prompt label from the shell state."""
        self.prompt_label.configure(text=self.shell.prompt())

    def _on_enter(self, event):
        """Run the command typed into the entry."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        if line.strip():
            self.history.append(line)
        self.history_pos = len(self.history)
        result = run_line(self.shell, line, self)
        self.refresh_prompt()
        if result.exit_requested:
            self.root.destroy()

    def _show_history(self):
        """Put the history item under the cursor into the entry."""
        self.entry.delete(0, tk.END)
        if self.history_pos < len(self.history):
            self.entry.insert(0, self.history[self.history_pos])

    def _on_history_up(self, event):
        """Show the previous command from the history."""
        if self.history_pos > 0:
            self.history_pos -= 1
            self._show_history()

    def _on_history_down(self, event):
        """Show the next command from the history."""
        if self.history_pos < len(self.history):
            self.history_pos += 1
            self._show_history()

    def start(self):
        """Show the welcome text and enter the main loop."""
        self.debug(["Эмулятор оболочки. Команды: ls, cd, exit."])
        self.refresh_prompt()
        self.root.mainloop()
