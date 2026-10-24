"""Colours, fonts and ttk styles for the desktop interface."""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk

__all__ = ["FONT_FAMILY", "PALETTE", "apply_theme"]

PALETTE = {
    "bg": "#0f172a",
    "surface": "#1e293b",
    "surface_alt": "#334155",
    "text": "#f8fafc",
    "muted": "#94a3b8",
    "primary": "#6366f1",
    "primary_hover": "#818cf8",
    "success": "#22c55e",
    "danger": "#ef4444",
    "warning": "#f59e0b",
}

if sys.platform == "win32":
    FONT_FAMILY = "Segoe UI"
elif sys.platform == "darwin":
    FONT_FAMILY = "Helvetica Neue"
else:
    FONT_FAMILY = "DejaVu Sans"


def apply_theme(root: tk.Misc) -> None:
    """Configure a dark, flat ttk theme on ``root``."""
    p = PALETTE
    style = ttk.Style(root)
    style.theme_use("clam")  # the only built-in theme that honours custom colours everywhere
    root.configure(background=p["bg"])

    style.configure(".", background=p["bg"], foreground=p["text"], font=(FONT_FAMILY, 11))
    style.configure("App.TFrame", background=p["bg"])
    style.configure("Card.TFrame", background=p["surface"])

    style.configure("Title.TLabel", font=(FONT_FAMILY, 30, "bold"), background=p["bg"])
    style.configure("Heading.TLabel", font=(FONT_FAMILY, 20, "bold"), background=p["bg"])
    style.configure("Body.TLabel", font=(FONT_FAMILY, 12), background=p["bg"])
    style.configure("Muted.TLabel", foreground=p["muted"], background=p["bg"])
    style.configure("Question.TLabel", font=(FONT_FAMILY, 38, "bold"), background=p["bg"])
    style.configure("Score.TLabel", font=(FONT_FAMILY, 48, "bold"), background=p["bg"])
    style.configure("Success.TLabel", foreground=p["success"], background=p["bg"])
    style.configure("Danger.TLabel", foreground=p["danger"], background=p["bg"])
    style.configure("Warning.TLabel", foreground=p["warning"], background=p["bg"])

    for name, base, hover in (
        ("Primary", p["primary"], p["primary_hover"]),
        ("Secondary", p["surface_alt"], "#475569"),
        ("Danger", "#b91c1c", p["danger"]),
        ("Key", p["surface"], p["surface_alt"]),
        ("Accent", p["primary"], p["primary_hover"]),
    ):
        style.configure(
            f"{name}.TButton",
            background=base,
            foreground=p["text"],
            padding=(16, 10),
            borderwidth=0,
            focusthickness=0,
            relief="flat",
            font=(FONT_FAMILY, 11, "bold"),
        )
        style.map(
            f"{name}.TButton",
            background=[("pressed", hover), ("active", hover)],
        )
    style.configure("Key.TButton", font=(FONT_FAMILY, 16, "bold"), padding=(0, 12))

    style.configure(
        "TEntry",
        fieldbackground=p["surface"],
        foreground=p["text"],
        insertcolor=p["text"],
        bordercolor=p["surface_alt"],
        lightcolor=p["surface_alt"],
        darkcolor=p["surface_alt"],
        padding=8,
    )
    style.map("TEntry", bordercolor=[("focus", p["primary"])])
    style.configure(
        "TCombobox",
        fieldbackground=p["surface"],
        background=p["surface_alt"],
        foreground=p["text"],
        arrowcolor=p["text"],
        padding=6,
    )
    style.map("TCombobox", fieldbackground=[("readonly", p["surface"])])
    root.option_add("*TCombobox*Listbox.background", p["surface"])
    root.option_add("*TCombobox*Listbox.foreground", p["text"])

    style.configure(
        "TRadiobutton", background=p["bg"], foreground=p["text"], font=(FONT_FAMILY, 12)
    )
    style.map("TRadiobutton", background=[("active", p["bg"])])

    style.configure(
        "Timer.Horizontal.TProgressbar",
        troughcolor=p["surface"],
        background=p["primary"],
        bordercolor=p["bg"],
        lightcolor=p["primary"],
        darkcolor=p["primary"],
        thickness=10,
    )
