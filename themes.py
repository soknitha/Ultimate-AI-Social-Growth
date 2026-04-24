"""
GrowthOS AI v2.0 — Theme Definitions
=====================================
10 hand-crafted, modern themes. Each theme defines 10 color roles:

  DARK_BG  — main window background
  SIDEBAR  — left navigation panel
  SURFACE  — cards, inputs, tables
  ACCENT   — primary highlight / interactive color
  SUCCESS  — positive status, green channel
  WARNING  — alerts, amber channel
  ERROR    — errors, danger (F38BA8 fallback if not present)
  TEXT     — primary body text
  SUBTEXT  — muted / secondary text
  BORDER   — widget borders, separators
  HOVER    — hover/selection highlight

Usage:
    from themes import THEMES, THEME_NAMES, DEFAULT_THEME
    t = THEMES["Tokyo Night"]
"""

from typing import Dict

THEME = Dict[str, str]

# ─────────────────────────────────────────────────────────────────────────────
# 1. Catppuccin Mocha  — deep purple, soft pastels (DEFAULT)
# ─────────────────────────────────────────────────────────────────────────────
_CATPPUCCIN_MOCHA: THEME = {
    "DARK_BG":  "#1E1E2E",
    "SIDEBAR":  "#181825",
    "SURFACE":  "#313244",
    "ACCENT":   "#89B4FA",   # Lavender blue
    "SUCCESS":  "#A6E3A1",   # Green
    "WARNING":  "#FAB387",   # Peach
    "ERROR":    "#F38BA8",   # Red
    "TEXT":     "#CDD6F4",
    "SUBTEXT":  "#6C7086",
    "BORDER":   "#45475A",
    "HOVER":    "#2D2D3B",
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. Midnight Pro  — ultra-dark with electric cyan neon
# ─────────────────────────────────────────────────────────────────────────────
_MIDNIGHT_PRO: THEME = {
    "DARK_BG":  "#0D0D14",
    "SIDEBAR":  "#080810",
    "SURFACE":  "#161624",
    "ACCENT":   "#00D4FF",   # Electric cyan
    "SUCCESS":  "#00FF9B",   # Neon mint
    "WARNING":  "#FFB800",   # Amber
    "ERROR":    "#FF4757",   # Coral red
    "TEXT":     "#E4E8F0",
    "SUBTEXT":  "#4A5568",
    "BORDER":   "#1E1E30",
    "HOVER":    "#12121F",
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. Nord Arctic  — Scandinavian cool blues and grey-greens
# ─────────────────────────────────────────────────────────────────────────────
_NORD_ARCTIC: THEME = {
    "DARK_BG":  "#2E3440",
    "SIDEBAR":  "#242831",
    "SURFACE":  "#3B4252",
    "ACCENT":   "#88C0D0",   # Frost blue
    "SUCCESS":  "#A3BE8C",   # Sage green
    "WARNING":  "#EBCB8B",   # Sand yellow
    "ERROR":    "#BF616A",   # Aurora red
    "TEXT":     "#ECEFF4",
    "SUBTEXT":  "#7B88A1",
    "BORDER":   "#4C566A",
    "HOVER":    "#434C5E",
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. Tokyo Night  — deep ink with vivid purple-blue neons
# ─────────────────────────────────────────────────────────────────────────────
_TOKYO_NIGHT: THEME = {
    "DARK_BG":  "#1A1B26",
    "SIDEBAR":  "#13141F",
    "SURFACE":  "#24283B",
    "ACCENT":   "#7AA2F7",   # Periwinkle
    "SUCCESS":  "#9ECE6A",   # Leaf green
    "WARNING":  "#E0AF68",   # Gold
    "ERROR":    "#F7768E",   # Rose
    "TEXT":     "#C0CAF5",
    "SUBTEXT":  "#565F89",
    "BORDER":   "#3B4261",
    "HOVER":    "#1F2335",
}

# ─────────────────────────────────────────────────────────────────────────────
# 5. Dracula  — iconic dark purple with vibrant contrast
# ─────────────────────────────────────────────────────────────────────────────
_DRACULA: THEME = {
    "DARK_BG":  "#282A36",
    "SIDEBAR":  "#1E1F29",
    "SURFACE":  "#373848",
    "ACCENT":   "#BD93F9",   # Purple
    "SUCCESS":  "#50FA7B",   # Bright green
    "WARNING":  "#FFB86C",   # Orange
    "ERROR":    "#FF5555",   # Red
    "TEXT":     "#F8F8F2",
    "SUBTEXT":  "#6272A4",
    "BORDER":   "#44475A",
    "HOVER":    "#2F3140",
}

# ─────────────────────────────────────────────────────────────────────────────
# 6. Solarized Dark  — warm dark tones, timeless readability
# ─────────────────────────────────────────────────────────────────────────────
_SOLARIZED_DARK: THEME = {
    "DARK_BG":  "#002B36",
    "SIDEBAR":  "#00212B",
    "SURFACE":  "#073642",
    "ACCENT":   "#268BD2",   # Blue
    "SUCCESS":  "#859900",   # Olive green
    "WARNING":  "#B58900",   # Solar yellow
    "ERROR":    "#DC322F",   # Red
    "TEXT":     "#FDF6E3",   # Cream
    "SUBTEXT":  "#657B83",
    "BORDER":   "#124552",
    "HOVER":    "#053642",
}

# ─────────────────────────────────────────────────────────────────────────────
# 7. One Dark Pro  — Atom editor's beloved dark palette
# ─────────────────────────────────────────────────────────────────────────────
_ONE_DARK_PRO: THEME = {
    "DARK_BG":  "#282C34",
    "SIDEBAR":  "#1E2127",
    "SURFACE":  "#353A45",
    "ACCENT":   "#61AFEF",   # Sky blue
    "SUCCESS":  "#98C379",   # Green
    "WARNING":  "#E5C07B",   # Yellow
    "ERROR":    "#E06C75",   # Dusty red
    "TEXT":     "#ABB2BF",
    "SUBTEXT":  "#5C6370",
    "BORDER":   "#3E4451",
    "HOVER":    "#2C313A",
}

# ─────────────────────────────────────────────────────────────────────────────
# 8. Material Ocean  — Deep space with rich Material Design accents
# ─────────────────────────────────────────────────────────────────────────────
_MATERIAL_OCEAN: THEME = {
    "DARK_BG":  "#0F111A",
    "SIDEBAR":  "#090B10",
    "SURFACE":  "#1A1C25",
    "ACCENT":   "#82AAFF",   # Cornflower blue
    "SUCCESS":  "#C3E88D",   # Lime
    "WARNING":  "#FFCB6B",   # Mango
    "ERROR":    "#FF5370",   # Coral
    "TEXT":     "#EEFFFF",   # Ice white
    "SUBTEXT":  "#546E7A",
    "BORDER":   "#222636",
    "HOVER":    "#161821",
}

# ─────────────────────────────────────────────────────────────────────────────
# 9. GitHub Dark  — GitHub's polished dark mode
# ─────────────────────────────────────────────────────────────────────────────
_GITHUB_DARK: THEME = {
    "DARK_BG":  "#0D1117",
    "SIDEBAR":  "#090D12",
    "SURFACE":  "#161B22",
    "ACCENT":   "#58A6FF",   # GitHub blue
    "SUCCESS":  "#3FB950",   # Merge green
    "WARNING":  "#D29922",   # Alert amber
    "ERROR":    "#F85149",   # Danger red
    "TEXT":     "#C9D1D9",
    "SUBTEXT":  "#484F58",
    "BORDER":   "#21262D",
    "HOVER":    "#151B23",
}

# ─────────────────────────────────────────────────────────────────────────────
# 10. Aurora Borealis  — midnight black with glowing teal aurora
# ─────────────────────────────────────────────────────────────────────────────
_AURORA_BOREALIS: THEME = {
    "DARK_BG":  "#0A0E14",
    "SIDEBAR":  "#060A0F",
    "SURFACE":  "#131922",
    "ACCENT":   "#00D9A3",   # Aurora teal
    "SUCCESS":  "#57E28A",   # Bioluminescent green
    "WARNING":  "#FFAD33",   # Amber glow
    "ERROR":    "#FF6B6B",   # Warm red
    "TEXT":     "#D8E6F3",
    "SUBTEXT":  "#4A6375",
    "BORDER":   "#1A2735",
    "HOVER":    "#0E1820",
}

# ─────────────────────────────────────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────────────────────────────────────
THEMES: Dict[str, THEME] = {
    "Catppuccin Mocha":  _CATPPUCCIN_MOCHA,
    "Midnight Pro":      _MIDNIGHT_PRO,
    "Nord Arctic":       _NORD_ARCTIC,
    "Tokyo Night":       _TOKYO_NIGHT,
    "Dracula":           _DRACULA,
    "Solarized Dark":    _SOLARIZED_DARK,
    "One Dark Pro":      _ONE_DARK_PRO,
    "Material Ocean":    _MATERIAL_OCEAN,
    "GitHub Dark":       _GITHUB_DARK,
    "Aurora Borealis":   _AURORA_BOREALIS,
}

THEME_NAMES:  list[str] = list(THEMES.keys())
DEFAULT_THEME: str      = "Catppuccin Mocha"
